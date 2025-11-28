// frontend/assets/js/progress-tracker.js
import { apiRequest } from "./api.js";

const API_BASE = "http://127.0.0.1:8000";

let tasksCache = [];
let selectedTaskId = null;

document.addEventListener("DOMContentLoaded", () => {
  loadTasks();

  // match HTML form id = "taskUploadForm"
  const uploadForm = document.getElementById("taskUploadForm");
  if (uploadForm) {
    uploadForm.addEventListener("submit", onSubmitTask);
  }
});

async function loadTasks() {
  const tbody = document.getElementById("tasksBody");
  const liveTitle = document.getElementById("liveTaskTitle");
  const liveMeta = document.getElementById("liveTaskMeta");

  if (!tbody) return;

  tbody.innerHTML =
    '<tr><td colspan="6" style="color:var(--text-muted);">Loading tasks...</td></tr>';

  try {
    const tasks = await apiRequest("/progress/tasks");
    tasksCache = tasks;

    if (!tasks.length) {
      tbody.innerHTML =
        '<tr><td colspan="6" style="color:var(--text-muted);">No tasks assigned yet. Once an admin assigns tasks for your approved internships, they will appear here.</td></tr>';
      if (liveTitle)
        liveTitle.textContent = "No active task. Waiting for assignments.";
      if (liveMeta)
        liveMeta.textContent =
          "Check back later or contact your mentor/admin about tasks.";
      return;
    }

    tbody.innerHTML = "";
    tasks.forEach((t, index) => {
      const tr = document.createElement("tr");
      tr.style.cursor = "pointer";

      const statusColor = getStatusColor(t);

      tr.innerHTML = `
        <td>${index + 1}</td>
        <td>${t.title}</td>
        <td>${t.internship_title}</td>
        <td>${t.due_date}</td>
        <td>
          <span style="color:${statusColor}; font-size:0.8rem;">
            ${t.status_label}
          </span>
        </td>
        <td>${
          t.submitted_at
            ? new Date(t.submitted_at).toLocaleDateString()
            : "-"
        }</td>
      `;

      tr.addEventListener("click", () => {
        selectTask(t);
      });

      tbody.appendChild(tr);
    });

    // AUTO-select live task = closest upcoming due date (rule C1)
    const live = pickLiveTask(tasks);
    if (live) {
      selectTask(live);
    } else {
      // Fallback if all overdue: just select first row
      selectTask(tasks[0]);
    }
  } catch (err) {
    console.error("Failed to load tasks", err);
    tbody.innerHTML =
      '<tr><td colspan="6" style="color:red;">Failed to load tasks.</td></tr>';
    if (liveTitle)
      liveTitle.textContent = "Error loading tasks from the server.";
    if (liveMeta)
      liveMeta.textContent =
        "Please refresh the page or try again in a few minutes.";
  }
}

function getStatusColor(task) {
  if (task.status === "on_time") return "#4ade80"; // green
  if (task.status === "late") return "#facc15"; // yellow

  // not_submitted
  const due = new Date(task.due_date);
  const now = new Date();
  if (due < new Date(now.getFullYear(), now.getMonth(), now.getDate())) {
    // overdue
    return "#f97373"; // red-ish
  }
  return "#e5e7eb"; // neutral
}

function pickLiveTask(tasks) {
  const today = new Date();
  const todayDateOnly = new Date(
    today.getFullYear(),
    today.getMonth(),
    today.getDate()
  );

  // Filter only tasks whose due_date >= today and not submitted on time yet
  const upcoming = tasks.filter((t) => {
    const due = new Date(t.due_date);
    const dueDateOnly = new Date(
      due.getFullYear(),
      due.getMonth(),
      due.getDate()
    );
    return dueDateOnly >= todayDateOnly && t.status !== "on_time";
  });

  if (!upcoming.length) return null;

  // Sort by nearest due date
  upcoming.sort(
    (a, b) => new Date(a.due_date).getTime() - new Date(b.due_date).getTime()
  );
  return upcoming[0];
}

function selectTask(task) {
  selectedTaskId = task.task_id;

  const liveTitle = document.getElementById("liveTaskTitle");
  const liveMeta = document.getElementById("liveTaskMeta");
  const uploadSection = document.getElementById("uploadSection");
  const label = document.getElementById("selectedTaskLabel");

  if (liveTitle) {
    liveTitle.textContent = task.title;
  }
  if (liveMeta) {
    liveMeta.textContent = `Internship: ${task.internship_title} • Due: ${task.due_date} • Status: ${task.status_label}`;
  }

  if (label) {
    label.textContent = `${task.title} (due ${task.due_date})`;
  }

  if (uploadSection) {
    uploadSection.style.display = "block";
  }
}

async function onSubmitTask(e) {
  e.preventDefault();

  if (!selectedTaskId) {
    alert("Please select a task from the list first.");
    return;
  }

  const fileInput = document.getElementById("deliverableFile");
  if (!fileInput || !fileInput.files.length) {
    alert("Choose a file to upload.");
    return;
  }

  const token = localStorage.getItem("access_token");
  if (!token) {
    window.location.href = "./login.html";
    return;
  }

  const formData = new FormData();
  formData.append("file", fileInput.files[0]); // Allow ALL file types

  try {
    const res = await fetch(
      `${API_BASE}/progress/tasks/${selectedTaskId}/submit`,
      {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
        },
        body: formData,
      }
    );

    if (!res.ok) {
      throw new Error("Upload failed");
    }

    const data = await res.json();
    alert(`Submitted (${data.status})`);
    fileInput.value = "";
    loadTasks();
  } catch (err) {
    console.error("Task submit failed", err);
    alert("Failed to submit task.");
  }
}

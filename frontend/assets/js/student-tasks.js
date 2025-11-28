// static/js/student-tasks.js
import { apiRequest } from "./api.js";

document.addEventListener("DOMContentLoaded", () => {
  loadMyTasks();
});

// ================ LOAD TASKS ===================

async function loadMyTasks() {
  const tbody = document.getElementById("studentTasksBody");
  if (!tbody) return;

  tbody.innerHTML =
    '<tr><td colspan="5" style="color:var(--text-muted);">Loading...</td></tr>';

  try {
    const tasks = await apiRequest("/students/me/tasks");

    if (!tasks.length) {
      tbody.innerHTML =
        '<tr><td colspan="5" style="color:var(--text-muted);">No tasks yet. Once an admin assigns work for your approved internships, it will appear here.</td></tr>';
      return;
    }

    tbody.innerHTML = "";
    tasks.forEach((t) => {
      const tr = document.createElement("tr");

      let statusLabel = "Not submitted";
      if (t.status === "submitted") statusLabel = "Submitted";

      tr.innerHTML = `
        <td>${t.title}</td>
        <td>${t.internship_title || "-"}</td>
        <td>${t.due_date}</td>
        <td>${statusLabel}</td>
        <td>
          <button class="btn btn-ghost" data-view="${t.task_id}">View</button>
          <button class="btn btn-primary" data-submit="${t.task_id}">
            ${t.status === "submitted" ? "Resubmit" : "Submit"}
          </button>
        </td>
      `;

      tbody.appendChild(tr);
    });

    bindTaskButtons();
  } catch (err) {
    console.error("Failed to load tasks", err);
    tbody.innerHTML =
      '<tr><td colspan="5" style="color:red;">Failed to load tasks.</td></tr>';
  }
}

// ================ BUTTON ACTIONS ===================

function bindTaskButtons() {
  // Simple "view" shows description + last submission + feedback
  document.querySelectorAll("[data-view]").forEach((btn) => {
    btn.onclick = () => {
      const taskId = Number(btn.getAttribute("data-view"));
      showTaskDetails(taskId);
    };
  });

  document.querySelectorAll("[data-submit]").forEach((btn) => {
    btn.onclick = () => {
      const taskId = Number(btn.getAttribute("data-submit"));
      submitTask(taskId);
    };
  });
}

async function showTaskDetails(taskId) {
  // We already have all data in table; fetch full list again, pick this task
  const tasks = await apiRequest("/students/me/tasks");
  const t = tasks.find((x) => x.task_id === taskId);
  if (!t) return;

  const info = `
Task: ${t.title}
Internship: ${t.internship_title || "-"}

Description:
${t.description || "No description provided."}

Latest submission:
${t.raw_value || "No submission yet."}

Feedback:
${t.feedback || "No feedback yet."}
  `;

  alert(info);
}

async function submitTask(taskId) {
  const content = prompt(
    "Paste your solution / notes / URL here (for files, you can paste a drive link):",
  );
  if (content === null || !content.trim()) return;

  try {
    await apiRequest(`/students/tasks/${taskId}/submit`, {
      method: "POST",
      body: JSON.stringify({ content }),
    });
    alert("Submission saved.");
    loadMyTasks();
  } catch (err) {
    console.error("Failed to submit task", err);
    alert("Failed to submit task.");
  }
}

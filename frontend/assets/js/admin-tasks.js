// static/js/admin-tasks.js
import { apiRequest } from "./api.js";

let studentsCache = [];
let internshipsCache = [];
let selectedStudentId = null;

document.addEventListener("DOMContentLoaded", () => {
  loadAcceptedUsers();
  loadInternships();
  wireTaskForm();
  wireStudentChange();
});

// ================== LOAD APPROVED STUDENTS ==================

async function loadAcceptedUsers() {
  try {
    const users = await apiRequest("/admin/users/accepted");
    studentsCache = users || [];

    const select = document.getElementById("taskStudent");
    if (!select) return;
    select.innerHTML = "";

    if (!users.length) {
      const opt = document.createElement("option");
      opt.textContent = "No accepted users yet";
      opt.value = "";
      select.appendChild(opt);
      select.disabled = true;
      return;
    }

    users.forEach((u) => {
      const opt = document.createElement("option");
      opt.value = u.student_id;
      opt.textContent = `${u.name} – ${u.company}`;
      select.appendChild(opt);
    });

    // default selection
    selectedStudentId = users[0].student_id;
    select.value = String(selectedStudentId);
    loadStudentTasks();
  } catch (err) {
    console.error("Failed to load accepted users", err);
  }
}

// ================== LOAD INTERNSHIPS ==================

async function loadInternships() {
  try {
    const ints = await apiRequest("/admin/internships");
    internshipsCache = ints || [];

    const select = document.getElementById("taskInternship");
    if (!select) return;
    select.innerHTML = "";

    if (!ints.length) {
      const opt = document.createElement("option");
      opt.textContent = "No internships yet";
      opt.value = "";
      select.appendChild(opt);
      select.disabled = true;
      return;
    }

    ints.forEach((i) => {
      const opt = document.createElement("option");
      opt.value = i.id;
      opt.textContent = `${i.title} – ${i.company}`;
      select.appendChild(opt);
    });
  } catch (err) {
    console.error("Failed to load internships", err);
  }
}

// ================== STUDENT DROPDOWN CHANGE ==================

function wireStudentChange() {
  const select = document.getElementById("taskStudent");
  if (!select) return;

  select.addEventListener("change", () => {
    selectedStudentId = Number(select.value) || null;
    loadStudentTasks();
  });
}

// ================== TASK CREATION FORM ==================

function wireTaskForm() {
  const form = document.getElementById("taskForm");
  if (!form) return;

  form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const studentId = Number(
      document.getElementById("taskStudent").value || "0",
    );
    const internshipId = Number(
      document.getElementById("taskInternship").value || "0",
    );
    const title = document.getElementById("taskTitle").value.trim();
    const description = document.getElementById("taskDescription").value.trim();
    const assignedDate = document.getElementById("taskAssignedDate").value;
    const dueDate = document.getElementById("taskDueDate").value;

    if (!studentId || !internshipId || !title || !dueDate) {
      alert("Student, internship, title and due date are required.");
      return;
    }

    const payload = {
      student_id: studentId,
      internship_id: internshipId,
      title,
      description,
      assigned_date: assignedDate || null,
      due_date: dueDate,
    };

    try {
      await apiRequest("/admin/tasks", {
        method: "POST",
        body: JSON.stringify(payload),
      });
      alert("Task created for internship.");
      form.reset();
      // keep student selection; just reload tasks view
      loadStudentTasks();
    } catch (err) {
      console.error(err);
      alert(err.message || "Failed to create task.");
    }
  });
}

// ================== LOAD TASKS FOR SELECTED STUDENT ==================

async function loadStudentTasks() {
  const tbody = document.getElementById("tasksTableBody");
  if (!tbody) return;

  if (!selectedStudentId) {
    tbody.innerHTML =
      '<tr><td colspan="5" style="color:var(--text-muted);">Select a student on the left.</td></tr>';
    return;
  }

  tbody.innerHTML =
    '<tr><td colspan="5" style="color:var(--text-muted);">Loading...</td></tr>';

  try {
    const tasks = await apiRequest(
      `/admin/students/${selectedStudentId}/tasks`,
    );

    if (!tasks.length) {
      tbody.innerHTML =
        '<tr><td colspan="5" style="color:var(--text-muted);">No tasks yet for this student.</td></tr>';
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
          ${
            t.submission_id
              ? `<button class="btn btn-ghost" data-review="${t.submission_id}">Review</button>`
              : `<span style="color:var(--text-muted);font-size:0.8rem;">No submission</span>`
          }
        </td>
      `;

      tbody.appendChild(tr);
    });

    bindReviewButtons();
  } catch (err) {
    console.error("Failed to load student tasks", err);
    tbody.innerHTML =
      '<tr><td colspan="5" style="color:red;">Failed to load tasks</td></tr>';
  }
}

// ================== REVIEW FEEDBACK ==================

function bindReviewButtons() {
  document.querySelectorAll("[data-review]").forEach((btn) => {
    btn.onclick = async () => {
      const id = btn.getAttribute("data-review");
      const feedback = prompt("Enter feedback / comments for this submission:");
      if (feedback === null) return;

      try {
        await apiRequest(`/admin/submissions/${id}/review`, {
          method: "PATCH",
          body: JSON.stringify({ feedback }),
        });
        alert("Feedback saved.");
        loadStudentTasks();
      } catch (err) {
        console.error(err);
        alert("Failed to save feedback.");
      }
    };
  });
}

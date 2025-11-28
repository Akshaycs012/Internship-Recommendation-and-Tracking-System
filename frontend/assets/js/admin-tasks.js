// frontend/assets/js/admin-tasks.js
import { apiRequest } from "./api.js";

document.addEventListener("DOMContentLoaded", () => {
  loadAcceptedUsers();
  loadInternships();
  wireTaskForm();
});

let studentsCache = [];
let internshipsCache = [];

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
      opt.value = u.user_id;
      opt.textContent = `${u.name} – ${u.company}`;
      select.appendChild(opt);
    });
  } catch (err) {
    console.error("Failed to load accepted users", err);
  }
}

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

    const noLinkOpt = document.createElement("option");
    noLinkOpt.value = "";
    noLinkOpt.textContent = "General learning task (not specific to one internship)";
    select.appendChild(noLinkOpt);

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

function wireTaskForm() {
  const form = document.getElementById("taskForm");
  if (!form) return;

  form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const studentId = document.getElementById("taskStudent").value;
    const internshipId = document.getElementById("taskInternship").value || null;
    const title = document.getElementById("taskTitle").value;
    const description = document.getElementById("taskDescription").value;
    const assignedDate = document.getElementById("taskAssignedDate").value;
    const dueDate = document.getElementById("taskDueDate").value;

    if (!studentId || !title || !dueDate) {
      alert("Student, title, and due date are required.");
      return;
    }

    const payload = {
      student_id: Number(studentId),
      internship_id: internshipId ? Number(internshipId) : null,
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
      alert("Task created for student.");
      form.reset();
    } catch (err) {
      alert(err.message || "Failed to create task.");
    }
  });
}

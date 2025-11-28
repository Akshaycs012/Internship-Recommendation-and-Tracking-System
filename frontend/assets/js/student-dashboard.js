// frontend/assets/js/student-dashboard.js
import { apiRequest } from "./api.js";

document.addEventListener("DOMContentLoaded", () => {
  loadStudentSummary();
});

async function loadStudentSummary() {
  // match IDs used in student-dashboard.html
  const appsEl = document.getElementById("count-apps");
  const accEl = document.getElementById("count-accepted");
  const pendEl = document.getElementById("count-pending");
  const updatesEl = document.getElementById("recent-list");

  try {
    const data = await apiRequest("/students/me/summary");

    if (appsEl) appsEl.textContent = data.applications ?? 0;
    if (accEl) accEl.textContent = data.accepted ?? 0;
    if (pendEl) pendEl.textContent = data.pending ?? 0;

    if (updatesEl) {
      updatesEl.innerHTML = "";

      const items = Array.isArray(data.recent_updates)
        ? data.recent_updates
        : [];

      if (!items.length) {
        updatesEl.textContent = "No recent activity yet.";
        return;
      }

      items.forEach((msg) => {
        const line = document.createElement("div");
        line.textContent = `• ${msg}`;
        updatesEl.appendChild(line);
      });
    }
  } catch (err) {
    console.error("Failed to load student summary", err);
    if (updatesEl) {
      updatesEl.innerHTML = "";
      updatesEl.textContent = "Failed to load updates.";
    }
  }
}

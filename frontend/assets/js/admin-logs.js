// frontend/assets/js/admin-logs.js
import { apiRequest } from "./api.js";

document.addEventListener("DOMContentLoaded", () => {
  loadLogs();
});

async function loadLogs() {
  const tbody = document.getElementById("logsBody");
  tbody.innerHTML = "";

  try {
    const logs = await apiRequest("/admin/logs");

    if (!logs.length) {
      const row = document.createElement("tr");
      row.innerHTML =
        '<td colspan="5" style="color: var(--text-muted);">No logs yet</td>';
      tbody.appendChild(row);
      return;
    }

    logs.forEach((log) => {
      const row = document.createElement("tr");
      row.innerHTML = `
        <td>${log.type}</td>
        <td>${log.student_name}</td>
        <td>${log.internship_title}</td>
        <td>${log.company}</td>
        <td>${log.status}</td>
      `;
      tbody.appendChild(row);
    });
  } catch (err) {
    console.error("Failed to load logs", err);
  }
}

import { apiRequest } from "./api.js";

document.addEventListener("DOMContentLoaded", loadLogs);

async function loadLogs(){
    const list = document.getElementById("logsList");
    list.innerHTML = "";

    const logs = await apiRequest("/admin/logs");

    if(!logs.length){
        list.innerHTML = "<p>No history yet...</p>";
        return;
    }

    logs.forEach(l=>{
        const li=document.createElement("li");
        li.textContent = `${l.event} — ${l.time}`;
        list.appendChild(li);
    });
}

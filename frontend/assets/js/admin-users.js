// frontend/assets/js/admin-users.js
import { apiRequest } from "./api.js";

document.addEventListener("DOMContentLoaded", () => {
  loadAcceptedUsers();
});

async function loadAcceptedUsers(){
    const tbody = document.getElementById("acceptedUsersBody");
    tbody.innerHTML = "Loading...";

    const users = await apiRequest("/admin/users/accepted");
    tbody.innerHTML = "";

    users.forEach(u=>{
        tbody.innerHTML += `
        <tr>
            <td>${u.name}</td>
            <td>${u.internship}</td>
            <td>${u.company}</td>
            <td>${u.skills}</td>
        </tr>`;
    });
}


async function loadUserDetails(userId) {
  const panel = document.getElementById("userDetailsContent");
  panel.textContent = "Loading...";

  try {
    const d = await apiRequest(`/admin/users/${userId}`);

    panel.innerHTML = `
      <div style="margin-bottom: 0.5rem;">
        <strong>${d.name}</strong><br/>
        <span style="color: var(--text-muted); font-size: 0.8rem;">${
          d.email
        }</span>
      </div>

      <div style="margin-bottom: 0.5rem;">
        <strong>Internship:</strong> ${d.internship_title} · ${d.company} (${
      d.sector
    })
      </div>

      <div style="margin-bottom: 0.5rem;">
        <strong>Skills:</strong> ${d.skills || "Not specified"}
      </div>

      <div style="margin-bottom: 0.5rem;">
        <strong>Duration:</strong> ${d.duration_days} days<br/>
        <strong>Working Days:</strong> ${d.working_days} days<br/>
        <strong>Remaining Days:</strong> ${d.remaining_days} days
      </div>

      <div style="margin-bottom: 0.5rem;">
        <strong>Performance:</strong> ${
          d.performance_percentage
        }%<br/>
        <strong>Leave Used:</strong> ${d.leave_percentage}%
      </div>

      <div>
        <strong>Resume:</strong>
        ${
          d.resume_url
            ? `<a href="${d.resume_url}" target="_blank">View resume</a>`
            : "Not uploaded"
        }
      </div>
    `;
  } catch (err) {
    console.error("Failed to load user details", err);
    panel.textContent = "Failed to load details.";
  }
}

import { apiRequest } from "./api.js";

document.addEventListener("DOMContentLoaded", loadUsers);

async function loadUsers() {
    const tbody = document.getElementById("usersBody");
    tbody.innerHTML = "";

    const users = await apiRequest("/admin/users/accepted");

    if (!users.length) {
        tbody.innerHTML = "<tr><td colspan='4'>No active interns</td></tr>";
        return;
    }

    users.forEach(u => {
        const row = document.createElement("tr");
        row.innerHTML = `
            <td><button onclick="openUser(${u.user_id})" class="btn btn-ghost">${u.name}</button></td>
            <td>${u.internship}</td>
            <td>${u.company}</td>
            <td>${u.skills}</td>
        `;
        tbody.appendChild(row);
    });
}

/* ===== Detailed View ===== */
window.openUser = async function(id) {
    const u = await apiRequest(`/admin/users/${id}`);

    alert(`
Name: ${u.name}
Internship: ${u.internship}
Company: ${u.company}

Days Completed: ${u.days_passed}
Remaining Days: ${u.days_remaining}
Status: ${u.status}
    `);

    /* Auto-complete if time up */
    if (u.days_remaining <= 0) {
        await apiRequest(`/admin/users/${id}/complete`, { method: "POST" });
        alert("Internship completed and archived!");
        loadUsers();
    }
};

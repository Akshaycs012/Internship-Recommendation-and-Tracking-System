import { apiRequest } from "./api.js";

document.addEventListener("DOMContentLoaded", () => loadApplications());

async function loadApplications() {
    const tbody = document.getElementById("applicationsBody");
    tbody.innerHTML = "";

    const apps = await apiRequest("/admin/applications");

    if (!apps.length) {
        tbody.innerHTML = "<tr><td colspan='4'>No pending applications</td></tr>";
        return;
    }

    apps.forEach(a => {
        const row = document.createElement("tr");
        row.innerHTML = `
            <td>${a.student}</td>
            <td>${a.internship}</td>
            <td>${a.skills}</td>
            <td>
                <button class='btn btn-success' onclick="approveModal(${a.app_id})">Approve</button>
                <button class='btn btn-danger' onclick="rejectApplication(${a.app_id})">Reject</button>
            </td>
        `;
        tbody.appendChild(row);
    });
}

/* ===== Approve + Duration Modal ===== */
window.approveModal = function(appID) {
    const days = prompt("Enter internship duration in DAYS:");
    if (!days || isNaN(days)) return alert("Invalid number");

    approve(appID, days);
};

async function approve(id, days) {
    await apiRequest(`/admin/applications/${id}/approve`, {
        method: "POST",
        body: JSON.stringify({ duration_days: Number(days) })
    });

    alert("Approved");
    loadApplications();
}

/* ===== Reject Application ===== */
window.rejectApplication = async function(id) {
    await apiRequest(`/admin/applications/${id}/reject`, { method:"PATCH" });
    loadApplications();
}

// static/js/admin-internships.js
// Handles:
//   - listing internships
//   - when "View" clicked => load applications
//   - filter by status
//   - approve / reject
//   - open resume PDF in new tab
import { apiRequest } from "./api.js";

let selectedInternshipId = null;
let currentFilter = "pending";

// ================= LOAD INTERNSHIPS ==================
document.addEventListener("DOMContentLoaded", () => {
  loadInternships();

  // wire filter buttons once
  document.querySelectorAll("[data-filter]").forEach((btn) => {
    btn.addEventListener("click", () => {
      currentFilter = btn.dataset.filter;
      // visual active state
      document
        .querySelectorAll("[data-filter]")
        .forEach((b) => b.classList.remove("btn-primary"));
      btn.classList.add("btn-primary");
      loadApplications();
    });
  });
});

async function loadInternships() {
  const tbody = document.getElementById("internshipsBody");
  tbody.innerHTML =
    '<tr><td colspan="4" style="color:var(--text-muted);">Loading...</td></tr>';

  try {
    const data = await apiRequest("/admin/internships");

    if (!data.length) {
      tbody.innerHTML =
        '<tr><td colspan="4" style="color:var(--text-muted);">No internships created yet</td></tr>';
      return;
    }

    tbody.innerHTML = "";
    data.forEach((intern) => {
      const row = document.createElement("tr");
      row.innerHTML = `
            <td>${intern.title}</td>
            <td>${intern.company}</td>
            <td>${intern.industry ?? "-"}</td>
            <td><button class="btn btn-primary" data-id="${intern.id}">View</button></td>
        `;
      const btn = row.querySelector("button");
      btn.onclick = () => selectInternship(intern.id);
      tbody.appendChild(row);
    });
  } catch (err) {
    console.error("Failed to load internships", err);
    tbody.innerHTML =
      '<tr><td colspan="4" style="color:red;">Failed to load internships</td></tr>';
  }
}

// ================= SELECT INTERNSHIP ==================
function selectInternship(id) {
  selectedInternshipId = id;
  loadApplications();
}

// ================= LOAD APPLICATIONS ==================
async function loadApplications() {
  const tbody = document.getElementById("appsBody");
  if (!tbody) return;

  if (!selectedInternshipId) {
    tbody.innerHTML =
      '<tr><td colspan="5" style="color:var(--text-muted);">Select internship first</td></tr>';
    return;
  }

  tbody.innerHTML =
    '<tr><td colspan="5" style="color:var(--text-muted);">Loading...</td></tr>';

  try {
    let url = `/admin/internships/${selectedInternshipId}/applications`;
    if (currentFilter !== "all") {
      url += `?status=${currentFilter}`;
    }

    const apps = await apiRequest(url);

    if (!apps.length) {
      tbody.innerHTML =
        '<tr><td colspan="5" style="color:var(--text-muted);">No applications found</td></tr>';
      return;
    }

    tbody.innerHTML = "";
    apps.forEach((a) => {
      const row = document.createElement("tr");

      // decide which buttons to show based on status
      let actionsHtml = "";
      if (a.status === "pending") {
        actionsHtml = `
          <button class="btn btn-primary btn-sm" data-approve="${a.id}">Approve</button>
          <button class="btn btn-ghost btn-sm" data-reject="${a.id}">Reject</button>
        `;
      } else if (a.status === "approved") {
        actionsHtml = `
          <button class="btn btn-ghost btn-sm" data-reject="${a.id}">Mark Rejected</button>
        `;
      } else if (a.status === "rejected") {
        actionsHtml = `
          <button class="btn btn-primary btn-sm" data-approve="${a.id}">Re-Approve</button>
        `;
      }

      const resumeHtml = a.resume_url
        ? `<a href="${a.resume_url}" target="_blank" class="btn btn-ghost btn-sm">View</a>`
        : `<span style="color:var(--text-muted);font-size:0.8rem;">No resume</span>`;

      row.innerHTML = `
        <td>${a.student}</td>
        <td>${a.email}</td>
        <td>${resumeHtml}</td>
        <td>${a.status}</td>
        <td>${actionsHtml}</td>
      `;
      tbody.appendChild(row);
    });

    bindStatusActions();
  } catch (err) {
    console.error("Failed to load applications", err);
    tbody.innerHTML =
      '<tr><td colspan="5" style="color:red;">Error loading applications</td></tr>';
  }
}

// ================= UPDATE STATUS ==================
function bindStatusActions() {
  document.querySelectorAll("[data-approve]").forEach((btn) => {
    btn.onclick = async () => {
      const id = btn.dataset.approve;
      await apiRequest(`/admin/applications/{id}/approve`.replace("{id}", id), {
        method: "PATCH",
      });
      loadApplications();
    };
  });

  document.querySelectorAll("[data-reject]").forEach((btn) => {
    btn.onclick = async () => {
      const id = btn.dataset.reject;
      await apiRequest(`/admin/applications/{id}/reject`.replace("{id}", id), {
        method: "PATCH",
      });
      loadApplications();
    };
  });
}

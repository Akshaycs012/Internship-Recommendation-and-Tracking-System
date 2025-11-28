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
async function loadApplicants(id){
    const tbody=document.getElementById("internApps");
    tbody.innerHTML=`<tr><td colspan=4>Loading...</td></tr>`;

    const res=await apiRequest(`/admin/internships/${id}/applications`);

    tbody.innerHTML="";
    res.forEach(s=>{
        tbody.innerHTML+=`
        <tr>
            <td>${s.student}</td>
            <td><a href="${s.resume_url}" target="_blank">View Resume</a></td>
            <td>${s.status}</td>
            <td>
                <button onclick="approve(${s.id})" class="btn btn-success">Approve</button>
                <button onclick="reject(${s.id})" class="btn btn-danger">Reject</button>
            </td>
        </tr>`;
    })
}

async function approve(id){
    await apiRequest(`/admin/applications/${id}/approve`, { method:"PATCH" });
    loadInternships();
}

async function reject(id){
    await apiRequest(`/admin/applications/${id}/reject`, { method:"PATCH" });
    loadInternships();
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


async function viewTasks(id){
    const tasks=await apiRequest(`/admin/internships/${id}/tasks`);
    alert(JSON.stringify(tasks,null,2)); // later replace with UI modal
}

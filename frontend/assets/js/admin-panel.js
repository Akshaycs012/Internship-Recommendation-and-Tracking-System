import { apiRequest } from "./api.js";

document.addEventListener("DOMContentLoaded",()=>{
    handleInternshipForm();
    loadApplications();
});

// ------------------- Internship Form -------------------
function handleInternshipForm(){
    const form=document.getElementById("addInternshipForm");
    if(!form) return;

    form.addEventListener("submit",async(e)=>{
        e.preventDefault();

        const body={
            title:intTitle.value,
            company:intCompany.value,
            location:intLocation.value,
            skills:intSkills.value,
            industry:intIndustry.value
        };

        await apiRequest("/admin/internships",{
            method:"POST",
            headers:{"Content-Type":"application/json"},
            body:JSON.stringify(body)
        });

        alert("Internship Added");
        form.reset();
    });
}


// ------------------- Load Application List -------------------
async function loadApplications(){
    const tbody=document.getElementById("adminApplicationsBody");
    tbody.innerHTML=`<tr><td colspan="4">Loading...</td></tr>`;

    const apps=await apiRequest("/admin/applications");

    if(!apps.length){
        tbody.innerHTML=`<tr><td colspan="4">No applications yet</td></tr>`;
        return;
    }

    tbody.innerHTML="";
    apps.forEach(a=>{
        tbody.innerHTML+=`
        <tr>
            <td>${a.student_name}</td>
            <td>${a.internship_title}</td>
            <td>${a.status}</td>
            <td>
                <button class="btn btn-primary" data-approve="${a.id}">Approve</button>
                <button class="btn btn-danger" data-reject="${a.id}">Reject</button>
            </td>
        </tr>
        `;
    });

    bindEvents();
}


// ------------------- Approve / Reject Buttons -------------------
function bindEvents(){
    document.querySelectorAll("[data-approve]").forEach(b=>
        b.onclick=()=>update(b.dataset.approve,"approve"));
    document.querySelectorAll("[data-reject]").forEach(b=>
        b.onclick=()=>update(b.dataset.reject,"reject"));
}

async function update(id,action){
    await apiRequest(`/admin/applications/${id}/${action}`,{method:"PATCH"});
    loadApplications();
}


// ------------------- NEW — LOAD APPLICANTS PER INTERNSHIP -------------------
async function loadApplicants(internshipId) {
    const tbody = document.querySelector("#applicationsTable tbody");
    tbody.innerHTML = "<tr><td colspan='5'>Loading...</td></tr>";

    try {
        const res = await apiRequest(`/admin/internships/${internshipId}/applicants`);
        if (!res.length) {
            tbody.innerHTML = "<tr><td colspan='5'>No applications found</td></tr>";
            return;
        }

        tbody.innerHTML = "";
        res.forEach(a => {
            const row = document.createElement("tr");
            row.innerHTML = `
                <td>${a.name}</td>
                <td>${a.email}</td>
                <td><button class="btn btn-secondary">View PDF</button></td>
                <td>${a.status}</td>
                <td>
                    <button class="btn btn-success" onclick="approve(${a.application_id})">Approve</button>
                    <button class="btn btn-danger" onclick="reject(${a.application_id})">Reject</button>
                </td>
            `;
            tbody.appendChild(row);
        });

    } catch(err) {
        tbody.innerHTML = "<tr><td colspan='5'>Error loading data</td></tr>";
    }
}

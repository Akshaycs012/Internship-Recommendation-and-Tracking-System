import { apiRequest } from "./api.js";

document.addEventListener("DOMContentLoaded",()=>{
    handleInternshipForm();
    loadApplications();
});

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


// ================ APPLICATIONS LOAD ================

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

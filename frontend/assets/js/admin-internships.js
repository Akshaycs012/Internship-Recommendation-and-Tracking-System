import { apiRequest } from "./api.js";

let selected=null,filter="pending";

document.addEventListener("DOMContentLoaded",()=>loadInternships());

async function loadInternships(){
    const box=document.getElementById("internshipsBody");
    box.innerHTML=`<tr><td colspan='4'>Loading...</td></tr>`;

    const list=await apiRequest("/admin/internships");

    if(!list.length) return box.innerHTML=`<tr><td colspan='4'>No Internships</td></tr>`;

    box.innerHTML="";
    list.forEach(x=>{
        box.innerHTML+=`
        <tr>
            <td>${x.title}</td>
            <td>${x.company}</td>
            <td>${x.industry}</td>
            <td><button class='btn btn-primary' onclick='select(${x.id})'>View</button></td>
        </tr>`;
    });
}

window.select=function(id){
    selected=id;
    loadApps();
}

async function loadApps(){
    const box=document.getElementById("appsBody");
    if(!selected) return box.innerHTML=`<tr><td colspan='4'>Select Internship First</td></tr>`;

    let url=`/admin/internships/${selected}/applications`;
    if(filter!=="all") url+=`?status=${filter}`;

    const apps=await apiRequest(url);

    if(!apps.length) return box.innerHTML=`<tr><td colspan='4'>No Applications Found</td></tr>`;

    box.innerHTML="";
    apps.forEach(x=>{
        box.innerHTML+=`
        <tr>
            <td>${x.student}</td>
            <td>${x.email}</td>
            <td>${x.status}</td>
            <td>
                <button onclick='update(${x.id},"approve")' class='btn btn-success'>Approve</button>
                <button onclick='update(${x.id},"reject")' class='btn btn-danger'>Reject</button>
            </td>
        </tr>`;
    });
}

window.update=async(id,type)=>{
    await apiRequest(`/admin/applications/${id}/${type}`,{method:"PATCH"});
    loadApps();
}

document.querySelectorAll("[data-filter]").forEach(b=>b.onclick=()=>{
    filter=b.dataset.filter;
    loadApps();
});

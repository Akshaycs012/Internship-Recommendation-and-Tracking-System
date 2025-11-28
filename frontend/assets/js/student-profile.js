import { apiRequest } from "./api.js";

document.addEventListener("DOMContentLoaded", loadProfile);

async function loadProfile(){
    const data = await apiRequest("/students/me/profile");

    set("full_name", data.name);
    set("email", data.email);
    set("phone", data.phone);
    set("age", data.age);
    set("dob", data.date_of_birth);
    set("education", data.education);
    set("experience", data.experience);
    set("skills", data.skills);
    set("portfolio_url", data.portfolio_url);
    set("linkedin_url", data.linkedin_url);
    set("github_url", data.github_url);
    set("skills_rating", data.skills_rating);

    document.getElementById("resumeDisplay").innerText =
       data.resume_url ? "Resume Uploaded ✓" : "No resume uploaded";

    if(data.profile_complete) lockForm();
}

document.getElementById("saveBtn").onclick = async(e)=>{
    e.preventDefault();
    const body = collect();

    await apiRequest("/students/me/profile",{
        method:"PUT",
        headers:{ "Content-Type":"application/json" },
        body: JSON.stringify(body)
    });

    alert("Profile saved successfully");
    lockForm();
};

document.getElementById("uploadResumeBtn").onclick = async()=>{
    const file = document.getElementById("resumeFile").files[0];
    if(!file) return alert("Choose resume first!");

    const fd = new FormData();
    fd.append("file", file);

    const token = localStorage.getItem("access_token");
    const r = await fetch("http://127.0.0.1:8000/students/me/resume",{
    method:"POST",
    headers:{ Authorization:`Bearer ${token}` },
    body:fd
});


    if(!r.ok) return alert("Upload failed");

// refresh profile so resume_url loads from DB
await loadProfile();

alert("Resume uploaded successfully!");

};

document.getElementById("editBtn").onclick = () => unlockForm();

function collect(){
    let ids=["full_name","phone","age","dob","education","experience","skills",
             "linkedin_url","github_url","portfolio_url","skills_rating"];

    let obj={};
    ids.forEach(id => obj[id]=get(id));
    return obj;
}

function set(id,val){ document.getElementById(id).value = val || "" }
function get(id){ return document.getElementById(id).value }

function lockForm(){
    document.querySelectorAll("input,textarea").forEach(e=> e.disabled=true);
    document.getElementById("saveBtn").style.display="none";
    document.getElementById("editBtn").style.display="inline-block";
}

function unlockForm(){
    document.querySelectorAll("input,textarea").forEach(e=> e.disabled=false);
    document.getElementById("editBtn").style.display="none";
    document.getElementById("saveBtn").style.display="inline-block";
}

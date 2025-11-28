import { apiRequest } from "./api.js";

document.addEventListener("DOMContentLoaded",loadTasks);

async function loadTasks(){
   const table=document.getElementById("taskTable");
   const tasks=await apiRequest("/students/my-tasks");

   if(!tasks.length){ table.innerHTML="<tr><td>No Tasks Yet</td></tr>"; return;}

   table.innerHTML="";
   tasks.forEach(t=>{
      table.innerHTML+=`
      <tr>
        <td>${t.title}</td>
        <td>Due: ${t.due_date}</td>
        <td>
          <form onsubmit="upload(${t.id},event)">
            <input type="file" required>
            <button>Upload</button>
          </form>
        </td>
      </tr>`;
   });
}

window.upload=async(id,e)=>{
   e.preventDefault();
   const file=e.target[0].files[0];
   const form=new FormData(); form.append("file",file);
   await apiRequest(`/students/submit-task/${id}`,{method:"POST",body:form});
   alert("Submitted");
}

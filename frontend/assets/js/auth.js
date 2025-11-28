import { apiRequest, setAuthToken } from "/static/js/api.js";

document.addEventListener("DOMContentLoaded", () => {
  const loginForm = document.getElementById("loginForm");
  const registerForm = document.getElementById("registerForm");
  const loginToggle = document.getElementById("loginToggle");
  const registerToggle = document.getElementById("registerToggle");

  function showLogin(){ loginForm.style.display="grid"; registerForm.style.display="none"; }
  function showRegister(){ loginForm.style.display="none"; registerForm.style.display="grid"; }

  loginToggle.onclick = showLogin;
  registerToggle.onclick = showRegister;

  if(location.hash==="#register") showRegister();

  loginForm.onsubmit = async(e)=>{
    e.preventDefault();
    const email = loginEmail.value;
    const password = loginPassword.value;

    try{
      const res = await apiRequest("/auth/login",{
        method:"POST", body:JSON.stringify({email,password})
      });
      setAuthToken(res.access_token);
      const role = JSON.parse(atob(res.access_token.split('.')[1])).role;
      location.href = role==="student" ? "/student-dashboard.html" :
                      role==="mentor" ? "/mentor-dashboard.html" :
                      "/admin-panel.html";
    }catch(e){ alert("Login failed"); }
  };

  registerForm.onsubmit = async(e)=>{
    e.preventDefault();
    try{
      const res = await apiRequest("/auth/register",{
        method:"POST",
        body:JSON.stringify({
          full_name:regName.value,
          email:regEmail.value,
          password:regPassword.value,
          role:regRole.value
        })
      });
      setAuthToken(res.access_token);
      location.href = regRole.value==="student"?"/student-dashboard.html":
                      regRole.value==="mentor"?"/mentor-dashboard.html":
                      "/admin-panel.html";

    }catch(e){ alert("Registration failed"); }
  };
});

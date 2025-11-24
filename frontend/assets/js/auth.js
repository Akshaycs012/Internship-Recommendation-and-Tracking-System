import { apiRequest, setAuthToken } from "./api.js";




document.addEventListener("DOMContentLoaded", () => {
  const loginToggle = document.getElementById("loginToggle");
  const registerToggle = document.getElementById("registerToggle");
  const loginForm = document.getElementById("loginForm");
  const registerForm = document.getElementById("registerForm");

  function showLogin() {
    loginForm.style.display = "grid";
    registerForm.style.display = "none";
    loginToggle.classList.add("btn-primary");
    registerToggle.classList.remove("btn-primary");
  }

  function showRegister() {
    loginForm.style.display = "none";
    registerForm.style.display = "grid";
    loginToggle.classList.remove("btn-primary");
    registerToggle.classList.add("btn-primary");
  }

  loginToggle.addEventListener("click", showLogin);
  registerToggle.addEventListener("click", showRegister);

  if (window.location.hash === "#register") showRegister();

  // ✅ LOGIN CONNECTION
  loginForm.addEventListener("submit", async (e) => {
    e.preventDefault();

    const email = document.getElementById("loginEmail").value;
    const password = document.getElementById("loginPassword").value;

    try {
      const res = await apiRequest("/auth/login", {
        method: "POST",
        body: JSON.stringify({ email, password }),
      });

      setAuthToken(res.access_token);

      // ✅ Decode JWT to get role
      const payload = JSON.parse(atob(res.access_token.split(".")[1]));
      const role = payload.role;

      if (role === "student") window.location.href = "./student-dashboard.html";
      else if (role === "mentor") window.location.href = "./mentor-dashboard.html";
      else if (role === "admin") window.location.href = "./admin-panel.html";
      else alert("Unknown role");

    } catch (err) {
      alert("Login failed");
    }
  });

  // ✅ REGISTER CONNECTION
  registerForm.addEventListener("submit", async (e) => {
    e.preventDefault();

    const full_name = document.getElementById("regName").value;
    const email = document.getElementById("regEmail").value;
    const password = document.getElementById("regPassword").value;
    const role = document.getElementById("regRole").value;

    try {
      const res = await apiRequest("/auth/register", {
        method: "POST",
        body: JSON.stringify({ full_name, email, password, role }),
      });

      setAuthToken(res.access_token);

      if (role === "student") window.location.href = "./student-dashboard.html";
      else if (role === "mentor") window.location.href = "./mentor-dashboard.html";
      else window.location.href = "./admin-panel.html";

    } catch (err) {
      alert("Registration failed");
    }
  });
});

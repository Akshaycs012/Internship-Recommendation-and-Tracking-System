document.addEventListener("DOMContentLoaded", () => {
  const loginToggle = document.getElementById("loginToggle");
  const registerToggle = document.getElementById("registerToggle");
  const loginForm = document.getElementById("loginForm");
  const registerForm = document.getElementById("registerForm");

  function showLogin() {
    loginForm.style.display = "grid";
    registerForm.style.display = "none";
    loginToggle.classList.add("btn-primary");
    loginToggle.classList.remove("btn-ghost");
    registerToggle.classList.remove("btn-primary");
    registerToggle.classList.add("btn-ghost");
  }

  function showRegister() {
    loginForm.style.display = "none";
    registerForm.style.display = "grid";
    loginToggle.classList.remove("btn-primary");
    loginToggle.classList.add("btn-ghost");
    registerToggle.classList.add("btn-primary");
    registerToggle.classList.remove("btn-ghost");
  }

  loginToggle.addEventListener("click", showLogin);
  registerToggle.addEventListener("click", showRegister);

  // If URL has #register, open registration directly
  if (window.location.hash === "#register") {
    showRegister();
  }

  // TODO: connect to FastAPI /auth/login and /auth/register later
  loginForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    // placeholder – connect API later
    alert("Login will be connected to backend /auth/login");
  });

  registerForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    // placeholder – connect API later
    alert("Register will be connected to backend /auth/register");
  });
});

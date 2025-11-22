// Highlight active nav link based on current page
function setActiveNavLink() {
  const path = window.location.pathname;
  const links = document.querySelectorAll(".nav-link");

  links.forEach((link) => {
    const href = link.getAttribute("href");
    if (!href) return;

    const file = href.split("/").pop();
    if (path.endsWith(file)) {
      link.classList.add("nav-link--active");
    }
  });

  // Default: highlight Home when at / or /index.html
  if (path === "/" || path.endsWith("/frontend") || path.endsWith("/frontend/")) {
    document.querySelectorAll('.nav-link[href="./index.html"]').forEach((l) =>
      l.classList.add("nav-link--active")
    );
  }
}

document.addEventListener("DOMContentLoaded", () => {
  setActiveNavLink();
});

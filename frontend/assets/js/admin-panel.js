document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("addInternshipForm");

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    // TODO: POST to /admin/internships
    alert("Internship will be created through backend admin endpoint.");
  });
});

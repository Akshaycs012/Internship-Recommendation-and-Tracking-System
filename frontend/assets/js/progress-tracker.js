document.addEventListener("DOMContentLoaded", () => {
  const uploadForm = document.getElementById("uploadForm");

  uploadForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    // TODO: send file to backend /progress/upload
    alert("File upload will be implemented with FastAPI endpoint.");
  });
});

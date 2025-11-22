document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("searchForm");

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    // TODO: call FastAPI /recommendations endpoint with filters
    alert("Search filters will be sent to backend recommendation engine.");
  });
});

document.addEventListener("DOMContentLoaded", () => {
  const progressDiv = document.getElementById("mentorStudentProgress");
  const feedbackForm = document.getElementById("feedbackForm");

  document.querySelectorAll("#studentsList button[data-student]").forEach((btn) => {
    btn.addEventListener("click", () => {
      const student = btn.getAttribute("data-student");
      // TODO: fetch progress from backend /mentor/student/{id}
      progressDiv.textContent = `Showing progress summary for Student ${student} (placeholder).`;
    });
  });

  feedbackForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    // TODO: send feedback to /mentor/feedback
    alert("Feedback will be submitted to backend mentor_feedback endpoint.");
  });
});

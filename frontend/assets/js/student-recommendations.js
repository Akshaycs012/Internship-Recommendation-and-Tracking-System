// frontend/assets/js/student-recommendations.js
import { apiRequest } from "./api.js";

document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("searchForm");

  if (form) {
    form.addEventListener("submit", (e) => {
      e.preventDefault();
      loadRecommendations();
    });
  }

  // initial load: uses student's profile skills when skills field is empty
  loadRecommendations();
});

async function loadRecommendations() {
  const keywordsInput = document.getElementById("searchKeywords");
  const skillsInput = document.getElementById("searchSkills");

  const keywords = keywordsInput?.value || "";
  const skills = skillsInput?.value || "";

  const params = new URLSearchParams();
  if (keywords) params.append("keywords", keywords);
  if (skills) params.append("skills", skills);

  try {
    const recs = await apiRequest(`/internships/recommendations?${params.toString()}`, { method:"GET" });
    renderRecommendations(recs);
  } catch (err) {
    console.error("Failed to load recommendations", err);
    alert("Failed to load recommendations from server.");
  }
}

function renderRecommendations(list) {
  const container = document.getElementById("recsList");
  if (!container) return;

  container.innerHTML = "";

  if (!list || !list.length) {
    container.innerHTML =
      '<p style="font-size:0.9rem; color:var(--text-muted);">No internships found. Try changing filters or ask admin to add internships.</p>';
    return;
  }

  list.forEach((item) => {
    const card = document.createElement("div");
    card.className = "card";

    const matchClass =
      item.match >= 80
        ? "badge-success"
        : item.match >= 50
        ? "badge-warning"
        : "";

    card.innerHTML = `
      <div class="card-header">
        <div>
          <div class="card-title">${item.title}</div>
          <div class="card-subtitle">
            ${item.company} · ${item.location || "Location not specified"}
          </div>
        </div>
        <div class="badge ${matchClass}">
          Match: ${item.match}%
        </div>
      </div>
      <p style="font-size:0.85rem; color:var(--text-muted);">
        Skills needed: ${item.skills || "Not specified"}
      </p>
      <div style="display:flex; gap:0.75rem; margin-top:0.5rem;">
        <button class="btn btn-ghost" type="button">View Details</button>
        <button class="btn btn-primary" type="button" data-apply="${item.id}">
          Apply
        </button>
      </div>
    `;

    container.appendChild(card);
  });

  wireApplyButtons(container);
}

function wireApplyButtons(container) {
  container.querySelectorAll("[data-apply]").forEach((btn) => {
    btn.addEventListener("click", async () => {
      const internshipId = btn.getAttribute("data-apply");
      if (!internshipId) return;

      try {
        await apiRequest(`/applications/apply/${internshipId}`, {
          method: "POST",
        });

        btn.textContent = "Applied";
        btn.disabled = true;
        btn.classList.add("btn-ghost");
        alert("Application submitted.");
      } catch (err) {
        console.error("Failed to apply", err);
        alert("Could not apply – maybe you already applied?");
      }
    });
  });
}

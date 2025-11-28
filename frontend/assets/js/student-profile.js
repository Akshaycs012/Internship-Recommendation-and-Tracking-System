// frontend/assets/js/student-profile.js
import { apiRequest } from "./api.js";

const API_BASE = "http://127.0.0.1:8000";

document.addEventListener("DOMContentLoaded", () => {
  loadProfile();

  const btnUpload = document.getElementById("uploadResume");
  const btnSaveSkills = document.getElementById("saveSkills");

  if (btnUpload) {
    btnUpload.addEventListener("click", onUploadResume);
  }

  if (btnSaveSkills) {
    btnSaveSkills.addEventListener("click", onSaveSkills);
  }
});

async function loadProfile() {
  const skillBox = document.getElementById("skillBox");

  try {
    const profile = await apiRequest("/students/me/profile");
    if (skillBox) {
      skillBox.value = profile.skills || "";
    }
  } catch (err) {
    console.error("Failed to load profile", err);
  }
}

async function onUploadResume() {
  const fileInput = document.getElementById("resumeFile");
  const statusEl = document.getElementById("resumeStatus");

  if (!fileInput || !fileInput.files.length) {
    alert("Please choose a resume file first.");
    return;
  }

  const token = localStorage.getItem("access_token");
  if (!token) {
    window.location.href = "./login.html";
    return;
  }

  const formData = new FormData();
  formData.append("file", fileInput.files[0]); // allow all file types

  try {
    const res = await fetch(`${API_BASE}/students/me/resume`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`,
      },
      body: formData,
    });

    if (!res.ok) {
      throw new Error("Upload failed");
    }

    const data = await res.json();
    if (statusEl) {
      statusEl.textContent = `Uploaded: ${data.file_url}`;
    }
    alert("Resume uploaded successfully.");
  } catch (err) {
    console.error("Resume upload failed", err);
    if (statusEl) {
      statusEl.textContent = "Failed to upload resume.";
    }
  }
}

async function onSaveSkills() {
  const skillBox = document.getElementById("skillBox");
  const msgEl = document.getElementById("skillMsg");
  if (!skillBox) return;

  const skills = skillBox.value || "";

  try {
    // We send skills as query param to keep it simple: /students/me/skills?skills=...
    const params = new URLSearchParams();
    params.append("skills", skills);

    const data = await apiRequest(`/students/me/skills?${params.toString()}`, {
      method: "PUT",
    });

    if (msgEl) {
      msgEl.textContent = "Skills saved.";
    }
    alert("Skills updated.");
  } catch (err) {
    console.error("Failed to save skills", err);
    if (msgEl) {
      msgEl.textContent = "Failed to save skills.";
    }
  }
}

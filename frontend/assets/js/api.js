// Simple helper for calling backend (plug FastAPI later)

const API_BASE_URL = "http://127.0.0.1:8000";

function getAuthToken() {
  return localStorage.getItem("access_token");
}

function setAuthToken(token) {
  localStorage.setItem("access_token", token);
}

async function apiRequest(path, options = {}) {
  const token = getAuthToken();
  const headers = options.headers || {};

  if (!(options.body instanceof FormData)) {
    headers["Content-Type"] = headers["Content-Type"] || "application/json";
  }

  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const res = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers,
  });

  if (!res.ok) {
    const msg = await res.text();
    throw new Error(msg || `API error ${res.status}`);
  }

  const contentType = res.headers.get("content-type") || "";
  if (contentType.includes("application/json")) {
    return res.json();
  }
  return res.text();
}

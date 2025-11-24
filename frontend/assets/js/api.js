const BASE_URL = "http://127.0.0.1:8000";

export async function apiRequest(endpoint, options = {}) {
  const token = localStorage.getItem("access_token");

  const res = await fetch(BASE_URL + endpoint, {
    method: options.method || "GET",
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {})
    },
    body: options.body || null
  });

  if (!res.ok) {
    throw new Error("API error");
  }

  return res.json();
}

export function setAuthToken(token) {
  localStorage.setItem("access_token", token);
}

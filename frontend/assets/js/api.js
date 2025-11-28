// frontend/assets/js/api.js

const BASE_URL = "http://127.0.0.1:8000";

export async function apiRequest(endpoint, options = {}) {
  const token = localStorage.getItem("access_token");

  const headers = {
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };

  let body = null;

  if (options.body instanceof FormData) {
    // browser will set correct multipart boundary
    body = options.body;
  } else if (options.body) {
    headers["Content-Type"] = "application/json";
    body = options.body;
  }

  const res = await fetch(BASE_URL + endpoint, {
    method: options.method || "GET",
    headers,
    body,
  });

  if (!res.ok) {
    // try to read error message if any
    let msg = "API error";
    try {
      const data = await res.json();
      if (data && data.detail) msg = data.detail;
    } catch (_) {
      // ignore
    }
    throw new Error(msg);
  }

  // some endpoints might return no content
  const text = await res.text();
  if (!text) return null;
  try {
    return JSON.parse(text);
  } catch {
    return text;
  }
}

export function setAuthToken(token) {
  localStorage.setItem("access_token", token);
}

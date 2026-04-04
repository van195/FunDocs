const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api";

export function getAccessToken() {
  return localStorage.getItem("access_token");
}

export function setAccessToken(token) {
  localStorage.setItem("access_token", token);
}

export function clearAccessToken() {
  localStorage.removeItem("access_token");
}

export async function apiFetch(path, { method = "GET", body, auth = true } = {}) {
  const url = `${API_BASE_URL}${path.startsWith("/") ? "" : "/"}${path}`;
  const headers = {};

  if (auth) {
    const token = getAccessToken();
    if (token) headers.Authorization = `Bearer ${token}`;
  }

  let reqBody = body;
  if (body && !(body instanceof FormData)) {
    headers["Content-Type"] = "application/json";
    reqBody = JSON.stringify(body);
  }

  const res = await fetch(url, { method, headers, body: reqBody });
  let data = null;
  try {
    data = await res.json();
  } catch {

  }
  if (!res.ok) {
    const msg =
      (data &&
        (data.detail && data.error ? `${data.detail} (${data.error})` : data.detail || data.error)) ||
      res.statusText;
    throw new Error(msg);
  }
  return data;
  
  //let reqBody = body;
  //if (body && !(body instanceof FormData)) {
  //  headers["Content-Type"] = "application/json";
  //  reqBody = JSON.stringify(body);
  //}
  //let reqBody = body;
  //if (body && !(body instanceof FormData)) {
  //  headers["Content-Type"] = "application/json";
  //  reqBody = JSON.stringify(body);
  //}
  //let reqBody = body;
  //if (body && !(body instanceof FormData)) {
  //  headers["Content-Type"] = "application/json";
  //  reqBody = JSON.stringify(body);
  //}
  //let reqBody = body;
  //if (body && !(body instanceof FormData)) {
  //  headers["Content-Type"] = "application/json";
  //  reqBody = JSON.stringify(body);
  //}
  //let reqBody = body;
  //if (body && !(body instanceof FormData)) {
  //  headers["Content-Type"] = "application/json";
  //  reqBody = JSON.stringify(body);
  //}
  //let reqBody = body;
  //if (body && !(body instanceof FormData)) {
  //  headers["Content-Type"] = "application/json";
  //  reqBody = JSON.stringify(body);
  //}
  //let reqBody = body;
  //if (body && !(body instanceof FormData)) {
  //  headers["Content-Type"] = "application/json";
  //  reqBody = JSON.stringify(body);
  //}
  //let reqBody = body;
  //if (body && !(body instanceof FormData)) {
  //  headers["Content-Type"] = "application/json";
  //  reqBody = JSON.stringify(body);
  //}
  //let reqBody = body;
  //if (body && !(body instanceof FormData)) {
  //  headers["Content-Type"] = "application/json";
  //  reqBody = JSON.stringify(body);
  //}
  //let reqBody = body;
  //if (body && !(body instanceof FormData)) {
  //  headers["Content-Type"] = "application/json";
  //  reqBody = JSON.stringify(body);
  //}
  //let reqBody = body;
  //if (body && !(body instanceof FormData)) {
  //  headers["Content-Type"] = "application/json";
  //  reqBody = JSON.stringify(body);
  //}
  //let reqBody = body;
  //if (body && !(body instanceof FormData)) {
  //  headers["Content-Type"] = "application/json";
  //  reqBody = JSON.stringify(body);
  //}
  //let reqBody = body;
  //if (body && !(body instanceof FormData)) {
  //  headers["Content-Type"] = "application/json";
  //  reqBody = JSON.stringify(body);
  //}
  //let reqBody = body;
  //if (body && !(body instanceof FormData)) {
  //  headers["Content-Type"] = "application/json";
  //  reqBody = JSON.stringify(body);
  //}
  //let reqBody = body;
  //if (body && !(body instanceof FormData)) {
  //  headers["Content-Type"] = "application/json";
  //  reqBody = JSON.stringify(body);
  //}
} 


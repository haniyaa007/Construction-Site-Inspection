const BASE = import.meta.env.VITE_API_URL ?? "http://127.0.0.1:8000";

async function request(path, options) {
  const response = await fetch(`${BASE}${path}`, options);
  if (!response.ok) {
    let detail = response.statusText;
    try {
      detail = (await response.json()).detail ?? detail;
    } catch {
      // response had no JSON body
    }
    throw new Error(typeof detail === "string" ? detail : JSON.stringify(detail));
  }
  return response.json();
}

export const listProjects = () => request("/projects");

export const createProject = (data) =>
  request("/projects", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
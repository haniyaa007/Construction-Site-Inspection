import { useEffect, useState } from "react";
import { createProject, listProjects } from "./api";
import "./App.css";

export default function App() {
  const [projects, setProjects] = useState([]);
  const [name, setName] = useState("");
  const [location, setLocation] = useState("");
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);

  async function refresh() {
    try {
      setProjects(await listProjects());
      setError(null);
    } catch (e) {
      setError(`${e.message}. Is the backend running on port 8000?`);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    refresh();
  }, []);

  async function handleSubmit(event) {
    event.preventDefault();
    try {
      await createProject({ name, location: location || null });
      setName("");
      setLocation("");
      await refresh();
    } catch (e) {
      setError(e.message);
    }
  }

  return (
    <main className="container">
      <h1>Construction Site Inspection</h1>

      <section className="card">
        <h2>New project</h2>
        <form onSubmit={handleSubmit} className="row">
          <input
            placeholder="Project name"
            value={name}
            onChange={(e) => setName(e.target.value)}
            required
          />
          <input
            placeholder="Location (optional)"
            value={location}
            onChange={(e) => setLocation(e.target.value)}
          />
          <button type="submit">Create</button>
        </form>
      </section>

      {error && <p className="error">{error}</p>}

      <section className="card">
        <h2>Projects</h2>
        {loading && <p>Loading…</p>}
        {!loading && projects.length === 0 && <p>No projects yet.</p>}
        <ul>
          {projects.map((p) => (
            <li key={p.id}>
              <strong>{p.name}</strong>
              {p.location && <span> · {p.location}</span>}
            </li>
          ))}
        </ul>
      </section>
    </main>
  );
}
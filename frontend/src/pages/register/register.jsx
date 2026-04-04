import './register.css';
import { apiFetch, clearAccessToken, getAccessToken, setAccessToken } from "../../api.js";
import { useState } from 'react';
function Register({ onAuthed }) {
  const [mode, setMode] = useState("login"); // login | register
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function submit(e) {
    e.preventDefault();
    setError("");
    setBusy(true);
    try {
      if (mode === "register") {
        await apiFetch("/auth/register/", {
          method: "POST",
          auth: false,
          body: { username, email, password }
        });
      }

      const tokens = await apiFetch("/auth/login/", {
        method: "POST",
        auth: false,
        body: { username, password }
      });
      setAccessToken(tokens.access);
      onAuthed();
    } catch (err) {
      setError(err.message || "Request failed");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="register">
      <h1>FunDocs</h1>
      <div className="card">
        <div className="tabs">
          
          <button
            className={mode === "register" ? "active" : ""}
            onClick={() => setMode("register")}
            type="button"
          >
            Register
          </button>
        </div>

        <form onSubmit={submit} className="form">
          <label>
            Username
            <input value={username} onChange={(e) => setUsername(e.target.value)} required />
          </label>

          {mode === "register" ? (
            <label>
              Email
              <input value={email} onChange={(e) => setEmail(e.target.value)} type="email" required />
            </label>
          ) : null}

          <label>
            Password
            <input value={password} onChange={(e) => setPassword(e.target.value)} type="password" required />
          </label>

          {error ? <div className="error">{error}</div> : null}
          <button disabled={busy} type="submit">
            {busy ? "Please wait..." : mode === "register" ? "Create account" : "Login"}
          </button>
        </form>
      </div>
    </div>
  );
}
export default Register;
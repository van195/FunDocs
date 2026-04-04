import './register.css';
import { apiFetch, clearAccessToken, getAccessToken, setAccessToken } from "../../api.js";
import ai from "../../assets/robot_hero.png"
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { PaymentGate } from '../../App.jsx';
function Register({ onAuthed,me ,loadMe}) {
    const navigation = useNavigate()
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
      if(!me.has_access) return <PaymentGate onPaid={loadMe} />
    } catch (err) {
      setError(err.message || "Request failed");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="register">
      <h1>FunDocs</h1>
        <div className="signUpContainer">
            <div className="card">
                <div className="tabs">
                
                    <button
                        className={mode === "register" ? "active" : ""}
                        onClick={() => setMode("register")}
                        type="button"
                    >
                        sign up
                    </button>
                </div>
                

             <form onSubmit={submit} className="form">
                <label>
                    
                    <input value={username} onChange={(e) => setUsername(e.target.value)} required placeholder='user name'/>
                </label>

                
                    <label>
                    <input value={email} onChange={(e) => setEmail(e.target.value)} type="email" required placeholder='email' />
                    </label>
                

                <label>
                    
                    <input value={password} onChange={(e) => setPassword(e.target.value)} type="password" required placeholder='password' />
                </label>

                {error ? <div className="error">{error}</div> : null}
                <button disabled={busy} type="submit">
                    {busy ? "Please wait..." : mode === "register" ? "Create account" : "Login"}
                </button>
             </form>
            </div>
            <div className="theTextDecore">
                
            </div>
      </div>
    </div>
  );
}
export default Register;
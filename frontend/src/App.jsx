import React, { useEffect, useMemo, useState } from "react";
import { apiFetch, clearAccessToken, getAccessToken, setAccessToken } from "./api";
import Register from "./pages/register/register";
import { Route,Routes } from "react-router-dom";
import Home from "./pages/home/home";
import Dashboard from "./pages/dashbord/dashboard";
import { useToggle } from "./context/PageContext";

export function PaymentGate({ onPaid }) {
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  async function startPayment() {
    setError("");
    setBusy(true);
    try {
      const res = await apiFetch("/payments/chapa/create/", { method: "POST" });
      if (!res.authorization_url) throw new Error("Missing authorization_url from server.");
      window.location.href = res.authorization_url;
    } catch (e) {
      setError(e.message || "Payment failed");
    } finally {
      setBusy(false);
    }
  }

  async function verifyAndCheckAccess() {
    setError("");
    setBusy(true);
    try {
     
      await apiFetch("/payments/chapa/verify-latest/", { method: "POST" });
      await onPaid();
    } catch (e) {
      setError(e.message || "Could not verify payment");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="container">
      <h1>Unlock your dashboard</h1>
      <div className="card">
        <p>You must pay with Chapa to upload files and chat with the AI.</p>
        {error ? <div className="error">{error}</div> : null}
        <button disabled={busy} onClick={startPayment}>
          {busy ? "Starting payment..." : "Pay with Chapa"}
        </button>
        <button className="secondary" onClick={verifyAndCheckAccess} type="button" disabled={busy}>
          I already paid (verify & unlock)
        </button>
      </div>
    </div>
  );
}

export function FunModeToggle({ funMode, onChange }) {
  return (
    <div className="buttonOfModes">
      <label className="toggle" >
        <input type="checkbox" checked={funMode} onChange={(e) => onChange(e.target.checked)} />
        <span>Fun Mode</span>
      </label>
      <label className="toggle1" >
        <button>Laser focus mode</button>
      </label>
      <label className="toggle" >
       <button>Smart Language translate</button>
      </label>
    </div>
    
  );
}

export function ChatBox({ documentId }) {
  const [messages, setMessages] = useState([]);
  const [question, setQuestion] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [Auth, setAuthentication] = useState(null);

 // const [messages, setMessages] = useState([]);
 // const [question, setQuestion] = useState("");
 // const [busy, setBusy] = useState(false);
 // const [error, setError] = useState("");
 // const [Auth, setAuthentication] = useState(null);
 // const [messages, setMessages] = useState([]);
 // const [question, setQuestion] = useState("");
 // const [busy, setBusy] = useState(false);
 // const [error, setError] = useState("");
 // const [Auth, setAuthentication] = useState(null);
 // const [messages, setMessages] = useState([]);
 // const [question, setQuestion] = useState("");
 // const [busy, setBusy] = useState(false);
 // const [error, setError] = useState("");
 // const [Auth, setAuthentication] = useState(null);
 // const [messages, setMessages] = useState([]);
 // const [question, setQuestion] = useState("");
 // const [busy, setBusy] = useState(false);
 // const [error, setError] = useState("");
 // const [Auth, setAuthentication] = useState(null);
 // const [messages, setMessages] = useState([]);
 // const [question, setQuestion] = useState("");
 // const [busy, setBusy] = useState(false);
 // const [error, setError] = useState("");
 // const [Auth, setAuthentication] = useState(null);
 // const [messages, setMessages] = useState([]);
 // const [question, setQuestion] = useState("");
 // const [busy, setBusy] = useState(false);
 // const [error, setError] = useState("");
 // const [Auth, setAuthentication] = useState(null);
 // const [messages, setMessages] = useState([]);
 // const [question, setQuestion] = useState("");
 // const [busy, setBusy] = useState(false);
 // const [error, setError] = useState("");
 // const [Auth, setAuthentication] = useState(null);
 // const [messages, setMessages] = useState([]);
 // const [question, setQuestion] = useState("");
 // const [busy, setBusy] = useState(false);
 // const [error, setError] = useState("");
 // const [Auth, setAuthentication] = useState(null);
 // const [messages, setMessages] = useState([]);
 // const [question, setQuestion] = useState("");
 // const [busy, setBusy] = useState(false);
 // const [error, setError] = useState("");
 // const [Auth, setAuthentication] = useState(null);
 // const [messages, setMessages] = useState([]);
 // const [question, setQuestion] = useState("");
 // const [busy, setBusy] = useState(false);
 // const [error, setError] = useState("");
 // const [Auth, setAuthentication] = useState(null);
 // const [messages, setMessages] = useState([]);
 // const [question, setQuestion] = useState("");
 // const [busy, setBusy] = useState(false);
 // const [error, setError] = useState("");
 // const [Auth, setAuthentication] = useState(null);
 // const [messages, setMessages] = useState([]);
 // const [question, setQuestion] = useState("");
 // const [busy, setBusy] = useState(false);
 // const [error, setError] = useState("");
 // const [Auth, setAuthentication] = useState(null);
 // const [messages, setMessages] = useState([]);
 // const [question, setQuestion] = useState("");
 // const [busy, setBusy] = useState(false);
 // const [error, setError] = useState("");
 // const [Auth, setAuthentication] = useState(null);
 // const [messages, setMessages] = useState([]);
 // const [question, setQuestion] = useState("");
 // const [busy, setBusy] = useState(false);
 // const [error, setError] = useState("");
 // const [Auth, setAuthentication] = useState(null);
 // const [messages, setMessages] = useState([]);
 // const [question, setQuestion] = useState("");
 // const [busy, setBusy] = useState(false);
 // const [error, setError] = useState("");
 // const [Auth, setAuthentication] = useState(null);
  async function send() {
    if (!question.trim() || !documentId) return;
    setError("");
    setBusy(true);
    const q = question.trim();
    setQuestion("");
    setMessages((m) => [...m, { role: "user", content: q }]);

    try {
      const res = await apiFetch("/chat/ask/", {
        method: "POST",
        body: { document_id: documentId, question: q }
      });
      setMessages((m) => [...m, { role: "assistant", content: res.answer }]);
    } catch (e) {
      setError(e.message || "Chat failed");
      setMessages((m) => [
        ...m,
        { role: "assistant", content: "Sorry, I ran into an error. Try again." }
      ]);
    } finally {
      setBusy(false);
    }
  }
  return (
    <div className="card chat">
      <div className="chatHeader">Chat about your file</div>
      <div className="chatBody">
        {messages.length === 0 ? (
          <div className="hint">Ask a question like “Explain this document” or “What is the main idea?”</div>
        ) : null}
        {messages.map((m, idx) => (
          <div key={idx} className={`msg ${m.role}`}>
            <div className="role">{m.role === "user" ? "You" : "AI"}</div>
            <div className="content">{m.content}</div>
          </div>
        ))}
      </div>

      <div className="chatFooter">
        {error ? <div className="error">{error}</div> : null}
        <div className="chatInputRow">
          <input
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="Type your question..."
            disabled={busy}
            onKeyDown={(e) => {
              if (e.key === "Enter") send();
            }}
          />
          <button disabled={busy || !question.trim()} onClick={send} type="button">
            {busy ? "Thinking..." : "Send"}
          </button>
        </div>
      </div>
    </div>
  );
}


export default function App() {
  const [loading, setLoading] = useState(true);
  const [me, setMe] = useState(null);
  const [authError, setAuthError] = useState("");
  const { value } = useToggle();

  

  async function loadMe() {
    try {
      setAuthError("");
      const token = getAccessToken();
      if (!token) {
        setMe(null);
        return;
      }
      const data = await apiFetch("/me/");
      setMe(data);
    } catch (e) {
      clearAccessToken();
      setMe(null);
      setAuthError(e.message || "Not authenticated");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadMe();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  if (loading) {
    return (
      <div className="container">
        <div className="card">Loading...</div>
      </div>
    );
  }
    if(!value){
      return <Home />;
    }
    if(!me && value){
      return <Register onAuthed={loadMe}  me={me} loadMe={loadMe}/>;
    }
 if (!me?.has_access && value) {
        return <PaymentGate onPaid={loadMe} />;
       }
 
  if(me?.has_access && value) return <Dashboard me={me} onMeUpdated={setMe} />;
 return(
 <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/register" element={(<Register onAuthed={loadMe}  me={me} loadMe={loadMe}/>)} />
     </Routes>
 ) 
  //if (!me) {
  //  return <Home/>;
  //}

  //if (!me?.has_access) {
  //  return <PaymentGate onPaid={loadMe} />;
  //}
  //if (!me) {
  //  return <Home/>;
  //}

  //if (!me?.has_access) {
  //  return <PaymentGate onPaid={loadMe} />;
  //}
  //if (!me) {
  //  return <Home/>;
  //}

  //if (!me?.has_access) {
  //  return <PaymentGate onPaid={loadMe} />;
  //}


  

}


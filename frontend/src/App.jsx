import React, { useEffect, useMemo, useState } from "react";
import { apiFetch, clearAccessToken, getAccessToken, setAccessToken } from "./api";

function LoginRegister({ onAuthed }) {
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
    <div className="container">
      <h1>NotebookLM-like</h1>
      <div className="card">
        <div className="tabs">
          <button
            className={mode === "login" ? "active" : ""}
            onClick={() => setMode("login")}
            type="button"
          >
            Login
          </button>
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

function PaymentGate({ onPaid }) {
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

function FunModeToggle({ funMode, onChange }) {
  return (
    <label className="toggle">
      <input type="checkbox" checked={funMode} onChange={(e) => onChange(e.target.checked)} />
      <span>Fun Mode</span>
    </label>
  );
}

function ChatBox({ documentId }) {
  const [messages, setMessages] = useState([]);
  const [question, setQuestion] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

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

function Dashboard({ me, onMeUpdated }) {
  const [funMode, setFunMode] = useState(Boolean(me.fun_mode));
  const [docs, setDocs] = useState([]);
  const [activeDocId, setActiveDocId] = useState(null);
  const [uploadBusy, setUploadBusy] = useState(false);
  const [uploadError, setUploadError] = useState("");

  async function refreshDocs() {
    const data = await apiFetch("/documents/");
    setDocs(data.documents || []);
    if (!activeDocId && (data.documents || []).length > 0) {
      setActiveDocId(data.documents[0].id);
    }
  }

  async function refreshMe() {
    const data = await apiFetch("/me/");
    onMeUpdated?.(data);
    setFunMode(Boolean(data.fun_mode));
  }

  useEffect(() => {
    refreshDocs().catch(() => {});
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function onToggleFun(nextFun) {
    setFunMode(nextFun);
    await apiFetch("/me/preferences/", { method: "PATCH", body: { fun_mode: nextFun } });
    await refreshMe();
  }

  async function uploadFile(file) {
    if (!file) return;
    setUploadBusy(true);
    setUploadError("");
    try {
      const fd = new FormData();
      fd.append("file", file);
      await apiFetch("/documents/upload/", { method: "POST", body: fd });
      await refreshDocs();
    } catch (e) {
      setUploadError(e.message || "Upload failed");
    } finally {
      setUploadBusy(false);
    }
  }

  const activeDoc = useMemo(() => docs.find((d) => d.id === activeDocId), [docs, activeDocId]);

  return (
    <div className="container">
      <div className="topBar">
        <div>
          <h1>Dashboard</h1>
          <div className="sub">Chat over your uploaded file</div>
        </div>
        <FunModeToggle
          funMode={funMode}
          onChange={(next) => {
            onToggleFun(next).catch(() => {});
          }}
        />
      </div>

      <div className="grid2">
        <div className="card">
          <div className="cardHeader">Upload</div>
          <input
            type="file"
            accept=".pdf,.txt,.docx,application/pdf,application/msword,application/vnd.openxmlformats-officedocument.wordprocessingml.document,text/plain"
            disabled={uploadBusy}
            onChange={(e) => uploadFile(e.target.files?.[0])}
          />
          {uploadError ? <div className="error">{uploadError}</div> : null}
          {uploadBusy ? <div className="hint">Processing... (this can take a moment)</div> : null}

          <div className="cardHeader" style={{ marginTop: 16 }}>
            Documents
          </div>

          {docs.length === 0 ? (
            <div className="hint">No documents uploaded yet.</div>
          ) : (
            <div className="docList">
              {docs.map((d) => (
                <button
                  key={d.id}
                  type="button"
                  className={`doc ${d.id === activeDocId ? "active" : ""}`}
                  onClick={() => setActiveDocId(d.id)}
                >
                  <div className="docName">{d.original_filename}</div>
                  <div className="docMeta">{d.processing_status}</div>
                </button>
              ))}
            </div>
          )}
        </div>

        <div>
          <div className="docSelected card">
            <div className="cardHeader">Active file</div>
            {activeDoc ? (
              <div>
                <div className="docName">{activeDoc.original_filename}</div>
                <div className="docMeta">{activeDoc.processing_status}</div>
              </div>
            ) : (
              <div className="hint">Upload a file to start.</div>
            )}
          </div>

          <ChatBox documentId={activeDocId} key={activeDocId || "none"} />
        </div>
      </div>
    </div>
  );
}

export default function App() {
  const [loading, setLoading] = useState(true);
  const [me, setMe] = useState(null);
  const [authError, setAuthError] = useState("");

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

  if (!me) {
    return <LoginRegister onAuthed={loadMe} />;
  }

  if (!me.has_access) {
    return <PaymentGate onPaid={loadMe} />;
  }

  return <Dashboard me={me} onMeUpdated={setMe} />;
}


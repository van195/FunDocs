import { useEffect, useMemo, useState } from "react";
import { FunModeToggle,ChatBox } from "../../App";
import { apiFetch } from "../../api";
import AttachFileOutlinedIcon from '@mui/icons-material/AttachFileOutlined';

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
    <div className="container-dashbord">
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
        <div className="card-dashbord">
          <div className="cardHeader">Upload</div>
          <div className="uploadContainer">
              <label className="Fileupload-bUtton" for ="fileInput"><AttachFileOutlinedIcon 
           
            /> Upload files</label>
          <input
            type="file"  id="fileInput"
            accept=".pdf,.txt,.docx,application/pdf,application/msword,application/vnd.openxmlformats-officedocument.wordprocessingml.document,text/plain"
            disabled={uploadBusy}
            onChange={(e) => uploadFile(e.target.files?.[0])}
          />
          </div>
           
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
export default Dashboard;
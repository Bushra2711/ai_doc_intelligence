import { useState, useEffect } from "react";
import UploadDocument from "../components/UploadDocument";
import { api, friendlyError } from "../services/api";
import type { DocumentRecord } from "../services/api";

type Props = { token: string; documents: DocumentRecord[]; loading: boolean; error: string; onRefresh: () => void; onLogout: () => void };

export default function Dashboard({ token, documents, loading, error, onRefresh, onLogout }: Props) {
  const [selected, setSelected] = useState<DocumentRecord | null>(null);
  const [busy, setBusy] = useState(""); const [actionError, setActionError] = useState("");
  const completed = documents.filter(d => d.status === "completed").length;
  const processing = documents.filter(d => d.status === "processing").length;
  const failed = documents.filter(d => d.status === "failed").length;
  const pending = documents.filter(d => d.status === "uploaded" || d.status === "pending").length;
  async function run(action: "process" | "analyze" | "delete", doc: DocumentRecord) {
    if (action === "delete" && !window.confirm(`Delete ${doc.filename}?`)) return;
    setBusy(`${action}-${doc.id}`); setActionError("");
    try { if (action === "process") await api.process(doc.id, token); if (action === "analyze") await api.analyze(doc.id, token); if (action === "delete") await api.remove(doc.id, token); await onRefresh(); if (selected?.id === doc.id && action === "delete") setSelected(null); }
    catch (err) { setActionError(friendlyError(err)); } finally { setBusy(""); }
  }

  return <div className="app-shell"><aside className="sidebar"><div className="logo-lockup"><div className="brand-mark small">D</div><div><strong>DOCUMIND</strong><span>AI PLATFORM</span></div></div><nav><a className="active">⌂ <span>Overview</span></a><a>▣ <span>Documents</span></a><a>◈ <span>AI Processing</span></a><a>◌ <span>Audit logs</span></a></nav><div className="sidebar-foot"><span className="online-dot" /> System operational<button onClick={onLogout}>Sign out</button></div></aside><main className="workspace"><header className="topbar"><div><p className="eyebrow">WORKSPACE / OVERVIEW</p><h1>Good morning, welcome back</h1></div><div className="user-chip"><span>U</span><div><strong>Workspace user</strong><small>Employee account</small></div><button onClick={onLogout}>Logout</button></div></header><div className="content"><div className="hero-row"><div><p className="eyebrow cyan">INTELLIGENT DOCUMENT OPERATIONS</p><h2>Your document command center</h2><p className="muted">Ingest, understand, and act on your business content.</p></div><div className="hero-pulse"><span className="pulse-dot" /> AI services ready</div></div>{(error || actionError) && <div className="alert wide">{error || actionError}</div>}<section className="metric-grid"><Metric label="Total documents" value={documents.length} tone="blue" /><Metric label="Completed" value={completed} tone="green" /><Metric label="In progress" value={processing} tone="amber" /><Metric label="Needs attention" value={failed} tone="red" /></section><div className="main-grid"><UploadDocument token={token} onUploaded={() => onRefresh()} /><section className="panel"><div className="panel-heading"><div><p className="eyebrow">LIVE WORKSPACE</p><h3>Recent documents</h3></div><span className="count-pill">{documents.length} total</span></div>{loading ? <div className="empty-state"><span className="spinner" />Loading workspace data...</div> : documents.length === 0 ? <div className="empty-state"><div className="empty-icon">□</div><strong>No documents yet</strong><span>Upload a document to start your intelligence workflow.</span></div> : <div className="document-list">{documents.map(doc => <DocumentRow key={doc.id} doc={doc} busy={busy} onAction={run} onView={setSelected} />)}</div>}</section></div><section className="pipeline panel"><div><p className="eyebrow">PROCESSING PIPELINE</p><h3>From file to insight</h3></div><div className="pipeline-steps">{["Upload", "Extract", "Analyze", "Understand", "Act"].map((step, index) => <div className="pipeline-step" key={step}><span>{String(index + 1).padStart(2, "0")}</span><strong>{step}</strong>{index < 4 && <i />}</div>)}</div><small>{pending} document{pending === 1 ? "" : "s"} ready for processing</small></section></div></main>{selected && <Detail doc={selected} token={token} onClose={() => setSelected(null)} />}</div>;
}

function Metric({ label, value, tone }: { label: string; value: number; tone: string }) { return <div className={`metric-card ${tone}`}><span>{label}</span><strong>{value}</strong><small>Live workspace count</small></div>; }

function DocumentRow({ doc, busy, onAction, onView }: { doc: DocumentRecord; busy: string; onAction: (action: "process" | "analyze" | "delete", doc: DocumentRecord) => void; onView: (doc: DocumentRecord) => void }) { const canProcess = doc.status === "uploaded" || doc.status === "pending" || doc.status === "failed"; const canAnalyze = doc.status === "completed"; return <div className="document-row"><div className="file-icon">{doc.file_type.includes("pdf") ? "PDF" : doc.file_type.includes("word") ? "DOC" : "IMG"}</div><div className="doc-main"><strong title={doc.filename}>{doc.filename}</strong><small>{formatBytes(doc.file_size)} · {new Date(doc.created_at).toLocaleDateString()}</small></div><span className={`status ${doc.status}`}><i />{doc.status}</span><div className="row-actions"><button onClick={() => onView(doc)}>View</button>{canProcess && <button disabled={!!busy} onClick={() => onAction("process", doc)}>{busy === `process-${doc.id}` ? "..." : "Process"}</button>}{canAnalyze && <button className="accent" disabled={!!busy} onClick={() => onAction("analyze", doc)}>{busy === `analyze-${doc.id}` ? "..." : "Analyze"}</button>}<button className="danger" disabled={!!busy} onClick={() => onAction("delete", doc)}>Delete</button></div></div>; }

function Detail({
  doc,
  token,
  onClose,
}: {
  doc: DocumentRecord;
  token: string;
  onClose: () => void;
}) {
  const [text, setText] = useState<string | null>(null);
  const [analysis, setAnalysis] =
    useState<Awaited<ReturnType<typeof api.analysis>> | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const load = async () => {
    setLoading(true);
    setError("");

    try {
      const [textResult, analysisResult] = await Promise.allSettled([
        api.text(doc.id, token),
        api.analysis(doc.id, token),
      ]);

      if (textResult.status === "fulfilled") {
        setText(textResult.value.extracted_text);
      } else {
        setError(
          "Could not load extracted text. Process the document first."
        );
      }

      if (analysisResult.status === "fulfilled") {
        setAnalysis(analysisResult.value);
      }
    } catch (err) {
      setError(friendlyError(err));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (doc.status === "completed" || doc.status === "processing") {
      void load();
    }
  }, [doc.id, doc.status, token]);

  return (
    <div className="modal-backdrop">
      <section className="detail-modal">
        <button className="close-button" onClick={onClose}>
          ×
        </button>

        <p className="eyebrow cyan">DOCUMENT DETAIL</p>

        <h2>{doc.filename}</h2>

        <div className="detail-meta">
          <span className={`status ${doc.status}`}>
            <i />
            {doc.status}
          </span>

          <span>{doc.file_type}</span>
          <span>{formatBytes(doc.file_size)}</span>

          <span className="uploaded-date">
            {new Date(doc.created_at).toLocaleDateString()}{" "}
            {new Date(doc.created_at).toLocaleTimeString()}
          </span>
        </div>

        {doc.status === "uploaded" && (
          <div className="alert info">
            ⓘ Process this document to extract text and generate AI analysis.
          </div>
        )}

        {doc.status === "failed" && (
          <div className="alert error">
            ⚠ This document failed to process. Please try again or upload a
            different file.
          </div>
        )}

        {!text &&
          !analysis &&
          !error &&
          doc.status === "completed" && (
            <button
              className="secondary-button"
              disabled={loading}
              onClick={() => void load()}
            >
              {loading ? "Loading..." : "Load extracted intelligence"}
            </button>
          )}

        {error && <div className="alert">{error}</div>}

        {text && (
          <div className="detail-section">
            <h3>Extracted text</h3>
            <pre>{text}</pre>
          </div>
        )}

        {analysis && (
  <div className="detail-section">
    <h3>
      AI analysis{" "}
      <span className="type-badge">
        {analysis.document_type}
      </span>
    </h3>

    {/* Invoice */}
    {analysis.document_type === "Invoice" && (
      <div className="extracted-fields">
        <h4>Extracted Fields</h4>

        <div className="field-grid">
          <div className="field-item">
            <span>Invoice Number</span>
            <strong>{analysis.invoice_number || "N/A"}</strong>
          </div>

          <div className="field-item">
            <span>Vendor</span>
            <strong>{analysis.vendor || "N/A"}</strong>
          </div>

          <div className="field-item">
            <span>Invoice Date</span>
            <strong>{analysis.invoice_date || "N/A"}</strong>
          </div>

          <div className="field-item">
            <span>Total Amount</span>
            <strong>{analysis.total_amount || "N/A"}</strong>
          </div>

          <div className="field-item">
            <span>GST</span>
            <strong>{analysis.gst || "N/A"}</strong>
          </div>
        </div>
      </div>
    )}

    {/* Resume / Bio-Data */}
    {analysis.document_type === "Resume" && (
      <div className="extracted-fields">
        <h4>Extracted Fields</h4>

        <div className="field-grid">
          <div className="field-item">
            <span>Full Name</span>
            <strong>{analysis.full_name || "N/A"}</strong>
          </div>

          <div className="field-item">
            <span>Date of Birth</span>
            <strong>{analysis.date_of_birth || "N/A"}</strong>
          </div>

          <div className="field-item">
            <span>Email</span>
            <strong>{analysis.email || "N/A"}</strong>
          </div>

          <div className="field-item">
            <span>Phone</span>
            <strong>{analysis.phone || "N/A"}</strong>
          </div>

          <div className="field-item">
            <span>Education</span>
            <strong>{analysis.education || "N/A"}</strong>
          </div>

          <div className="field-item">
            <span>Skills</span>
            <strong>{analysis.skills || "N/A"}</strong>
          </div>

          <div className="field-item">
            <span>Experience</span>
            <strong>{analysis.experience || "N/A"}</strong>
          </div>

          <div className="field-item">
            <span>Height</span>
            <strong>{analysis.height || "N/A"}</strong>
          </div>

          <div className="field-item">
            <span>Father Name</span>
            <strong>{analysis.father_name || "N/A"}</strong>
          </div>

          <div className="field-item">
            <span>Father Occupation</span>
            <strong>{analysis.father_occupation || "N/A"}</strong>
          </div>

          <div className="field-item">
            <span>Mother Occupation</span>
            <strong>{analysis.mother_occupation || "N/A"}</strong>
          </div>

          <div className="field-item">
            <span>Siblings</span>
            <strong>{analysis.siblings || "N/A"}</strong>
          </div>
        </div>
      </div>
    )}

    <h4>Summary</h4>
    <p>{analysis.summary}</p>

    <h4>Key points</h4>
    <pre>{analysis.key_points}</pre>

    <h4>Important information</h4>
    <pre>{analysis.important_information}</pre>
  </div>
)}
      </section>
    </div>
  );
}

function formatBytes(bytes: number) { if (!bytes) return "0 B"; const units = ["B", "KB", "MB"]; const index = Math.min(Math.floor(Math.log(bytes) / Math.log(1024)), units.length - 1); return `${(bytes / 1024 ** index).toFixed(index ? 1 : 0)} ${units[index]}`; }

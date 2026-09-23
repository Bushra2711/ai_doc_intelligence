import { useEffect, useState } from "react";
import UploadDocument from "./UploadDocument";
import type { DashboardMetrics, DocumentRecord } from "../services/api";

type Props = {
  token: string;
  userName: string;
  documents: DocumentRecord[];
  metrics: DashboardMetrics | null;
  completed: number;
  processing: number;
  failed: number;
  error: string;
  onRefresh: () => void;
  onView: (doc: DocumentRecord) => void;
};

export default function OverviewDashboard({ token, userName, documents, metrics, completed, processing, failed, error, onRefresh, onView }: Props) {
  const [recent, setRecent] = useState<DocumentRecord[]>(documents.slice(0, 5));

  useEffect(() => setRecent(documents.slice(0, 5)), [documents]);

  const typeEntries = Object.entries(metrics?.document_types || {}).sort((a, b) => b[1] - a[1]);
  const totalTypes = typeEntries.reduce((sum, item) => sum + item[1], 0) || documents.length || 1;
  const invoiceOnly = !!metrics && metrics.invoice_documents === documents.length && documents.length > 0;
  const confidence = metrics?.average_invoice_confidence == null ? "—" : Math.round(metrics.average_invoice_confidence * 100) + "%";

  const donut = typeEntries.length
    ? typeEntries.map((item, index) => {
        const colors = ["#258cf4", "#16b887", "#f39a22", "#8456e8", "#e65a8a"];
        const start = typeEntries.slice(0, index).reduce((sum, entry) => sum + entry[1], 0) / totalTypes * 360;
        const end = start + item[1] / totalTypes * 360;
        return colors[index % colors.length] + " " + start + "deg " + end + "deg";
      }).join(", ")
    : "#e7eef0 0deg 360deg";

  function workflow(stage: "process" | "analyze" | "view") {
    const target = recent[0];
    if (!target) return;
    window.dispatchEvent(new CustomEvent(stage === "view" ? "documind:view" : "documind:" + stage, { detail: target.id }));
  }

  function openDocuments() {
    document.querySelector<HTMLButtonElement>(".side-nav-item:nth-child(2)")?.click();
  }

  return <>
    <section className="overview-welcome">
      <div>
        <p className="eyebrow overview-eyebrow">WELCOME BACK, {((userName || "User").split(" ")[0] || "User").toUpperCase()}! <span>👋</span></p>
        <h2>AI-Powered Intelligent Document Processing</h2>
        <p>Ingest. Understand. Automate. Turn documents into actionable insights.</p>
      </div>
      <div className="welcome-visual">
        <div className="doc-stack"><span>PDF</span><span>DOCX</span></div>
        <div className="flow-arrow">→</div>
        <div className="structured-box"><strong>Structured Data</strong><small>• Invoice Details</small><small>• Line Items</small><small>• Compliance Check</small><small>• Analytics</small></div>
      </div>
    </section>

    {error && <div className="alert wide">{error}</div>}

    <section className="overview-kpis">
      <OverviewKpi icon="▤" label="Total Documents" value={documents.length} hint="Live workspace count" tone="blue" />
      <OverviewKpi icon="✓" label="Completed" value={completed} hint="Successfully processed" tone="green" />
      <OverviewKpi icon="◷" label="In Progress" value={processing} hint="Currently processing" tone="indigo" />
      <OverviewKpi icon="!" label="Needs Attention" value={failed} hint="Requires review" tone="red" />
      <OverviewKpi icon="✦" label="Avg. Confidence" value={confidence} hint="Extraction quality" tone="purple" />
    </section>

    <section className="overview-command-grid">
      <div className="overview-upload-wrap">
        <div className="overview-section-title"><span className="section-icon">↥</span><div><h3>Upload Document</h3><small>Select a file to start the intelligence workflow.</small></div><span className="info-dot">i</span></div>
        <div className="overview-upload"><UploadDocument token={token} onUploaded={() => onRefresh()} /></div>
      </div>

      <div className="overview-workflow">
        <div className="overview-section-title"><span className="section-icon">✣</span><div><h3>Document Processing Workflow</h3><small>Move from upload to validated results.</small></div></div>
        <div className="workflow-line">
          {[["↥","Upload","Add document"],["⚙","Process","Run OCR"],["▣","Analyze","Extract data"],["✓","Validate","Check compliance"],["◉","View","Results & Report"]].map(([icon,title,desc], index) =>
            <div className={"workflow-node " + (index === 0 ? "done" : index === 1 && processing ? "active" : "")} key={title}>
              <span>{icon}</span><strong>{title}</strong><small>{desc}</small>{index < 4 && <i>→</i>}
            </div>
          )}
        </div>
        <div className="workflow-buttons">
          <button className="workflow-btn blue" disabled={!recent.length || (recent[0].status !== "uploaded" && recent[0].status !== "pending" && recent[0].status !== "failed")} onClick={() => workflow("process")}>▷&nbsp; Process</button>
          <button className="workflow-btn purple" disabled={!recent.length || recent[0].status !== "completed"} onClick={() => workflow("analyze")}>▥&nbsp; Analyze</button>
          <button className="workflow-btn muted-btn" disabled={!recent.length} onClick={() => workflow("view")}>◉&nbsp; View Results</button>
        </div>
      </div>
    </section>

    <section className="overview-bottom-grid">
      <div className="overview-panel recent-panel">
        <div className="overview-panel-head">
          <div><span className="mini-label">LIVE WORKSPACE</span><h3>Recent Documents</h3><p>Your latest files and processing status.</p></div>
          <button onClick={openDocuments}>View All →</button>
        </div>
        {recent.length === 0 ? <div className="overview-empty">No documents yet. Upload your first document to begin.</div> : <div className="overview-table">
          <div className="overview-table-head"><span>#</span><span>Document Name</span><span>Type</span><span>Size</span><span>Status</span><span>Confidence</span><span>Actions</span></div>
          {recent.map((doc, index) => <div className="overview-table-row" key={doc.id}>
            <span>{index + 1}</span><strong title={doc.filename}>{doc.filename}</strong><span>{invoiceOnly ? "Invoice" : "Document"}</span><span>{formatBytes(doc.file_size)}</span>
            <span className={"overview-status " + doc.status}>● {doc.status === "completed" ? "Completed" : doc.status}</span>
            <span>{doc.status === "completed" ? confidence : "—"}</span><button onClick={() => onView(doc)}>◉&nbsp; View</button>
          </div>)}
        </div>}
      </div>

      <div className="overview-panel distribution-panel">
        <div className="overview-panel-head">
          <div><span className="mini-label">DOCUMENT MIX</span><h3>Document Type Distribution</h3></div>
          <select defaultValue="all" aria-label="Distribution range"><option value="all">All Time</option><option value="30">Last 30 Days</option></select>
        </div>
        <div className="donut-wrap">
          <div className="donut" style={{ background: "conic-gradient(" + donut + ")" }}><div><strong>{documents.length}</strong><span>Documents</span></div></div>
          <div className="donut-legend">{typeEntries.length ? typeEntries.map((item, i) => <div key={item[0]}><span className={"legend-dot dot-" + (i % 5)} /><b>{item[0]}</b><strong>{item[1]} ({Math.round(item[1] / totalTypes * 100)}%)</strong></div>) : <div><span className="legend-dot dot-0" /><b>Documents</b><strong>{documents.length}</strong></div>}</div>
        </div>
      </div>
    </section>
  </>;
}

function OverviewKpi({ icon, label, value, hint, tone }: { icon: string; label: string; value: string | number; hint: string; tone: string }) {
  return <div className={"overview-kpi " + tone}><span className="kpi-icon">{icon}</span><div><small>{label}</small><strong>{value}</strong><em>{hint}</em></div></div>;
}

function formatBytes(bytes: number) {
  if (bytes < 1024) return bytes + " B";
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + " KB";
  return (bytes / (1024 * 1024)).toFixed(1) + " MB";
}

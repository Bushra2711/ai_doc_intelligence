import { DragEvent, useEffect, useRef, useState } from "react";
import { api, DocumentRecord, friendlyError } from "../services/api";

type UploadDocumentProps = { token: string; onUploaded: (document: DocumentRecord) => void };

function UploadDocument({ token, onUploaded }: UploadDocumentProps) {
  const [uploadedDocument, setUploadedDocument] = useState<DocumentRecord | null>(null);
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [stage, setStage] = useState<"upload" | "process" | "analyze" | "view">("upload");
  const inputRef = useRef<HTMLInputElement>(null);

  function choose(next: File | undefined) {
    if (!next) return;
    setError(""); setMessage("");
    if (next.size > 10 * 1024 * 1024) { setFile(null); setError("This file is larger than the 10 MB limit."); return; }
    setFile(next);
  }

  useEffect(() => {
    const handleWorkflow = (event: Event) => {
      const next = (event as CustomEvent<{ id: string; stage: "process" | "analyze" | "view" }>).detail;
      if (uploadedDocument?.id === next?.id) setStage(next.stage);
    };
    window.addEventListener("documind:workflow", handleWorkflow);
    return () => window.removeEventListener("documind:workflow", handleWorkflow);
  }, [uploadedDocument]);

  function onDrop(event: DragEvent<HTMLDivElement>) {
    event.preventDefault();
    choose(event.dataTransfer.files?.[0]);
  }

  async function uploadDocument() {
    if (!file) { setError("Please select a document first."); return; }
    setLoading(true); setError(""); setMessage("");
    try {
      const data = await api.upload(file, token);
      setUploadedDocument(data);
      onUploaded(data); setFile(null); if (inputRef.current) inputRef.current.value = ""; setMessage("Document uploaded successfully!");
    } catch (err) { setError(friendlyError(err)); }
    finally { setLoading(false); }
  }

  return (
    <div className="upload-panel panel">
      <div className="upload-reference-icon">⇧</div>
      <h2>Upload Document</h2>
      <div className="upload-dropzone" onDragOver={(e) => e.preventDefault()} onDrop={onDrop} onClick={() => inputRef.current?.click()}>
        <span className="upload-prompt">Drag &amp; drop your file here, or click below to select</span>
        <span className="upload-cloud">⇧</span>
        <strong>{file ? file.name : "Choose File"}</strong>
        {file && <small>{(file.size / 1024 / 1024).toFixed(2)} MB</small>}
        <input ref={inputRef} type="file" accept=".pdf,.docx,.png,.jpg,.jpeg,.gif,.webp" onChange={(e) => choose(e.target.files?.[0])} />
      </div>
      <div className="upload-actions">
        <button type="button" onClick={uploadDocument} disabled={!file || loading || !!uploadedDocument} className="primary-button upload-button">{loading ? "Uploading..." : uploadedDocument ? "Uploaded" : "Upload Document"}</button>
      </div>
      <div className="document-action-steps workflow-steps" aria-label="Document workflow steps">
        <button type="button" className={stage === "process" ? "active-step" : ""} disabled={!uploadedDocument || stage !== "process"} onClick={() => { if (uploadedDocument) window.dispatchEvent(new CustomEvent("documind:process", { detail: uploadedDocument.id })); }}>2. Process</button>
        <button type="button" className={stage === "analyze" ? "active-step" : ""} disabled={!uploadedDocument || stage !== "analyze"} onClick={() => { if (uploadedDocument) window.dispatchEvent(new CustomEvent("documind:analyze", { detail: uploadedDocument.id })); }}>3. Analyze</button>
        <button type="button" className={stage === "view" ? "active-step" : ""} disabled={!uploadedDocument || stage !== "view"} onClick={() => { if (uploadedDocument) window.dispatchEvent(new CustomEvent("documind:view", { detail: uploadedDocument.id })); }}>4. View</button>
      </div>
      <small className="upload-help">Supported formats: PDF, DOCX, JPG, PNG, GIF, WEBP&nbsp; | &nbsp;Max size: 10 MB</small>
      {message && <p className="upload-success">{message}</p>}
      {error && <p className="upload-error">{error}</p>}
    </div>
  );
}
export default UploadDocument;

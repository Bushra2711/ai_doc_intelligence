import { DragEvent, useRef, useState } from "react";
import { api, DocumentRecord, friendlyError } from "../services/api";

type UploadDocumentProps = { token: string; onUploaded: (document: DocumentRecord) => void };

function UploadDocument({ token, onUploaded }: UploadDocumentProps) {
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const inputRef = useRef<HTMLInputElement>(null);

  function choose(next: File | undefined) {
    if (!next) return;
    setError(""); setMessage("");
    if (next.size > 10 * 1024 * 1024) { setFile(null); setError("This file is larger than the 10 MB limit."); return; }
    setFile(next);
  }

  function onDrop(event: DragEvent<HTMLDivElement>) {
    event.preventDefault();
    choose(event.dataTransfer.files?.[0]);
  }

  async function uploadDocument() {
    if (!file) { setError("Please select a document first."); return; }
    setLoading(true); setError(""); setMessage("");
    try {
      const data = await api.upload(file, token);
      onUploaded(data); setFile(null); if (inputRef.current) inputRef.current.value = ""; setMessage("Document uploaded successfully!");
    } catch (err) { setError(friendlyError(err)); }
    finally { setLoading(false); }
  }

  return (
    <div className="upload-panel panel">
      <div className="upload-reference-icon">⇧</div>
      <h2>Upload a document</h2>
      <p>Drag and drop your file here, or choose a file to upload</p>
      <div className="upload-dropzone" onDragOver={(e) => e.preventDefault()} onDrop={onDrop} onClick={() => inputRef.current?.click()}>
        <span className="upload-cloud">⇧</span>
        <strong>{file ? file.name : "Choose File"}</strong>
        {file && <small>{(file.size / 1024 / 1024).toFixed(2)} MB</small>}
        <input ref={inputRef} type="file" accept=".pdf,.docx,.png,.jpg,.jpeg,.gif,.webp" onChange={(e) => choose(e.target.files?.[0])} />
      </div>
      <button type="button" onClick={uploadDocument} disabled={!file || loading} className="primary-button upload-button">{loading ? "Uploading securely..." : "Upload document"}</button>
      <small className="upload-help">Supported formats: PDF, DOCX, JPG, PNG, GIF, WEBP&nbsp; | &nbsp;Max size: 10 MB</small>
      {message && <p className="upload-success">{message}</p>}
      {error && <p className="upload-error">{error}</p>}
    </div>
  );
}
export default UploadDocument;

import { useState } from "react";
import { api, DocumentRecord, friendlyError } from "../src/services/api";

type UploadDocumentProps = {
  token: string;
  onUploaded: (document: DocumentRecord) => void;
};

function UploadDocument({
  token,
  onUploaded,
}: UploadDocumentProps) {
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  async function uploadDocument() {
    if (!file) {
      setError("Please select a document first.");
      return;
    }

    setLoading(true);
    setError("");
    setMessage("");

    try {
      if (file.size > 10 * 1024 * 1024) throw new Error("This file is larger than the 10 MB limit.");
      const data = await api.upload(file, token);
      onUploaded(data);

      setFile(null);
      setMessage("Document uploaded successfully!");
    } catch (err) {
      setError(friendlyError(err));
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="upload-panel panel">
      <div className="mb-5">
        <div className="upload-icon">↑</div>

        <h2 className="mt-3 text-xl font-semibold text-white">
          Ingest a document
        </h2>

        <p className="mt-2 text-sm text-slate-400">
          Add a document to your intelligence workspace.
        </p>
      </div>

      <input
        type="file"
        accept=".pdf,.docx,.png,.jpg,.jpeg,.gif,.webp"
        onChange={(e) =>
          setFile(e.target.files?.[0] || null)
        }
        className="file-picker"
      />

      {file && (
        <p
          className="selected-file"
          title={file.name}
        >
          {file.name} <small>{(file.size / 1024 / 1024).toFixed(2)} MB</small>
        </p>
      )}

      <button
        type="button"
        onClick={uploadDocument}
        disabled={!file || loading}
        className="primary-button upload-button"
      >
        {loading ? "Uploading securely..." : "Upload document"}
      </button>

      {message && (
        <p className="mt-4 rounded-lg bg-emerald-950 p-3 text-sm text-emerald-300">
          {message}
        </p>
      )}

      {error && (
        <p className="mt-4 rounded-lg bg-red-950 p-3 text-sm text-red-300">
          {error}
        </p>
      )}
    </div>
  );
}

export default UploadDocument;
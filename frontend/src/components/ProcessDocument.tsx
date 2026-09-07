import { useState } from "react";

type Document = {
  id: string;
  filename: string;
  status: string;
};

type ProcessDocumentProps = {
  token: string;
  document: Document;
  onProcessed: (document: Document) => void;
};

function ProcessDocument({
  token,
  document,
  onProcessed,
}: ProcessDocumentProps) {
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  async function processDocument() {
    setLoading(true);
    setError("");
    setMessage("");

    try {
      const response = await fetch(
        `http://127.0.0.1:8000/api/v1/documents/${document.id}/process`,
        {
          method: "POST",
          headers: {
            Authorization: `Bearer ${token}`,
            Accept: "application/json",
          },
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          typeof data?.detail === "string"
            ? data.detail
            : "Document processing failed."
        );
      }

      const updatedDocument = {
        ...document,
        status: data.status,
      };

      onProcessed(updatedDocument);
      setMessage("Document processed successfully!");
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Document processing failed."
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="rounded-xl border border-slate-800 bg-slate-900 p-5">
      <p className="text-sm font-medium text-white">
        {document.filename}
      </p>

      <p className="mt-1 text-xs text-slate-500">
        Status: {document.status}
      </p>

      <button
        type="button"
        onClick={processDocument}
        disabled={loading}
        className="mt-4 rounded-lg bg-indigo-500 px-4 py-2 text-sm font-semibold text-white transition hover:bg-indigo-400 disabled:cursor-not-allowed disabled:opacity-50"
      >
        {loading ? "Processing..." : "Process Document"}
      </button>

      {message && (
        <p className="mt-3 text-sm text-emerald-400">
          {message}
        </p>
      )}

      {error && (
        <p className="mt-3 text-sm text-red-400">
          {error}
        </p>
      )}
    </div>
  );
}

export default ProcessDocument;
import { useState } from "react";

type Document = {
  id: string;
  filename: string;
  status: string;
};

type AnalyzeDocumentProps = {
  token: string;
  document: Document;
  onAnalyzed: (analysis: unknown) => void;
};

function AnalyzeDocument({
  token,
  document,
  onAnalyzed,
}: AnalyzeDocumentProps) {
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  async function analyzeDocument() {
    setLoading(true);
    setError("");
    setMessage("");

    try {
      const response = await fetch(
        `http://127.0.0.1:8000/api/v1/documents/${document.id}/analyze`,
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
            : "AI analysis failed."
        );
      }

      onAnalyzed(data);
      setMessage("Gemini AI analysis completed successfully!");
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "AI analysis failed."
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="rounded-xl border border-slate-800 bg-slate-900 p-5">
      <p className="text-sm font-medium text-white">
        AI Analysis
      </p>

      <p className="mt-1 text-xs text-slate-500">
        Analyze: {document.filename}
      </p>

      <button
        type="button"
        onClick={analyzeDocument}
        disabled={loading}
        className="mt-4 rounded-lg bg-emerald-500 px-4 py-2 text-sm font-semibold text-slate-950 transition hover:bg-emerald-400 disabled:cursor-not-allowed disabled:opacity-50"
      >
        {loading ? "Analyzing..." : "Analyze with AI"}
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

export default AnalyzeDocument;
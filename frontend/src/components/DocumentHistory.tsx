import { useEffect, useState } from "react";

type Document = {
  id: string;
  filename: string;
  status: string;
};

type DocumentHistoryProps = {
  token: string;
};

function DocumentHistory({ token }: DocumentHistoryProps) {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  async function loadDocuments() {
    try {
      const response = await fetch(
        "http://127.0.0.1:8000/api/v1/documents",
        {
          method: "GET",
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
            : "Failed to load documents."
        );
      }

      setDocuments(data);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Failed to load documents."
      );
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
  loadDocuments();
}, []);

  if (loading) {
    return (
      <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6 text-slate-400">
        Loading documents...
      </div>
    );
  }

  if (error) {
    return (
      <div className="rounded-2xl border border-red-500/20 bg-slate-900 p-6 text-red-400">
        {error}
      </div>
    );
  }

  return (
    <div className="rounded-2xl border border-slate-800 bg-slate-900">
      <div className="border-b border-slate-800 px-6 py-5">
        <h2 className="font-semibold text-white">
          My Documents
        </h2>

        <p className="mt-1 text-sm text-slate-500">
          Document history and processing status
        </p>
      </div>

      {documents.length === 0 ? (
        <div className="p-10 text-center text-slate-500">
          No documents found.
        </div>
      ) : (
        <div className="divide-y divide-slate-800">
          {documents.map((doc) => (
            <div
              key={doc.id}
              className="flex items-center justify-between gap-4 px-6 py-4"
            >
              <div className="min-w-0">
                <p className="truncate text-sm font-medium text-white">
                  {doc.filename}
                </p>

                <p className="mt-1 text-xs text-slate-500">
                  ID: {doc.id.slice(0, 8)}
                </p>
              </div>

              <span className="rounded-full bg-slate-800 px-3 py-1 text-xs text-slate-300">
                {doc.status}
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default DocumentHistory;
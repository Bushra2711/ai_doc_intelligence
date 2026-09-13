import { useEffect, useState } from "react";
import { api, friendlyError } from "../services/api";
import type { AuditLog } from "../services/api";

type Props = { token: string };

export default function AuditTrail({ token }: Props) {
  const [logs, setLogs] = useState<AuditLog[]>([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let active = true;
    setLoading(true);
    api.auditLogs(token, undefined)
      .then((data) => { if (active) setLogs(data); })
      .catch((err) => { if (active) setError(friendlyError(err)); })
      .finally(() => { if (active) setLoading(false); });
    return () => { active = false; };
  }, [token]);

  return (
    <section className="audit-panel panel">
      <div className="panel-heading">
        <div><p className="eyebrow">GOVERNANCE</p><h3>Audit trail</h3><small className="audit-subtitle">Traceable record of workspace write actions.</small></div>
        <span className="count-pill">{logs.length} events</span>
      </div>
      {loading && <div className="empty-state audit-empty">Loading audit events...</div>}
      {error && <div className="alert error">Could not load audit trail: {error}</div>}
      {!loading && !error && logs.length === 0 && <div className="empty-state audit-empty">No write actions recorded yet. Upload, process, analyze, or delete a document to create an audit event.</div>}
      {!loading && !error && logs.length > 0 && (
        <div className="audit-list">
          {logs.map((log) => (
            <div className="audit-row" key={log.id}>
              <span className={`audit-status ${log.status.toLowerCase()}`}>{log.status}</span>
              <div className="audit-main"><strong>{log.action}</strong><small>{log.details || "Workspace action"}</small></div>
              <time>{new Date(log.created_at).toLocaleString()}</time>
            </div>
          ))}
        </div>
      )}
    </section>
  );
}

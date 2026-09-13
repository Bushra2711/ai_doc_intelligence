import { useEffect, useState } from "react";
import { api, friendlyError } from "../services/api";
import type { DashboardMetrics } from "../services/api";

type Props = { token: string };

export default function DashboardAnalytics({ token }: Props) {
  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    let active = true;
    void api.dashboardMetrics(token).then((result) => {
      if (active) setMetrics(result);
    }).catch((err) => {
      if (active) setError(friendlyError(err));
    });
    return () => { active = false; };
  }, [token]);

  if (error) return <section className="analytics-grid"><div className="panel analytics-panel"><p className="eyebrow">KPI ANALYTICS</p><h3>Dashboard analytics</h3><div className="alert error">{error}</div></div></section>;
  if (!metrics) return <section className="analytics-grid"><div className="panel analytics-panel"><p className="eyebrow">KPI ANALYTICS</p><h3>Dashboard analytics</h3><div className="empty-state"><span className="spinner" />Loading KPI analytics...</div></div></section>;

  const confidence = metrics.average_invoice_confidence == null ? "—" : `${Math.round(metrics.average_invoice_confidence * 100)}%`;
  const complianceTotal = metrics.compliance_passed + metrics.compliance_warnings + metrics.compliance_failed;
  const maxDaily = Math.max(...metrics.recent_daily_counts.map(item => item.count), 1);
  const typeEntries = Object.entries(metrics.document_types).sort((a, b) => b[1] - a[1]);

  return <section className="analytics-section">
    <div className="analytics-heading"><div><p className="eyebrow">KPI ANALYTICS</p><h3>Operational intelligence</h3><small>Live metrics from your document processing workspace.</small></div></div>
    <div className="analytics-grid">
      <Metric label="Invoices" value={metrics.invoice_documents} detail={`${metrics.analyzed_documents} analyzed documents`} />
      <Metric label="Avg. invoice confidence" value={confidence} detail="Explainable extraction quality" />
      <Metric label="Compliance passed" value={metrics.compliance_passed} detail={`${complianceTotal} total compliance checks`} />
      <Metric label="Compliance failed" value={metrics.compliance_failed} detail={`${metrics.compliance_warnings} warnings`} />
    </div>
    <div className="analytics-lower-grid">
      <div className="panel analytics-panel"><div className="panel-heading"><div><p className="eyebrow">PROCESSING TREND</p><h3>Documents · last 7 days</h3></div></div><div className="trend-chart">{metrics.recent_daily_counts.map(item => <div className="trend-column" key={item.date}><strong>{item.count}</strong><div className="trend-bar"><span style={{ height: `${Math.max((item.count / maxDaily) * 100, item.count ? 8 : 0)}%` }} /></div><small>{item.date.slice(5)}</small></div>)}</div></div>
      <div className="panel analytics-panel"><div className="panel-heading"><div><p className="eyebrow">DOCUMENT MIX</p><h3>Types processed</h3></div></div>{typeEntries.length === 0 ? <div className="empty-state">No analyzed document types yet.</div> : <div className="analytics-list">{typeEntries.map(([type, count]) => <div className="analytics-list-row" key={type}><span>{type}</span><strong>{count}</strong></div>)}</div>}</div>
    </div>
  </section>;
}

function Metric({ label, value, detail }: { label: string; value: string | number; detail: string }) { return <div className="analytics-kpi"><span>{label}</span><strong>{value}</strong><small>{detail}</small></div>; }

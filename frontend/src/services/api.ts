export const API_BASE_URL = (
  import.meta.env.VITE_API_URL || "http://127.0.0.1:8000"
).replace(/\/$/, "");
const API_PREFIX = `${API_BASE_URL}/api/v1`;

export type DocumentStatus = "uploaded" | "pending" | "processing" | "completed" | "failed";
export type DocumentRecord = { id: string; user_id: string; filename: string; file_path: string; file_type: string; file_size: number; status: DocumentStatus; created_at: string; updated_at: string };
export type TaxBreakdown = { tax_type: string; rate: number | null; amount: number | null };
export type InvoiceLineItem = { line_number: number | null; description: string | null; hsn_code: string | null; quantity: number | null; unit_price: number | null; amount: number | null };
export type InvoiceFields = { invoice_number: string | null; invoice_date: string | null; due_date: string | null; vendor_name: string | null; vendor_gstin: string | null; buyer_name: string | null; buyer_gstin: string | null; subtotal: number | null; tax_amount: number | null; total_amount: number | null; currency: string | null; po_number: string | null; tax_breakdown: TaxBreakdown[]; line_items: InvoiceLineItem[] };
export type InvoiceExtraction = { document_id: string; fields: InvoiceFields };
export type ComplianceCheck = { rule: string; status: string; message: string };
export type InvoiceCompliance = { document_id: string; overall_status: string; passed: number; warnings: number; failed: number; checks: ComplianceCheck[] };
export type ConfidenceField = { field: string; value: unknown; score: number; level: string; reason: string };
export type InvoiceConfidence = { document_id: string; overall_score: number; overall_level: string; fields: ConfidenceField[] };
export type Analysis = {
  id: string; document_id: string; document_type: string; summary: string; key_points: string; important_information: string;
  invoice_number: string | null; vendor: string | null; invoice_date: string | null; total_amount: string | null; gst: string | null;
  full_name: string | null; date_of_birth: string | null; education: string | null; skills: string | null; experience: string | null; email: string | null; phone: string | null; height: string | null; father_name: string | null; father_occupation: string | null; mother_occupation: string | null; siblings: string | null;
  company: string | null; effective_date: string | null; expiry_date: string | null; payment_terms: string | null; signatures: string | null;
  po_number: string | null; supplier: string | null; items: string | null; amount: string | null; delivery_date: string | null;
  receipt_number: string | null; receipt_date: string | null; receipt_items: string | null; receipt_amount: string | null; receipt_tax: string | null;
  policy_name: string | null; policy_number: string | null; policy_effective_date: string | null; policy_expiry_date: string | null; department: string | null;
  sender: string | null; receiver: string | null; subject: string | null; email_date: string | null; email_purpose: string | null;
  certificate_type: string | null; institution: string | null; issue_date: string | null; certificate_number: string | null;
  created_at: string; updated_at: string;
};
export type ExtractedText = { id: string; document_id: string; extracted_text: string; created_at: string; updated_at: string };
export class ApiError extends Error { status: number; constructor(message: string, status = 0) { super(message); this.status = status; } }
async function request<T>(path: string, options: RequestInit = {}, token?: string): Promise<T> {
  const headers = new Headers(options.headers); headers.set("Accept", "application/json"); if (token) headers.set("Authorization", `Bearer ${token}`); if (options.body && !(options.body instanceof FormData)) headers.set("Content-Type", "application/json");
  let response: Response; try { response = await fetch(`${API_PREFIX}${path}`, { ...options, headers }); } catch { throw new ApiError("Unable to connect to the server. Please make sure the backend is running."); }
  const data = await response.json().catch(() => null); if (!response.ok) { const detail = typeof data?.detail === "string" ? data.detail : "The request could not be completed."; if (response.status === 401) throw new ApiError("Your session has expired. Please sign in again.", 401); if (response.status === 413) throw new ApiError("This file is larger than the 10 MB limit.", 413); throw new ApiError(detail, response.status); } return data as T;
}
export const api = {
  login: (email: string, password: string) => request<{ access_token: string }>("/auth/login", { method: "POST", body: JSON.stringify({ email, password }) }),
  register: (full_name: string, email: string, password: string) => request("/auth/register", { method: "POST", body: JSON.stringify({ full_name, email, password }) }),
  documents: (token: string) => request<DocumentRecord[]>("/documents", {}, token),
  upload: (file: File, token: string) => { const body = new FormData(); body.append("file", file); return request<DocumentRecord>("/documents/upload", { method: "POST", body }, token); },
  process: (id: string, token: string) => request(`/documents/${id}/process`, { method: "POST" }, token),
  analyze: (id: string, token: string) => request<Analysis>(`/documents/${id}/analyze`, { method: "POST" }, token),
  text: (id: string, token: string) => request<ExtractedText>(`/documents/${id}/text`, {}, token),
  analysis: (id: string, token: string) => request<Analysis>(`/documents/${id}/analysis`, {}, token),
  invoiceExtraction: (id: string, token: string) => request<InvoiceExtraction>(`/documents/${id}/extract-invoice`, {}, token),
  invoiceCompliance: (id: string, token: string) => request<InvoiceCompliance>(`/documents/${id}/compliance`, {}, token),
  invoiceConfidence: (id: string, token: string) => request<InvoiceConfidence>(`/documents/${id}/confidence`, {}, token),
  remove: (id: string, token: string) => request<void>(`/documents/${id}`, { method: "DELETE" }, token),
};
export function friendlyError(error: unknown): string { return error instanceof ApiError ? error.message : "Something went wrong. Please try again."; }

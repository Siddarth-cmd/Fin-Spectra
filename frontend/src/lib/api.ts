/**
 * Fin-Spectra API Service Layer
 * All API calls centralized here. Env var: NEXT_PUBLIC_API_URL
 */

import {
  PipelineSummary,
  AlertsResponse,
  ClassifiedAlert,
  TransactionDetail,
  InvestigationResult,
  InvestigationCase,
  StartInvestigationRequest,
  StartInvestigationResponse,
} from "./types";

export const API_BASE =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

// ─── Helpers ────────────────────────────────────────────────────────────────

async function apiFetch<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(options?.headers || {}),
    },
  });

  if (!res.ok) {
    let message = `API error ${res.status}: ${res.statusText}`;
    try {
      const body = await res.json();
      message = body?.detail || message;
    } catch {}
    throw new Error(message);
  }

  return res.json() as Promise<T>;
}

// ─── Health ──────────────────────────────────────────────────────────────────

export async function checkHealth(): Promise<{ status: string; version: string; llm_mode: string }> {
  return apiFetch("/api/health");
}

// ─── Summary / Dashboard ─────────────────────────────────────────────────────

export async function fetchSummary(): Promise<PipelineSummary> {
  return apiFetch<PipelineSummary>("/api/summary");
}

// ─── Alerts ──────────────────────────────────────────────────────────────────

export async function fetchAlerts(params?: {
  risk_level?: string;
  search?: string;
  typology?: string;
  status?: string;
  page?: number;
  page_size?: number;
}): Promise<AlertsResponse> {
  const query = new URLSearchParams();
  if (params?.risk_level) query.set("risk_level", params.risk_level);
  if (params?.search) query.set("search", params.search);
  if (params?.typology) query.set("typology", params.typology);
  if (params?.status) query.set("status", params.status);
  if (params?.page) query.set("page", String(params.page));
  if (params?.page_size) query.set("page_size", String(params.page_size));

  const qs = query.toString();
  return apiFetch<AlertsResponse>(`/api/alerts${qs ? "?" + qs : ""}`);
}

export async function fetchAlert(alertId: string): Promise<ClassifiedAlert> {
  return apiFetch<ClassifiedAlert>(`/api/alerts/${alertId}`);
}

// ─── Transactions ─────────────────────────────────────────────────────────────

export async function fetchTransaction(transactionId: string): Promise<TransactionDetail> {
  return apiFetch<TransactionDetail>(`/api/transactions/${transactionId}`);
}

// ─── Investigations ──────────────────────────────────────────────────────────

export async function startInvestigation(
  alert: ClassifiedAlert
): Promise<StartInvestigationResponse> {
  const payload: StartInvestigationRequest = {
    alert_id: alert.alert_id || alert.classified_alert_id,
    alert_type: alert.alert_type,
    entity_id: alert.customer_id,
    customer_id: alert.customer_id,
    account_id: alert.transaction?.account_id,
    risk_score: alert.risk_score,
    risk_level: alert.risk_level,
    raw_score: alert.risk_score,
    severity: alert.risk_level,
    trigger_reason: alert.alert_type,
    evidence: {
      customer: alert.customer,
      transaction: alert.transaction,
      accounts: alert.accounts || [],
      beneficiaries: alert.beneficiaries || [],
      devices: alert.devices || [],
      transaction_account: alert.transaction_account,
      transaction_beneficiary: alert.transaction_beneficiary,
    },
  };
  return apiFetch<StartInvestigationResponse>("/api/investigations/run", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function fetchInvestigations(): Promise<InvestigationCase[]> {
  return apiFetch<InvestigationCase[]>("/api/investigations/cases");
}

export async function fetchInvestigationDetail(caseId: string): Promise<InvestigationResult> {
  return apiFetch<InvestigationResult>(`/api/investigations/cases/${caseId}/detail`);
}

// ─── Polling helper ───────────────────────────────────────────────────────────

/**
 * Polls the investigation detail endpoint every intervalMs until
 * the case status is "CLOSED" or maxAttempts is reached.
 * Calls onUpdate(result) on each poll.
 */
export async function pollInvestigation(
  caseId: string,
  onUpdate: (result: InvestigationResult) => void,
  intervalMs = 2000,
  maxAttempts = 30
): Promise<InvestigationResult | null> {
  for (let i = 0; i < maxAttempts; i++) {
    await new Promise((r) => setTimeout(r, intervalMs));
    try {
      const result = await fetchInvestigationDetail(caseId);
      onUpdate(result);
      if (result.status === "CLOSED") return result;
    } catch {
      // backend may not have the case yet on first poll
    }
  }
  return null;
}

// ─── Audit Trail ─────────────────────────────────────────────────────────────

export interface AuditLogItem {
  id: string;
  alert_id?: string;
  entity_id?: string;
  objective?: string;
  typology?: string;
  status: string;
  priority_score?: number;
  priority_band?: string;
  final_risk_score?: number;
  decision?: string;
  created_at?: string;
  updated_at?: string;
  summary_notes?: string;
}

export async function fetchAuditLogs(status?: string): Promise<AuditLogItem[]> {
  const qs = status ? `?status=${encodeURIComponent(status)}` : "";
  return apiFetch<AuditLogItem[]>(`/api/audit/logs${qs}`);
}

export function getAuditPdfUrl(caseId: string): string {
  return `${API_BASE}/api/audit/logs/${encodeURIComponent(caseId)}/pdf`;
}

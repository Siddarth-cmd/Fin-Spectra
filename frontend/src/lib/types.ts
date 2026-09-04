/**
 * Fin-Spectra Type Definitions
 * Covers both frontend display types and Fin-Spectra API contracts.
 */

// ─── Common ──────────────────────────────────────────────────────────────────

export type RiskLevel = "CRITICAL" | "HIGH" | "MEDIUM" | "LOW";
export type Decision = "ALLOW" | "REVIEW" | "BLOCK";
export type TaskStatus = "PENDING" | "IN_PROGRESS" | "COMPLETED" | "FAILED";
export type CaseStatus = "OPEN" | "CLOSED";
export type AlertStatus = "OPEN" | "UNDER_INVESTIGATION" | "RESOLVED" | "ESCALATED";

// ─── Dashboard Summary ────────────────────────────────────────────────────────

export interface PipelineSummary {
  accounts_ingested: number;
  transactions_ingested: number;
  raw_alerts_generated: number;
  raw_alerts_by_rule: Record<string, number>;
  accounts_with_alerts: number;
  classified_alerts_by_risk_level: {
    CRITICAL: number;
    HIGH: number;
    MEDIUM: number;
    LOW: number;
  };
  cases_by_decision?: Record<string, number>;
  prioritized_alerts_count?: number;
  open_alerts?: number;
  under_investigation?: number;
  resolved_alerts?: number;
  pipeline_status?: string;
  last_run?: string;
  system_version?: string;
}

// ─── Customer, Transaction, Account, Beneficiary, Device ─────────────────────

export interface CustomerSummary {
  customer_id: string;
  name: string;
  risk_level: RiskLevel;
  account_age_days: number;
  occupation?: string;
  created_at?: string;
}

export interface TransactionSummary {
  transaction_id: string;
  amount: number;
  transaction_type: string;
  transaction_timestamp?: string;
  status?: string;
  account_id?: string;
  beneficiary_id?: string;
}

export interface TransactionDetail extends TransactionSummary {
  customer_id?: string;
  customer?: CustomerSummary;
  account?: { account_id: string; account_type: string; status: string };
  beneficiary?: { beneficiary_id: string; name: string; account_number: string };
}

export interface AccountSummary {
  account_id: string;
  account_type: string;
  status: string;
  created_at?: string;
}

export interface BeneficiarySummary {
  beneficiary_id: string;
  name: string;
  account_number: string;
}

export interface DeviceSummary {
  device_id: string;
  device_type: string;
  first_seen?: string;
  last_seen?: string;
}

// ─── Alerts ───────────────────────────────────────────────────────────────────

export interface InvestigationCaseSummary {
  case_id: string;
  status: CaseStatus;
  decision?: Decision;
  final_risk_score?: number;
  created_at?: string;
}

export interface ClassifiedAlert {
  classified_alert_id?: string;
  alert_id?: string;
  customer_id?: string;
  account_id?: string;          // direct shorthand
  transaction_id?: string;
  alert_type: string;
  risk_score: number;
  risk_level: RiskLevel;
  status?: AlertStatus;
  created_at?: string;
  timestamp?: string;           // alias for created_at used by original components
  detected_reason?: string;     // alias for alert_type note
  triggered_rules?: string[];   // legacy field for rule-based alerts
  customer?: CustomerSummary;
  transaction?: TransactionSummary;
  transaction_account?: { account_id: string; account_type: string; status: string };
  transaction_beneficiary?: { beneficiary_id: string; name: string; account_number: string };
  accounts?: AccountSummary[];
  beneficiaries?: BeneficiarySummary[];
  devices?: DeviceSummary[];
  investigation_case?: InvestigationCaseSummary;
}

export interface AlertsResponse {
  alerts: ClassifiedAlert[];
  items?: ClassifiedAlert[];   // backward compat alias — same as alerts
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

// ─── Investigation Request/Response ──────────────────────────────────────────

export interface StartInvestigationRequest {
  alert_id?: string;
  alert_type: string;
  entity_id?: string;
  customer_id?: string;
  account_id?: string;
  risk_score?: number;
  risk_level?: string;
  raw_score?: number;
  severity?: string;
  trigger_reason?: string;
  evidence?: Record<string, unknown>;
}

export interface StartInvestigationResponse {
  status: string;
  case_id: string;
  entity_id?: string;
  plan_satisfied?: boolean;
  task_list?: TaskItem[];
  investigation_plan?: string[];
  missing_evidence?: string[];
  collected_evidence_summary?: {
    ledger_records: number;
    kyc_notes: string;
    behavioral_metrics: Record<string, unknown>;
    graph_metrics: Record<string, unknown>;
  };
  decision?: string;
}

// ─── Investigation Detail / Workspace ────────────────────────────────────────

export interface TaskItem {
  task_id: string;
  name: string;
  agent_label: string;
  status: TaskStatus;
  required_evidence_key: string;
}

export interface BehavioralMetrics {
  velocity_z_score: number;
  pass_through_ratio: number;
  total_volume_in: number;
  total_volume_out: number;
  trigger_amount: number;
  historical_mean: number;
  historical_stddev: number;
  effective_stddev: number;
  historical_transaction_count: number;
  velocity_baseline_status: string;
  risk_explanation: string;
}

export interface GraphMetrics {
  account_count: number;
  beneficiary_count: number;
  device_count: number;
  transaction_count: number;
  unique_beneficiaries: number;
  tx_per_account: number;
  beneficiary_dispersion_ratio: number;
  multi_beneficiary_flag: number;
  multi_device_multi_beneficiary_flag: boolean;
  self_transfer_detected: boolean;
  fan_in_ratio: number;
  fan_out_ratio: number;
}

export interface RiskScoring {
  final_score?: number;
  decision?: Decision;
  subscores: {
    phase1_prior: number;
    behavior: number;
    graph: number;
    kyc: number;
  };
  explanation: string;
}

export interface LedgerEntry {
  id: string;
  dir: "IN" | "OUT";
  amount: number;
  channel: string;
  time: string;
}

export interface EvidenceSummary {
  ledger_count: number;
  ledger_history: LedgerEntry[];
  kyc_notes: string;
  balance_history: Record<string, unknown>;
  historical_cases_count: number;
}

export interface InvestigationResult {
  case_id: string;
  alert_id: string;
  entity_id: string;
  status: CaseStatus;
  priority_score?: number;
  priority_band?: string;
  created_at?: string;
  updated_at?: string;

  final_risk_score?: number;
  decision?: Decision;

  investigation_plan: string[];
  task_list: TaskItem[];
  plan_satisfied: boolean;
  missing_evidence: string[];
  loop_count: number;

  typology_classification: string;
  typology_rationale: string;
  alert_type: string;

  evidence_summary: EvidenceSummary;
  behavioral_metrics: BehavioralMetrics;
  graph_metrics: GraphMetrics;
  risk_scoring: RiskScoring;
  dossier: string;
}

// ─── Cases List ───────────────────────────────────────────────────────────────

export interface InvestigationCase {
  id: string;
  alert_id: string;
  entity_id: string;
  decision?: Decision;
  score?: number;
  status: CaseStatus;
}

"use client";

import React, { useState, useCallback } from "react";
import {
  X,
  Play,
  Loader,
  AlertTriangle,
  CheckCircle,
  ExternalLink,
  User,
  DollarSign,
  Clock,
  Shield,
} from "lucide-react";
import { ClassifiedAlert, InvestigationResult } from "@/lib/types";
import { startInvestigation, pollInvestigation } from "@/lib/api";
import { RiskBadge } from "@/components/common/RiskBadge";

interface AlertSlideOverProps {
  alert: ClassifiedAlert | null;
  onClose: () => void;
}

type InvestigationStatus =
  | "idle"
  | "starting"
  | "running"
  | "completed"
  | "failed"
  | "already_investigated";

function formatCurrency(v: number) {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 2,
  }).format(v);
}

function formatDate(iso?: string) {
  if (!iso) return "—";
  try {
    return new Date(iso).toLocaleString("en-US", {
      month: "short",
      day: "numeric",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  } catch {
    return iso;
  }
}

export function AlertSlideOver({ alert, onClose }: AlertSlideOverProps) {
  const [investigationStatus, setInvestigationStatus] = useState<InvestigationStatus>("idle");
  const [investigationResult, setInvestigationResult] = useState<InvestigationResult | null>(null);
  const [caseId, setCaseId] = useState<string | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const handleStartInvestigation = useCallback(async () => {
    if (!alert) return;
    setErrorMsg(null);
    setInvestigationStatus("starting");

    try {
      const response = await startInvestigation(alert);

      if (response.status === "already_investigated") {
        setInvestigationStatus("already_investigated");
        setCaseId(response.case_id);
        return;
      }

      setCaseId(response.case_id);
      setInvestigationStatus("running");

      // Poll for completion
      const result = await pollInvestigation(
        response.case_id,
        (partial) => {
          setInvestigationResult(partial);
        },
        2500,
        20
      );

      if (result) {
        setInvestigationResult(result);
        setInvestigationStatus("completed");
      } else {
        // timed out but we have partial result
        setInvestigationStatus("completed");
      }
    } catch (err: any) {
      setErrorMsg(err.message || "Investigation failed");
      setInvestigationStatus("failed");
    }
  }, [alert]);

  if (!alert) return null;

  const alertId = alert.alert_id || alert.classified_alert_id || "—";
  const score = alert.risk_score ?? 0;

  return (
    <>
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-black/60 backdrop-blur-sm z-40"
        onClick={onClose}
      />

      {/* Slide-over panel */}
      <div className="fixed right-0 top-0 h-full w-full max-w-xl bg-slate-900 border-l border-slate-700/60 shadow-2xl z-50 flex flex-col overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-700/60 bg-slate-800/80 flex-shrink-0">
          <div>
            <p className="text-xs text-slate-400 font-mono">{alertId}</p>
            <h2 className="text-lg font-bold text-white">{alert.alert_type}</h2>
          </div>
          <div className="flex items-center gap-3">
            <RiskBadge level={alert.risk_level} />
            <button
              onClick={onClose}
              className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-700 transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Scrollable body */}
        <div className="flex-1 overflow-y-auto p-6 space-y-5">
          {/* Alert Meta */}
          <div className="grid grid-cols-2 gap-3">
            <div className="bg-slate-800/60 border border-slate-700/60 rounded-xl p-3">
              <div className="flex items-center gap-1.5 text-slate-400 mb-1">
                <Shield className="w-3.5 h-3.5" />
                <p className="text-xs">Risk Score</p>
              </div>
              <p className={`text-2xl font-black tabular-nums ${
                score >= 85 ? "text-red-400" : score >= 65 ? "text-amber-400" : "text-emerald-400"
              }`}>
                {score.toFixed(1)}
              </p>
            </div>
            <div className="bg-slate-800/60 border border-slate-700/60 rounded-xl p-3">
              <div className="flex items-center gap-1.5 text-slate-400 mb-1">
                <Clock className="w-3.5 h-3.5" />
                <p className="text-xs">Created</p>
              </div>
              <p className="text-sm font-semibold text-white">{formatDate(alert.created_at)}</p>
            </div>
          </div>

          {/* Customer Info */}
          {alert.customer && (
            <div className="bg-slate-800/60 border border-slate-700/60 rounded-xl p-4">
              <div className="flex items-center gap-2 mb-3">
                <User className="w-4 h-4 text-cyan-400" />
                <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-widest">
                  Customer Profile
                </h3>
              </div>
              <div className="grid grid-cols-2 gap-3">
                {[
                  { label: "Name", value: alert.customer.name },
                  { label: "Customer ID", value: alert.customer.customer_id },
                  { label: "Risk Level", value: alert.customer.risk_level },
                  { label: "Account Age", value: `${alert.customer.account_age_days} days` },
                  { label: "Occupation", value: alert.customer.occupation || "—" },
                ].map((f) => (
                  <div key={f.label}>
                    <p className="text-xs text-slate-500">{f.label}</p>
                    <p className="text-sm font-semibold text-white">{f.value}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Transaction Info */}
          {alert.transaction && (
            <div className="bg-slate-800/60 border border-slate-700/60 rounded-xl p-4">
              <div className="flex items-center gap-2 mb-3">
                <DollarSign className="w-4 h-4 text-emerald-400" />
                <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-widest">
                  Triggering Transaction
                </h3>
              </div>
              <div className="grid grid-cols-2 gap-3">
                {[
                  { label: "Transaction ID", value: alert.transaction.transaction_id },
                  { label: "Amount", value: formatCurrency(alert.transaction.amount) },
                  { label: "Type", value: alert.transaction.transaction_type },
                  { label: "Timestamp", value: formatDate(alert.transaction.transaction_timestamp) },
                ].map((f) => (
                  <div key={f.label}>
                    <p className="text-xs text-slate-500">{f.label}</p>
                    <p className="text-sm font-semibold text-white font-mono">{f.value}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Investigation Status */}
          {investigationStatus !== "idle" && (
            <div
              className={`rounded-xl border p-4 ${
                investigationStatus === "completed"
                  ? "bg-emerald-400/10 border-emerald-500/30"
                  : investigationStatus === "failed"
                  ? "bg-red-400/10 border-red-500/30"
                  : investigationStatus === "already_investigated"
                  ? "bg-cyan-400/10 border-cyan-500/30"
                  : "bg-slate-800/60 border-slate-700/60"
              }`}
            >
              <div className="flex items-center gap-3">
                {(investigationStatus === "starting" || investigationStatus === "running") && (
                  <Loader className="w-5 h-5 text-cyan-400 animate-spin flex-shrink-0" />
                )}
                {investigationStatus === "completed" && (
                  <CheckCircle className="w-5 h-5 text-emerald-400 flex-shrink-0" />
                )}
                {investigationStatus === "failed" && (
                  <AlertTriangle className="w-5 h-5 text-red-400 flex-shrink-0" />
                )}
                {investigationStatus === "already_investigated" && (
                  <CheckCircle className="w-5 h-5 text-cyan-400 flex-shrink-0" />
                )}

                <div className="flex-1">
                  {investigationStatus === "starting" && (
                    <p className="text-sm text-white">Starting investigation pipeline...</p>
                  )}
                  {investigationStatus === "running" && (
                    <div>
                      <p className="text-sm font-semibold text-white">Multi-Agent Investigation Executing...</p>
                      <p className="text-xs text-cyan-400 mt-0.5">
                        Task Planner → Evidence Retrieval → KYC Verifier → Behaviour Agent → Graph Analyst → Case Assembly
                      </p>
                    </div>
                  )}
                  {investigationStatus === "completed" && investigationResult && (
                    <div>
                      <p className="text-sm font-bold text-emerald-300">Investigation Complete</p>
                      <p className="text-xs text-slate-400">
                        Score: {investigationResult.final_risk_score?.toFixed(1)} | Decision:{" "}
                        <span className="font-bold">{investigationResult.decision}</span>
                      </p>
                    </div>
                  )}
                  {investigationStatus === "failed" && (
                    <p className="text-sm text-red-300">{errorMsg || "Investigation failed"}</p>
                  )}
                  {investigationStatus === "already_investigated" && (
                    <p className="text-sm text-cyan-300">
                      Already investigated. Case: {caseId}
                    </p>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* Investigation summary quick result */}
          {investigationStatus === "completed" && investigationResult && (
            <div className="bg-slate-800/60 border border-slate-700/60 rounded-xl p-4 space-y-2">
              <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-widest mb-2">
                Quick Results
              </h3>
              <div className="grid grid-cols-2 gap-2 text-sm">
                <div>
                  <p className="text-xs text-slate-500">Typology</p>
                  <p className="font-mono font-bold text-purple-300">
                    {investigationResult.typology_classification || "—"}
                  </p>
                </div>
                <div>
                  <p className="text-xs text-slate-500">Tasks Completed</p>
                  <p className="font-semibold text-white">
                    {investigationResult.task_list?.filter((t) => t.status === "COMPLETED").length}/
                    {investigationResult.task_list?.length}
                  </p>
                </div>
                <div>
                  <p className="text-xs text-slate-500">Plan Satisfied</p>
                  <p className={`font-semibold ${investigationResult.plan_satisfied ? "text-emerald-400" : "text-amber-400"}`}>
                    {investigationResult.plan_satisfied ? "Yes" : "No"}
                  </p>
                </div>
                <div>
                  <p className="text-xs text-slate-500">Evidence Records</p>
                  <p className="font-semibold text-white">
                    {investigationResult.evidence_summary?.ledger_count ?? 0} ledger
                  </p>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Footer Actions */}
        <div className="px-6 py-4 border-t border-slate-700/60 bg-slate-800/60 flex-shrink-0 space-y-2">
          {caseId && (
            <a
              href={`/investigations/${caseId}`}
              className="flex items-center justify-center gap-2 w-full bg-slate-700 hover:bg-slate-600 text-white text-sm font-semibold py-2.5 rounded-xl transition-colors"
            >
              <ExternalLink className="w-4 h-4" />
              Open Full Investigation Workspace
            </a>
          )}

          <button
            onClick={handleStartInvestigation}
            disabled={
              investigationStatus === "starting" ||
              investigationStatus === "running" ||
              investigationStatus === "completed" ||
              investigationStatus === "already_investigated"
            }
            className={`flex items-center justify-center gap-2 w-full text-sm font-semibold py-2.5 rounded-xl transition-all ${
              investigationStatus === "idle" || investigationStatus === "failed"
                ? "bg-cyan-600 hover:bg-cyan-500 text-white cursor-pointer"
                : "bg-slate-700 text-slate-400 cursor-not-allowed"
            }`}
          >
            {investigationStatus === "starting" || investigationStatus === "running" ? (
              <>
                <Loader className="w-4 h-4 animate-spin" />
                Running Investigation...
              </>
            ) : investigationStatus === "completed" ? (
              <>
                <CheckCircle className="w-4 h-4" />
                Investigation Complete
              </>
            ) : investigationStatus === "already_investigated" ? (
              <>
                <CheckCircle className="w-4 h-4" />
                Already Investigated
              </>
            ) : (
              <>
                <Play className="w-4 h-4" />
                Start Investigation
              </>
            )}
          </button>
        </div>
      </div>
    </>
  );
}

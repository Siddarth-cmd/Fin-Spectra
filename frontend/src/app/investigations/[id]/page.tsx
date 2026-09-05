"use client";

import React, { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { fetchInvestigationDetail } from "@/lib/api";
import { InvestigationResult } from "@/lib/types";
import { InvestigationPlannerPanel } from "@/components/investigation/InvestigationPlannerPanel";
import { EvidenceWorkspace } from "@/components/investigation/EvidenceWorkspace";
import { KycVerificationPanel } from "@/components/investigation/KycVerificationPanel";
import { BehaviorAnalysisPanel } from "@/components/investigation/BehaviorAnalysisPanel";
import { GraphMetricsPanel } from "@/components/investigation/GraphMetricsPanel";
import { RiskAssessmentPanel } from "@/components/investigation/RiskAssessmentPanel";
import { CaseSARPanel } from "@/components/investigation/CaseSARPanel";
import {
  ArrowLeft,
  Loader,
  AlertTriangle,
  ClipboardList,
  Search,
  UserCheck,
  Activity,
  GitBranch,
  Shield,
  FileText,
} from "lucide-react";

type Tab =
  | "planner"
  | "evidence"
  | "kyc"
  | "behavior"
  | "graph"
  | "risk"
  | "sar";

const TABS: { key: Tab; label: string; icon: React.ReactNode }[] = [
  { key: "planner", label: "Task Planner Agent", icon: <ClipboardList className="w-4 h-4" /> },
  { key: "evidence", label: "Evidence Agent", icon: <Search className="w-4 h-4" /> },
  { key: "kyc", label: "KYC Verifier Agent", icon: <UserCheck className="w-4 h-4" /> },
  { key: "behavior", label: "Behaviour Agent", icon: <Activity className="w-4 h-4" /> },
  { key: "graph", label: "Graph Analyst Agent", icon: <GitBranch className="w-4 h-4" /> },
  { key: "risk", label: "Risk Scoring Agent", icon: <Shield className="w-4 h-4" /> },
  { key: "sar", label: "Case Assembly Agent", icon: <FileText className="w-4 h-4" /> },
];

const DECISION_COLORS: Record<string, string> = {
  ALLOW: "bg-emerald-500/20 border-emerald-500/40 text-emerald-300",
  REVIEW: "bg-amber-500/20 border-amber-500/40 text-amber-300",
  BLOCK: "bg-red-500/20 border-red-500/40 text-red-300",
};

export default function InvestigationDetailPage() {
  const params = useParams();
  const router = useRouter();
  const caseId = params?.id as string;

  const [result, setResult] = useState<InvestigationResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<Tab>("planner");

  useEffect(() => {
    if (!caseId) return;

    async function load() {
      try {
        const data = await fetchInvestigationDetail(caseId);
        setResult(data);
      } catch (err: any) {
        setError(err.message || "Failed to load investigation");
      } finally {
        setLoading(false);
      }
    }

    load();
  }, [caseId]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full min-h-[400px]">
        <div className="text-center">
          <Loader className="w-8 h-8 text-cyan-400 animate-spin mx-auto mb-3" />
          <p className="text-slate-400 text-sm">Loading investigation workspace...</p>
        </div>
      </div>
    );
  }

  if (error || !result) {
    return (
      <div className="flex items-center justify-center h-full min-h-[400px]">
        <div className="text-center">
          <AlertTriangle className="w-8 h-8 text-red-400 mx-auto mb-3" />
          <p className="text-red-300 text-sm mb-2">{error || "Investigation not found"}</p>
          <p className="text-slate-500 text-xs">Case ID: {caseId}</p>
          <button
            onClick={() => router.back()}
            className="mt-4 text-sm text-cyan-400 hover:text-cyan-300 flex items-center gap-1 mx-auto"
          >
            <ArrowLeft className="w-3.5 h-3.5" /> Go back
          </button>
        </div>
      </div>
    );
  }

  const decisionCls = result.decision
    ? DECISION_COLORS[result.decision] || "bg-slate-700/30 border-slate-600/30 text-slate-400"
    : "bg-slate-700/30 border-slate-600/30 text-slate-400";

  return (
    <div className="flex flex-col h-full">
      {/* Page Header */}
      <div className="px-6 py-4 border-b border-slate-700/60 bg-slate-800/40 flex-shrink-0">
        <button
          onClick={() => router.back()}
          className="flex items-center gap-1.5 text-xs text-slate-400 hover:text-white mb-3 transition-colors"
        >
          <ArrowLeft className="w-3.5 h-3.5" /> Back
        </button>

        <div className="flex items-start justify-between gap-4 flex-wrap">
          <div>
            <div className="flex items-center gap-3 flex-wrap">
              <h1 className="text-xl font-bold text-white font-mono">{result.case_id}</h1>
              {result.decision && (
                <span
                  className={`text-xs font-bold px-2.5 py-1 rounded-lg border ${decisionCls}`}
                >
                  {result.decision}
                </span>
              )}
              <span className="text-xs font-medium text-slate-400 bg-slate-700/60 border border-slate-600/40 px-2 py-0.5 rounded-md">
                {result.status}
              </span>
            </div>
            <p className="text-sm text-slate-400 mt-1">
              Alert: <span className="font-mono text-slate-300">{result.alert_id}</span>
              {" · "}Entity: <span className="font-mono text-slate-300">{result.entity_id}</span>
              {result.typology_classification && (
                <>
                  {" · "}
                  <span className="text-purple-400 font-semibold">
                    {result.typology_classification}
                  </span>
                </>
              )}
            </p>
          </div>

          <div className="text-right">
            {result.final_risk_score !== undefined && result.final_risk_score !== null && (
              <div>
                <p className="text-xs text-slate-400">Risk Score</p>
                <p
                  className={`text-3xl font-black tabular-nums ${
                    result.final_risk_score > 75
                      ? "text-red-400"
                      : result.final_risk_score > 40
                      ? "text-amber-400"
                      : "text-emerald-400"
                  }`}
                >
                  {result.final_risk_score.toFixed(1)}
                </p>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="px-6 border-b border-slate-700/60 bg-slate-800/20 flex-shrink-0">
        <div className="flex gap-0 overflow-x-auto">
          {TABS.map((tab) => (
            <button
              key={tab.key}
              onClick={() => setActiveTab(tab.key)}
              className={`flex items-center gap-1.5 px-4 py-3 text-sm font-medium border-b-2 transition-colors whitespace-nowrap ${
                activeTab === tab.key
                  ? "border-cyan-500 text-cyan-400"
                  : "border-transparent text-slate-400 hover:text-white hover:border-slate-600"
              }`}
            >
              {tab.icon}
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      {/* Tab Content */}
      <div className="flex-1 overflow-y-auto p-6">
        {activeTab === "planner" && (
          <InvestigationPlannerPanel
            taskList={result.task_list || []}
            investigationPlan={result.investigation_plan || []}
            planSatisfied={result.plan_satisfied}
            missingEvidence={result.missing_evidence || []}
            loopCount={result.loop_count}
            alertType={result.alert_type}
            typologyClassification={result.typology_classification}
          />
        )}
        {activeTab === "evidence" && (
          <EvidenceWorkspace evidenceSummary={result.evidence_summary} />
        )}
        {activeTab === "kyc" && (
          <KycVerificationPanel
            kycNotes={result.evidence_summary?.kyc_notes || ""}
            riskScoring={result.risk_scoring}
          />
        )}
        {activeTab === "behavior" && (
          <BehaviorAnalysisPanel metrics={result.behavioral_metrics} />
        )}
        {activeTab === "graph" && (
          <GraphMetricsPanel metrics={result.graph_metrics} />
        )}
        {activeTab === "risk" && (
          <RiskAssessmentPanel
            riskScoring={result.risk_scoring}
            priorityScore={result.priority_score}
          />
        )}
        {activeTab === "sar" && (
          <CaseSARPanel
            dossier={result.dossier}
            typologyClassification={result.typology_classification}
            typologyRationale={result.typology_rationale}
            decision={result.decision}
            caseId={result.case_id}
            alertId={result.alert_id}
            entityId={result.entity_id}
          />
        )}
      </div>
    </div>
  );
}
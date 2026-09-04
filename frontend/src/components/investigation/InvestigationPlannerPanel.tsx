"use client";

import React from "react";
import { TaskItem } from "@/lib/types";
import {
  CheckCircle,
  Clock,
  Loader,
  XCircle,
  ChevronRight,
} from "lucide-react";

interface InvestigationPlannerPanelProps {
  taskList: TaskItem[];
  investigationPlan: string[];
  planSatisfied: boolean;
  missingEvidence: string[];
  loopCount: number;
  alertType: string;
  typologyClassification: string;
}

const STATUS_CONFIG: Record<
  string,
  { icon: React.ReactNode; label: string; color: string; bg: string }
> = {
  COMPLETED: {
    icon: <CheckCircle className="w-4 h-4" />,
    label: "Completed",
    color: "text-emerald-400",
    bg: "bg-emerald-400/10 border-emerald-500/30",
  },
  IN_PROGRESS: {
    icon: <Loader className="w-4 h-4 animate-spin" />,
    label: "Running",
    color: "text-cyan-400",
    bg: "bg-cyan-400/10 border-cyan-500/30",
  },
  PENDING: {
    icon: <Clock className="w-4 h-4" />,
    label: "Pending",
    color: "text-slate-400",
    bg: "bg-slate-700/40 border-slate-600/30",
  },
  FAILED: {
    icon: <XCircle className="w-4 h-4" />,
    label: "Failed",
    color: "text-red-400",
    bg: "bg-red-400/10 border-red-500/30",
  },
};

const PIPELINE_NODES = [
  { key: "task_planner", label: "Task Planner" },
  { key: "evidence_retrieval", label: "Evidence" },
  { key: "kyc_verifier", label: "KYC" },
  { key: "behavior_analyzer", label: "Behavior" },
  { key: "graph_analyst", label: "Graph" },
  { key: "plan_checker", label: "Plan Check" },
  { key: "typology_classifier", label: "Typology" },
  { key: "scoring_node", label: "Scoring" },
  { key: "case_assembler", label: "SAR" },
];

export function InvestigationPlannerPanel({
  taskList,
  investigationPlan,
  planSatisfied,
  missingEvidence,
  loopCount,
  alertType,
  typologyClassification,
}: InvestigationPlannerPanelProps) {
  return (
    <div className="space-y-4">
      {/* Pipeline Diagram */}
      <div className="bg-slate-800/60 border border-slate-700/60 rounded-xl p-4">
        <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-widest mb-3">
          Investigation Pipeline
        </h3>
        <div className="flex flex-wrap items-center gap-1">
          {PIPELINE_NODES.map((node, i) => (
            <React.Fragment key={node.key}>
              <div className="bg-slate-700/70 border border-slate-600/40 rounded-lg px-2 py-1.5 text-xs font-medium text-slate-200 whitespace-nowrap">
                {node.label}
              </div>
              {i < PIPELINE_NODES.length - 1 && (
                <ChevronRight className="w-3 h-3 text-slate-500 flex-shrink-0" />
              )}
            </React.Fragment>
          ))}
        </div>
      </div>

      {/* Alert & Typology Row */}
      <div className="grid grid-cols-2 gap-3">
        <div className="bg-slate-800/60 border border-slate-700/60 rounded-xl p-3">
          <p className="text-xs text-slate-400 mb-1">Alert Type</p>
          <p className="text-sm font-semibold text-white font-mono">{alertType || "—"}</p>
        </div>
        <div className="bg-slate-800/60 border border-slate-700/60 rounded-xl p-3">
          <p className="text-xs text-slate-400 mb-1">Classified Typology</p>
          <p className="text-sm font-semibold text-cyan-300 font-mono">
            {typologyClassification || "Pending..."}
          </p>
        </div>
      </div>

      {/* Task Cards */}
      <div className="bg-slate-800/60 border border-slate-700/60 rounded-xl p-4">
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-widest">
            Agent Task Queue
          </h3>
          {loopCount > 0 && (
            <span className="text-xs text-amber-400 bg-amber-400/10 px-2 py-0.5 rounded-full border border-amber-500/30">
              Loop #{loopCount}
            </span>
          )}
        </div>

        {taskList.length === 0 ? (
          <p className="text-slate-500 text-sm text-center py-4">
            No tasks generated yet
          </p>
        ) : (
          <div className="space-y-2">
            {taskList.map((task) => {
              const cfg = STATUS_CONFIG[task.status] || STATUS_CONFIG.PENDING;
              return (
                <div
                  key={task.task_id}
                  className={`flex items-center justify-between rounded-lg border px-3 py-2 ${cfg.bg}`}
                >
                  <div className="flex items-center gap-2">
                    <span className={cfg.color}>{cfg.icon}</span>
                    <div>
                      <p className="text-sm font-medium text-white">
                        {task.agent_label}
                      </p>
                      <p className="text-xs text-slate-400 font-mono">
                        {task.name}
                      </p>
                    </div>
                  </div>
                  <span
                    className={`text-xs font-semibold uppercase tracking-wide ${cfg.color}`}
                  >
                    {cfg.label}
                  </span>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Investigation Plan */}
      {investigationPlan.length > 0 && (
        <div className="bg-slate-800/60 border border-slate-700/60 rounded-xl p-4">
          <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-widest mb-3">
            Investigation Objectives
          </h3>
          <ul className="space-y-1.5">
            {investigationPlan.map((item, i) => (
              <li key={i} className="flex items-center gap-2 text-sm text-slate-300">
                <CheckCircle className="w-3.5 h-3.5 text-emerald-400 flex-shrink-0" />
                {item}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Plan Satisfaction */}
      <div
        className={`rounded-xl border p-3 flex items-center gap-3 ${
          planSatisfied
            ? "bg-emerald-400/10 border-emerald-500/30"
            : missingEvidence.length > 0
            ? "bg-amber-400/10 border-amber-500/30"
            : "bg-slate-800/60 border-slate-700/60"
        }`}
      >
        {planSatisfied ? (
          <CheckCircle className="w-5 h-5 text-emerald-400 flex-shrink-0" />
        ) : missingEvidence.length > 0 ? (
          <XCircle className="w-5 h-5 text-amber-400 flex-shrink-0" />
        ) : (
          <Clock className="w-5 h-5 text-slate-400 flex-shrink-0" />
        )}
        <div>
          <p className="text-sm font-semibold text-white">
            {planSatisfied
              ? "Plan Satisfied — All evidence collected"
              : missingEvidence.length > 0
              ? `Plan Incomplete — ${missingEvidence.length} evidence gap(s)`
              : "Awaiting plan evaluation"}
          </p>
          {missingEvidence.length > 0 && (
            <ul className="mt-1 space-y-0.5">
              {missingEvidence.map((m, i) => (
                <li key={i} className="text-xs text-amber-300 font-mono">
                  ⚠ {m}
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>
    </div>
  );
}

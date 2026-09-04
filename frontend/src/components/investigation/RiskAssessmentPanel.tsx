"use client";

import React from "react";
import { RiskScoring, Decision } from "@/lib/types";
import { ShieldAlert, ShieldCheck, ShieldX } from "lucide-react";

interface RiskAssessmentPanelProps {
  riskScoring: RiskScoring;
  priorityScore?: number;
}

const DECISION_CONFIG: Record<
  Decision,
  { label: string; color: string; bg: string; border: string; icon: React.ReactNode }
> = {
  ALLOW: {
    label: "ALLOW",
    color: "text-emerald-400",
    bg: "bg-emerald-400/10",
    border: "border-emerald-500/40",
    icon: <ShieldCheck className="w-8 h-8" />,
  },
  REVIEW: {
    label: "REVIEW",
    color: "text-amber-400",
    bg: "bg-amber-400/10",
    border: "border-amber-500/40",
    icon: <ShieldAlert className="w-8 h-8" />,
  },
  BLOCK: {
    label: "BLOCK",
    color: "text-red-400",
    bg: "bg-red-400/10",
    border: "border-red-500/40",
    icon: <ShieldX className="w-8 h-8" />,
  },
};

function ScoreGauge({ score }: { score: number }) {
  const pct = Math.min(Math.max(score, 0), 100);
  const color =
    score > 75 ? "text-red-400" : score > 40 ? "text-amber-400" : "text-emerald-400";
  const trackColor =
    score > 75 ? "bg-red-500" : score > 40 ? "bg-amber-500" : "bg-emerald-500";

  return (
    <div className="flex flex-col items-center gap-3">
      <div className={`text-5xl font-black tabular-nums ${color}`}>
        {score?.toFixed(1) ?? "—"}
      </div>
      <div className="text-xs text-slate-400">/ 100</div>
      <div className="w-full h-3 bg-slate-700 rounded-full overflow-hidden">
        <div
          className={`h-full rounded-full transition-all duration-700 ${trackColor}`}
          style={{ width: `${pct}%` }}
        />
      </div>
    </div>
  );
}

function SubScoreBar({
  label,
  value,
  weight,
}: {
  label: string;
  value: number;
  weight: string;
}) {
  const pct = Math.min(value, 100);
  const color = value > 75 ? "bg-red-500" : value > 40 ? "bg-amber-500" : "bg-emerald-500";

  return (
    <div>
      <div className="flex justify-between text-xs mb-1">
        <span className="text-slate-400">
          {label} <span className="text-slate-600">({weight})</span>
        </span>
        <span className="font-mono font-bold text-white">{value.toFixed(1)}</span>
      </div>
      <div className="h-1.5 bg-slate-700 rounded-full overflow-hidden">
        <div className={`h-full rounded-full ${color}`} style={{ width: `${pct}%` }} />
      </div>
    </div>
  );
}

export function RiskAssessmentPanel({
  riskScoring,
  priorityScore,
}: RiskAssessmentPanelProps) {
  if (!riskScoring) return null;

  const decision = riskScoring.decision;
  const cfg = decision ? DECISION_CONFIG[decision] : null;
  const finalScore = riskScoring.final_score ?? 0;

  return (
    <div className="space-y-4">
      {/* Decision + Score */}
      <div className={`rounded-xl border p-6 ${cfg?.bg ?? "bg-slate-800/60"} ${cfg?.border ?? "border-slate-700/60"}`}>
        <div className="flex items-center gap-6">
          {/* Gauge */}
          <div className="flex-1">
            <ScoreGauge score={finalScore} />
          </div>
          {/* Decision badge */}
          <div className="text-right">
            {cfg && (
              <>
                <div className={`flex justify-end ${cfg.color} mb-2`}>{cfg.icon}</div>
                <p className={`text-3xl font-black tracking-wider ${cfg.color}`}>
                  {cfg.label}
                </p>
                <p className="text-xs text-slate-400 mt-1">Final decision</p>
              </>
            )}
            {!cfg && (
              <p className="text-slate-500 text-sm">Investigation in progress...</p>
            )}
          </div>
        </div>
      </div>

      {/* Sub-Scores */}
      <div className="bg-slate-800/60 border border-slate-700/60 rounded-xl p-4 space-y-3">
        <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-widest mb-1">
          Composite Score Breakdown
        </h3>
        <p className="text-xs text-slate-500 mb-3">
          Final = 0.35 × Phase1 + 0.25 × Behavior + 0.25 × Graph + 0.15 × KYC
        </p>
        <SubScoreBar
          label="Phase-1 Prior"
          value={riskScoring.subscores.phase1_prior}
          weight="35%"
        />
        <SubScoreBar
          label="Behavioral"
          value={riskScoring.subscores.behavior}
          weight="25%"
        />
        <SubScoreBar
          label="Graph / Network"
          value={riskScoring.subscores.graph}
          weight="25%"
        />
        <SubScoreBar
          label="KYC"
          value={riskScoring.subscores.kyc}
          weight="15%"
        />
      </div>

      {/* Explanation */}
      {riskScoring.explanation && (
        <div className="bg-slate-800/60 border border-slate-700/60 rounded-xl p-4">
          <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-widest mb-2">
            Scoring Explanation
          </h3>
          <p className="text-sm text-slate-300 leading-relaxed font-mono text-xs">
            {riskScoring.explanation}
          </p>
        </div>
      )}

      {/* Thresholds legend */}
      <div className="grid grid-cols-3 gap-2 text-center">
        {[
          { label: "ALLOW", range: "≤ 40", color: "text-emerald-400", border: "border-emerald-500/30" },
          { label: "REVIEW", range: "41–75", color: "text-amber-400", border: "border-amber-500/30" },
          { label: "BLOCK", range: "> 75", color: "text-red-400", border: "border-red-500/30" },
        ].map((t) => (
          <div
            key={t.label}
            className={`border rounded-lg py-2 bg-slate-800/40 ${t.border}`}
          >
            <p className={`text-xs font-bold ${t.color}`}>{t.label}</p>
            <p className="text-xs text-slate-500">{t.range}</p>
          </div>
        ))}
      </div>
    </div>
  );
}

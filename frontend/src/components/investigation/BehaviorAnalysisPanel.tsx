"use client";

import React from "react";
import { BehavioralMetrics } from "@/lib/types";
import { Activity, TrendingUp, TrendingDown, AlertTriangle } from "lucide-react";

interface BehaviorAnalysisPanelProps {
  metrics: BehavioralMetrics;
}

function formatCurrency(v: number) {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 0,
  }).format(v);
}

function ZScoreBar({ value }: { value: number }) {
  const clamped = Math.min(Math.max(value, -1), 5);
  const pct = ((clamped + 1) / 6) * 100;
  const color =
    value > 3
      ? "bg-red-500"
      : value > 1.5
      ? "bg-amber-500"
      : "bg-emerald-500";

  return (
    <div>
      <div className="flex justify-between text-xs text-slate-400 mb-1">
        <span>Z-Score</span>
        <span
          className={`font-bold font-mono ${
            value > 3
              ? "text-red-400"
              : value > 1.5
              ? "text-amber-400"
              : "text-emerald-400"
          }`}
        >
          {value.toFixed(2)}σ
        </span>
      </div>
      <div className="h-2 bg-slate-700 rounded-full overflow-hidden">
        <div
          className={`h-full rounded-full transition-all ${color}`}
          style={{ width: `${pct}%` }}
        />
      </div>
      <div className="flex justify-between text-xs text-slate-600 mt-0.5">
        <span>-1</span>
        <span>0</span>
        <span>1.5</span>
        <span>3+</span>
      </div>
    </div>
  );
}

function PassThroughBar({ value }: { value: number }) {
  const pct = Math.min(value * 100, 100);
  const color = value > 0.9 ? "bg-red-500" : value > 0.6 ? "bg-amber-500" : "bg-emerald-500";

  return (
    <div>
      <div className="flex justify-between text-xs text-slate-400 mb-1">
        <span>Pass-Through Ratio</span>
        <span
          className={`font-bold font-mono ${
            value > 0.9 ? "text-red-400" : value > 0.6 ? "text-amber-400" : "text-emerald-400"
          }`}
        >
          {(value * 100).toFixed(1)}%
        </span>
      </div>
      <div className="h-2 bg-slate-700 rounded-full overflow-hidden">
        <div className={`h-full rounded-full ${color}`} style={{ width: `${pct}%` }} />
      </div>
    </div>
  );
}

export function BehaviorAnalysisPanel({ metrics }: BehaviorAnalysisPanelProps) {
  if (!metrics) return null;

  return (
    <div className="space-y-4">
      {/* Z-Score & Pass-Through Bars */}
      <div className="bg-slate-800/60 border border-slate-700/60 rounded-xl p-4 space-y-4">
        <div className="flex items-center gap-2 mb-1">
          <Activity className="w-4 h-4 text-cyan-400" />
          <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-widest">
            Velocity Analysis
          </h3>
        </div>
        <ZScoreBar value={metrics.velocity_z_score} />
        <PassThroughBar value={metrics.pass_through_ratio} />

        {metrics.velocity_baseline_status === "INSUFFICIENT_HISTORICAL_SAMPLES" && (
          <div className="flex items-center gap-2 text-xs text-amber-400 bg-amber-400/10 border border-amber-500/30 rounded-lg px-3 py-2">
            <AlertTriangle className="w-3.5 h-3.5 flex-shrink-0" />
            Insufficient historical data for baseline
          </div>
        )}
      </div>

      {/* Volume Grid */}
      <div className="grid grid-cols-2 gap-3">
        <div className="bg-slate-800/60 border border-emerald-500/20 rounded-xl p-4">
          <div className="flex items-center gap-1.5 mb-1">
            <TrendingDown className="w-3.5 h-3.5 text-emerald-400" />
            <p className="text-xs text-slate-400">Total Inflow</p>
          </div>
          <p className="text-lg font-bold text-emerald-400">
            {formatCurrency(metrics.total_volume_in)}
          </p>
        </div>
        <div className="bg-slate-800/60 border border-red-500/20 rounded-xl p-4">
          <div className="flex items-center gap-1.5 mb-1">
            <TrendingUp className="w-3.5 h-3.5 text-red-400" />
            <p className="text-xs text-slate-400">Total Outflow</p>
          </div>
          <p className="text-lg font-bold text-red-400">
            {formatCurrency(metrics.total_volume_out)}
          </p>
        </div>
      </div>

      {/* Statistical Baseline */}
      <div className="bg-slate-800/60 border border-slate-700/60 rounded-xl p-4">
        <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-widest mb-3">
          Statistical Baseline
        </h3>
        <div className="grid grid-cols-2 gap-3">
          {[
            { label: "Trigger Amount", value: formatCurrency(metrics.trigger_amount) },
            { label: "Historical Mean", value: formatCurrency(metrics.historical_mean) },
            { label: "Std Deviation", value: formatCurrency(metrics.historical_stddev) },
            { label: "Effective σ", value: formatCurrency(metrics.effective_stddev) },
            {
              label: "Historical TXs",
              value: `${metrics.historical_transaction_count} records`,
            },
            { label: "Baseline Status", value: metrics.velocity_baseline_status || "—" },
          ].map((row) => (
            <div key={row.label}>
              <p className="text-xs text-slate-500">{row.label}</p>
              <p className="text-sm font-semibold text-white font-mono">{row.value}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Risk Explanation */}
      {metrics.risk_explanation && (
        <div className="bg-slate-800/60 border border-slate-700/60 rounded-xl p-4">
          <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-widest mb-2">
            Scoring Rationale
          </h3>
          <p className="text-sm text-slate-300 leading-relaxed">{metrics.risk_explanation}</p>
        </div>
      )}
    </div>
  );
}

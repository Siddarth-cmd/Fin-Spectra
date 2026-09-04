"use client";

import React from "react";
import { GraphMetrics } from "@/lib/types";
import {
  GitBranch,
  Users,
  CreditCard,
  Smartphone,
  ArrowLeftRight,
  AlertTriangle,
  CheckCircle,
} from "lucide-react";

interface GraphMetricsPanelProps {
  metrics: GraphMetrics;
}

function Flag({
  active,
  label,
  severity = "high",
}: {
  active: boolean;
  label: string;
  severity?: "high" | "medium" | "low";
}) {
  const colors = {
    high: active ? "bg-red-400/10 border-red-500/40 text-red-300" : "bg-slate-700/30 border-slate-600/30 text-slate-500",
    medium: active ? "bg-amber-400/10 border-amber-500/40 text-amber-300" : "bg-slate-700/30 border-slate-600/30 text-slate-500",
    low: active ? "bg-cyan-400/10 border-cyan-500/40 text-cyan-300" : "bg-slate-700/30 border-slate-600/30 text-slate-500",
  };

  return (
    <div className={`flex items-center gap-2 rounded-lg border px-3 py-2 ${colors[severity]}`}>
      {active ? (
        <AlertTriangle className="w-3.5 h-3.5 flex-shrink-0" />
      ) : (
        <CheckCircle className="w-3.5 h-3.5 flex-shrink-0" />
      )}
      <span className="text-xs font-medium">{label}</span>
    </div>
  );
}

function RatioBar({ label, value, max = 1 }: { label: string; value: number; max?: number }) {
  const pct = Math.min((value / max) * 100, 100);
  const color = pct > 70 ? "bg-red-500" : pct > 40 ? "bg-amber-500" : "bg-emerald-500";

  return (
    <div>
      <div className="flex justify-between text-xs text-slate-400 mb-1">
        <span>{label}</span>
        <span className="font-mono font-bold text-white">{value.toFixed(2)}</span>
      </div>
      <div className="h-1.5 bg-slate-700 rounded-full overflow-hidden">
        <div className={`h-full rounded-full ${color}`} style={{ width: `${pct}%` }} />
      </div>
    </div>
  );
}

export function GraphMetricsPanel({ metrics }: GraphMetricsPanelProps) {
  if (!metrics) return null;

  const countCards = [
    { icon: <CreditCard className="w-4 h-4" />, label: "Accounts", value: metrics.account_count, color: "text-cyan-400" },
    { icon: <Users className="w-4 h-4" />, label: "Beneficiaries", value: metrics.beneficiary_count, color: "text-purple-400" },
    { icon: <Smartphone className="w-4 h-4" />, label: "Devices", value: metrics.device_count, color: "text-blue-400" },
    { icon: <ArrowLeftRight className="w-4 h-4" />, label: "Transactions", value: metrics.transaction_count, color: "text-emerald-400" },
  ];

  return (
    <div className="space-y-4">
      {/* Network topology counts */}
      <div className="grid grid-cols-4 gap-3">
        {countCards.map((c) => (
          <div key={c.label} className="bg-slate-800/60 border border-slate-700/60 rounded-xl p-3 text-center">
            <div className={`flex justify-center mb-1 ${c.color}`}>{c.icon}</div>
            <p className={`text-xl font-bold ${c.color}`}>{c.value}</p>
            <p className="text-xs text-slate-400">{c.label}</p>
          </div>
        ))}
      </div>

      {/* Ratio bars */}
      <div className="bg-slate-800/60 border border-slate-700/60 rounded-xl p-4 space-y-3">
        <div className="flex items-center gap-2 mb-1">
          <GitBranch className="w-4 h-4 text-cyan-400" />
          <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-widest">
            Network Ratios
          </h3>
        </div>
        <RatioBar label="Fan-In (Tx per Account)" value={metrics.fan_in_ratio} max={10} />
        <RatioBar label="Fan-Out (Beneficiary Dispersion)" value={metrics.fan_out_ratio} max={1} />
        <div className="flex justify-between text-xs text-slate-400 mt-1">
          <span>Unique Beneficiaries</span>
          <span className="font-mono font-bold text-white">{metrics.unique_beneficiaries}</span>
        </div>
      </div>

      {/* Suspicious flags */}
      <div className="bg-slate-800/60 border border-slate-700/60 rounded-xl p-4">
        <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-widest mb-3">
          Suspicious Flags
        </h3>
        <div className="space-y-2">
          <Flag
            active={metrics.self_transfer_detected}
            label="Self-Transfer / Circular Transaction Detected"
            severity="high"
          />
          <Flag
            active={metrics.multi_device_multi_beneficiary_flag}
            label="Multi-Device + Multi-Beneficiary (Shell Account Indicator)"
            severity="high"
          />
          <Flag
            active={metrics.multi_beneficiary_flag >= 2}
            label={`Multiple Beneficiaries (${metrics.beneficiary_count} registered)`}
            severity="medium"
          />
        </div>
      </div>
    </div>
  );
}

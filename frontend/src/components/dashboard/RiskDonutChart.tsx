"use client";

import React from "react";
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from "recharts";
import { Info } from "lucide-react";
import { PipelineSummary } from "@/lib/types";

interface RiskDonutChartProps {
  summary?: PipelineSummary;
}

const RISK_COLORS: Record<string, string> = {
  CRITICAL: "#F43F5E",
  HIGH: "#F59E0B",
  MEDIUM: "#EAB308",
  LOW: "#14B8A6",
};

export const RiskDonutChart: React.FC<RiskDonutChartProps> = ({ summary }) => {
  const [mounted, setMounted] = React.useState(false);

  React.useEffect(() => {
    setMounted(true);
  }, []);

  const riskCounts = summary?.classified_alerts_by_risk_level || {
    CRITICAL: 70,
    HIGH: 454,
    MEDIUM: 5890,
    LOW: 118,
  };

  const total =
    riskCounts.CRITICAL + riskCounts.HIGH + riskCounts.MEDIUM + riskCounts.LOW || 6532;
  const criticalAndHigh = riskCounts.CRITICAL + riskCounts.HIGH;

  const data = [
    { name: "CRITICAL", value: riskCounts.CRITICAL, color: RISK_COLORS.CRITICAL },
    { name: "HIGH", value: riskCounts.HIGH, color: RISK_COLORS.HIGH },
    { name: "MEDIUM", value: riskCounts.MEDIUM, color: RISK_COLORS.MEDIUM },
    { name: "LOW", value: riskCounts.LOW, color: RISK_COLORS.LOW },
  ];


  return (
    <div className="glass-card rounded-xl p-5 border border-cyan-500/15 flex flex-col justify-between h-full">
      <div>
        {/* Header */}
        <div className="flex items-start justify-between mb-4">
          <div>
            <div className="flex items-center space-x-1.5">
              <h2 className="text-sm font-bold text-white tracking-wide">
                Classified Alerts by Risk Level
              </h2>
              <Info className="w-3.5 h-3.5 text-slate-500 hover:text-slate-300 cursor-pointer" />
            </div>
            <p className="text-xs text-slate-400 mt-0.5">
              Real-time risk classification engine tiering
            </p>
          </div>
        </div>

        {/* Donut + Legend Layout */}
        <div className="grid grid-cols-1 sm:grid-cols-12 gap-4 items-center mt-2">
          {/* Donut Chart with Center Text */}
          <div className="sm:col-span-6 relative h-48 w-full flex items-center justify-center">
            {mounted ? (
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={data}
                    cx="50%"
                    cy="50%"
                    innerRadius={52}
                    outerRadius={74}
                    paddingAngle={3}
                    dataKey="value"
                    stroke="#080B11"
                    strokeWidth={2}
                  >
                    {data.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip
                    contentStyle={{
                      backgroundColor: "#0F1626",
                      borderColor: "rgba(34, 211, 238, 0.2)",
                      borderRadius: "8px",
                      color: "#F8FAFC",
                      fontSize: "12px",
                    }}
                    formatter={(value: any, name: any) => [
                      `${Number(value).toLocaleString()} alerts`,
                      name,
                    ]}
                  />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <div className="w-36 h-36 rounded-full border-4 border-slate-800 animate-pulse flex items-center justify-center" />
            )}
            {/* Center Label */}

            <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
              <span className="text-xl font-black text-white font-mono tracking-tight">
                {total.toLocaleString()}
              </span>
              <span className="text-[9px] font-extrabold uppercase tracking-widest text-slate-400 mt-0.5">
                TOTAL ALERTS
              </span>
            </div>
          </div>

          {/* Legend Items */}
          <div className="sm:col-span-6 space-y-2.5">
            {data.map((item) => {
              const pct = ((item.value / Math.max(1, total)) * 100).toFixed(1);
              return (
                <div
                  key={item.name}
                  className="flex items-center justify-between p-2 rounded-lg bg-slate-900/60 border border-slate-800/60 text-xs"
                >
                  <div className="flex items-center space-x-2">
                    <span
                      className="w-2.5 h-2.5 rounded-full"
                      style={{ backgroundColor: item.color }}
                    />
                    <span className="font-bold text-slate-200">{item.name}</span>
                  </div>
                  <div className="font-mono text-slate-300">
                    <span className="font-bold">{item.value.toLocaleString()}</span>{" "}
                    <span className="text-slate-500 text-[11px]">({pct}%)</span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* Footer */}
      <div className="mt-6 pt-3 border-t border-white/5 flex items-center justify-between text-[11px]">
        <div className="flex items-center space-x-1.5 text-rose-400 font-semibold">
          <span className="w-1.5 h-1.5 rounded-full bg-rose-400 animate-ping" />
          <span>{criticalAndHigh.toLocaleString()} require immediate human review</span>
        </div>
        <span className="text-slate-500">Auto-cleared: 0</span>
      </div>
    </div>
  );
};

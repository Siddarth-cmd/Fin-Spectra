import React from "react";
import { PipelineSummary } from "@/lib/types";

interface DetectionRuleChartProps {
  summary?: PipelineSummary;
}

const DEFAULT_RULE_ORDER = [
  "LARGE_AMOUNT",
  "FAN_IN",
  "FAN_OUT",
  "PASS_THROUGH",
  "STRUCTURING",
  "ROUND_AMOUNT",
  "HIGH_VELOCITY",
];

export const DetectionRuleChart: React.FC<DetectionRuleChartProps> = ({ summary }) => {
  const rawAlertsByRule = summary?.raw_alerts_by_rule || {};
  
  // Collect data for all rules
  const rulesData = DEFAULT_RULE_ORDER.map((ruleName) => {
    const count = rawAlertsByRule[ruleName] || 0;
    return { name: ruleName, count };
  });

  const totalTriggers = rulesData.reduce((acc, curr) => acc + curr.count, 0) || 1;
  const maxCount = Math.max(...rulesData.map((r) => r.count), 1);

  return (
    <div className="glass-card rounded-xl p-5 border border-cyan-500/15 flex flex-col justify-between h-full">
      <div>
        {/* Header */}
        <div className="flex items-start justify-between mb-4">
          <div>
            <h2 className="text-sm font-bold text-white tracking-wide">
              Raw Alerts by Detection Rule
            </h2>
            <p className="text-xs text-slate-400 mt-0.5">
              Distribution Across 7 Signatures
            </p>
          </div>
          <span className="px-2 py-0.5 rounded text-[9px] font-extrabold uppercase tracking-wider bg-blue-950/80 text-blue-300 border border-blue-400/30">
            RULE ENGINE V3.1
          </span>
        </div>

        {/* Rule Bars List */}
        <div className="space-y-3 mt-4">
          {rulesData.map((rule) => {
            const pct = ((rule.count / totalTriggers) * 100).toFixed(1);
            const barWidth = Math.max(4, Math.round((rule.count / maxCount) * 100));

            return (
              <div key={rule.name} className="group">
                <div className="flex items-center justify-between text-xs mb-1">
                  <span className="font-mono text-[11px] font-semibold text-slate-300 group-hover:text-cyan-300 transition-colors">
                    {rule.name}
                  </span>
                  <div className="font-mono text-[11px] text-slate-400">
                    <span className="text-slate-200 font-bold">{rule.count.toLocaleString()}</span>
                    <span className="text-slate-500 mx-1.5">•</span>
                    <span className="text-slate-400">{pct}%</span>
                  </div>
                </div>
                {/* Bar track */}
                <div className="w-full h-2 rounded-full bg-slate-900 border border-slate-800/80 overflow-hidden relative">
                  <div
                    className="h-full rounded-full bg-gradient-to-r from-cyan-500 via-blue-500 to-indigo-500 transition-all duration-500 shadow-glow-cyan"
                    style={{ width: `${barWidth}%` }}
                  />
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Footer */}
      <div className="mt-6 pt-3 border-t border-white/5 flex items-center justify-between text-[11px] text-slate-400">
        <span>Aggregation window: Past 24 hours</span>
        <span className="px-2 py-0.5 rounded bg-cyan-950/60 text-cyan-300 border border-cyan-500/30 font-semibold font-mono">
          Sum: {totalTriggers.toLocaleString()} Triggers
        </span>
      </div>
    </div>
  );
};

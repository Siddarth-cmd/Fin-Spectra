import React from "react";
import { Building2, ArrowDownUp, BellRing, AlertOctagon, TrendingUp } from "lucide-react";
import { PipelineSummary } from "@/lib/types";

interface KpiCardsProps {
  summary?: PipelineSummary;
}

export const KpiCards: React.FC<KpiCardsProps> = ({ summary }) => {
  const accountsIngested = summary?.accounts_ingested ?? 20000;
  const txIngested = summary?.transactions_ingested ?? 15000;
  const rawAlerts = summary?.raw_alerts_generated ?? 5000;
  const accountsWithAlerts = summary?.accounts_with_alerts ?? 100;

  const triggerRate = ((rawAlerts / Math.max(1, txIngested)) * 100).toFixed(2);
  const cohortFlaggedRate = ((accountsWithAlerts / Math.max(1, accountsIngested)) * 100).toFixed(2);


  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
      {/* Card 1: Accounts Ingested */}
      <div className="glass-card rounded-xl p-4 border border-cyan-500/15 relative overflow-hidden group">
        <div className="flex items-start justify-between">
          <span className="text-[10px] font-bold tracking-widest uppercase text-slate-400">
            ACCOUNTS INGESTED
          </span>
          <div className="w-8 h-8 rounded-full bg-cyan-950/70 border border-cyan-400/30 flex items-center justify-center text-cyan-400 shadow-glow-cyan">
            <Building2 className="w-4 h-4" />
          </div>
        </div>
        <div className="mt-3">
          <div className="text-3xl font-black text-white tracking-tight font-mono">
            {accountsIngested.toLocaleString()}
          </div>
          <div className="flex items-center space-x-1.5 mt-2 text-xs font-semibold text-cyan-400">
            <TrendingUp className="w-3.5 h-3.5" />
            <span>+100% cohort target</span>
          </div>
        </div>
      </div>

      {/* Card 2: Transactions Ingested */}
      <div className="glass-card rounded-xl p-4 border border-blue-500/15 relative overflow-hidden group">
        <div className="flex items-start justify-between">
          <span className="text-[10px] font-bold tracking-widest uppercase text-slate-400">
            TRANSACTIONS INGESTED
          </span>
          <div className="w-8 h-8 rounded-full bg-blue-950/70 border border-blue-400/30 flex items-center justify-center text-blue-400 shadow-glow">
            <ArrowDownUp className="w-4 h-4" />
          </div>
        </div>
        <div className="mt-3">
          <div className="text-3xl font-black text-white tracking-tight font-mono">
            {txIngested.toLocaleString()}
          </div>
          <div className="flex items-center space-x-1.5 mt-2 text-xs font-semibold text-blue-400">
            <TrendingUp className="w-3.5 h-3.5" />
            <span>+12.4% vs prev run</span>
          </div>
        </div>
      </div>

      {/* Card 3: Raw Alerts Generated */}
      <div className="glass-card rounded-xl p-4 border border-amber-500/15 relative overflow-hidden group">
        <div className="flex items-start justify-between">
          <span className="text-[10px] font-bold tracking-widest uppercase text-slate-400">
            RAW ALERTS GENERATED
          </span>
          <div className="w-8 h-8 rounded-full bg-amber-950/70 border border-amber-400/30 flex items-center justify-center text-amber-400 shadow-glow-amber">
            <BellRing className="w-4 h-4" />
          </div>
        </div>
        <div className="mt-3">
          <div className="text-3xl font-black text-white tracking-tight font-mono">
            {rawAlerts.toLocaleString()}
          </div>
          <div className="flex items-center space-x-1.5 mt-2 text-xs font-semibold text-amber-400">
            <span>{triggerRate}% trigger rate</span>
            <span className="text-slate-500">•</span>
            <span className="text-slate-400 font-normal">7 models</span>
          </div>
        </div>
      </div>

      {/* Card 4: Accounts With Alerts */}
      <div className="glass-card rounded-xl p-4 border border-rose-500/15 relative overflow-hidden group">
        <div className="flex items-start justify-between">
          <span className="text-[10px] font-bold tracking-widest uppercase text-slate-400">
            ACCOUNTS WITH ALERTS
          </span>
          <div className="w-8 h-8 rounded-full bg-rose-950/70 border border-rose-400/30 flex items-center justify-center text-rose-400 shadow-glow-rose">
            <AlertOctagon className="w-4 h-4" />
          </div>
        </div>
        <div className="mt-3">
          <div className="text-3xl font-black text-white tracking-tight font-mono">
            {accountsWithAlerts.toLocaleString()}
          </div>
          <div className="flex items-center space-x-1.5 mt-2 text-xs font-semibold text-rose-400">
            <span>{cohortFlaggedRate}% cohort flagged</span>
            <span className="text-slate-500">•</span>
            <span className="text-slate-400 font-normal">high risk</span>
          </div>
        </div>
      </div>
    </div>
  );
};

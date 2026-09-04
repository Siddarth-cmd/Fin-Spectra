import React from "react";
import { Database, ArrowRightLeft, ShieldAlert, ArrowRight } from "lucide-react";
import { PipelineSummary } from "@/lib/types";

interface PipelineFlowStripProps {
  summary?: PipelineSummary;
}

export const PipelineFlowStrip: React.FC<PipelineFlowStripProps> = ({ summary }) => {
  const accountsCount = summary?.accounts_ingested?.toLocaleString() || "20,000";
  const txCount = summary?.transactions_ingested?.toLocaleString() || "15,000";
  const rawAlertsCount = summary?.raw_alerts_generated?.toLocaleString() || "5,000";


  return (
    <div className="w-full glass-card rounded-xl p-3 border border-cyan-500/15 mb-6">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-3 items-center">
        {/* Node 1: AML Data Ingestion */}
        <div className="relative flex items-center space-x-3.5 p-3 rounded-lg bg-[#0C121E]/90 border border-white/5 hover:border-cyan-500/20 transition-all">
          <div className="w-10 h-10 rounded-lg bg-cyan-950/80 border border-cyan-400/30 flex items-center justify-center text-cyan-400 shadow-glow-cyan flex-shrink-0">
            <Database className="w-5 h-5" />
          </div>
          <div className="min-w-0 flex-1">
            <div className="flex items-center space-x-2">
              <span className="text-xs font-bold text-slate-100 tracking-wide truncate">
                AMLData Ingest
              </span>
              <span className="px-1.5 py-0.5 rounded text-[9px] font-extrabold uppercase tracking-wider bg-teal-950/80 text-teal-300 border border-teal-500/30">
                100% INGESTED
              </span>
            </div>
            <div className="text-[11px] text-slate-400 mt-0.5 font-medium">
              {accountsCount} accounts processed
            </div>
          </div>
          <div className="hidden md:block absolute -right-3 top-1/2 -translate-y-1/2 z-10">
            <div className="w-6 h-6 rounded-full bg-[#080B11] border border-cyan-500/30 flex items-center justify-center text-cyan-400">
              <ArrowRight className="w-3 h-3" />
            </div>
          </div>
        </div>

        {/* Node 2: Transaction Monitor */}
        <div className="relative flex items-center space-x-3.5 p-3 rounded-lg bg-[#0C121E]/90 border border-white/5 hover:border-blue-500/20 transition-all">
          <div className="w-10 h-10 rounded-lg bg-blue-950/80 border border-blue-400/30 flex items-center justify-center text-blue-400 shadow-glow flex-shrink-0">
            <ArrowRightLeft className="w-5 h-5" />
          </div>
          <div className="min-w-0 flex-1">
            <div className="flex items-center space-x-2">
              <span className="text-xs font-bold text-slate-100 tracking-wide truncate">
                TransactionMonitor
              </span>
              <span className="px-1.5 py-0.5 rounded text-[9px] font-extrabold uppercase tracking-wider bg-blue-950/80 text-blue-300 border border-blue-500/30">
                SYNCED
              </span>
            </div>
            <div className="text-[11px] text-slate-400 mt-0.5 font-medium">
              {txCount} records evaluated
            </div>
          </div>
          <div className="hidden md:block absolute -right-3 top-1/2 -translate-y-1/2 z-10">
            <div className="w-6 h-6 rounded-full bg-[#080B11] border border-cyan-500/30 flex items-center justify-center text-cyan-400">
              <ArrowRight className="w-3 h-3" />
            </div>
          </div>
        </div>

        {/* Node 3: Alert Classification */}
        <div className="flex items-center space-x-3.5 p-3 rounded-lg bg-[#0C121E]/90 border border-white/5 hover:border-rose-500/20 transition-all">
          <div className="w-10 h-10 rounded-lg bg-rose-950/80 border border-rose-400/30 flex items-center justify-center text-rose-400 shadow-glow-rose flex-shrink-0">
            <ShieldAlert className="w-5 h-5" />
          </div>
          <div className="min-w-0 flex-1">
            <div className="flex items-center space-x-2">
              <span className="text-xs font-bold text-slate-100 tracking-wide truncate">
                Alert Classification
              </span>
              <span className="px-1.5 py-0.5 rounded text-[9px] font-extrabold uppercase tracking-wider bg-rose-950/80 text-rose-300 border border-rose-500/30">
                ACTIVE
              </span>
            </div>
            <div className="text-[11px] text-slate-400 mt-0.5 font-medium">
              {rawAlertsCount} raw alerts triaged
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

"use client";

import React, { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Loader, ExternalLink, ShieldCheck } from "lucide-react";
import { fetchInvestigations } from "@/lib/api";
import { InvestigationCase } from "@/lib/types";

export default function InvestigationsListPage() {
  const router = useRouter();
  const [cases, setCases] = useState<InvestigationCase[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const data = await fetchInvestigations();
        setCases(data);
      } catch (err) {
        console.error("Error loading cases:", err);
      } finally {
        setIsLoading(false);
      }
    }
    load();
  }, []);

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center space-x-3">
            <h1 className="text-xl font-bold text-white tracking-tight">
              Investigation Cases
            </h1>
          </div>
          <p className="text-xs text-slate-400 mt-1 leading-relaxed">
            View all multi-agent investigations and their findings.
          </p>
        </div>
      </div>

      <div className="glass-card rounded-xl p-5 border border-cyan-500/15 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse min-w-[800px]">
            <thead>
              <tr className="border-b border-white/5 text-[10px] font-bold uppercase tracking-widest text-slate-400">
                <th className="py-3 px-3">Case ID</th>
                <th className="py-3 px-3">Alert ID</th>
                <th className="py-3 px-3">Entity Ref</th>
                <th className="py-3 px-3">Status</th>
                <th className="py-3 px-3">Decision</th>
                <th className="py-3 px-3">Score</th>
                <th className="py-3 px-3 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/5 text-xs">
              {isLoading ? (
                <tr>
                  <td colSpan={7} className="py-16 text-center text-slate-400">
                    <div className="inline-block animate-spin rounded-full h-6 w-6 border-2 border-cyan-500 border-t-transparent mb-2" />
                    <div>Loading cases...</div>
                  </td>
                </tr>
              ) : cases.length === 0 ? (
                <tr>
                  <td colSpan={7} className="py-16 text-center text-slate-400">
                    No investigations found. Go to the Alert Queue to start an investigation.
                  </td>
                </tr>
              ) : (
                cases.map((c) => (
                  <tr
                    key={c.id}
                    onClick={() => router.push(`/investigations/${c.id}`)}
                    className="hover:bg-cyan-950/20 cursor-pointer transition-colors group"
                  >
                    <td className="py-3.5 px-3 font-mono font-bold text-cyan-400 group-hover:underline">
                      {c.id}
                    </td>
                    <td className="py-3.5 px-3 font-mono text-slate-300">
                      {c.alert_id}
                    </td>
                    <td className="py-3.5 px-3 font-mono text-slate-300">
                      {c.entity_id}
                    </td>
                    <td className="py-3.5 px-3">
                      <span className="px-2 py-0.5 rounded text-[9px] font-bold tracking-wider uppercase bg-teal-950/70 text-teal-300 border border-teal-500/30">
                        {c.status || "OPEN"}
                      </span>
                    </td>
                    <td className="py-3.5 px-3 font-bold">
                      <span className={
                        c.decision === "BLOCK" ? "text-red-400" :
                        c.decision === "REVIEW" ? "text-amber-400" :
                        c.decision === "ALLOW" ? "text-emerald-400" : "text-slate-400"
                      }>
                        {c.decision || "—"}
                      </span>
                    </td>
                    <td className="py-3.5 px-3 font-mono font-bold">
                      {c.score !== undefined && c.score !== null ? c.score.toFixed(1) : "—"}
                    </td>
                    <td className="py-3.5 px-3 text-right">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          router.push(`/investigations/${c.id}`);
                        }}
                        className="inline-flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-cyan-400 text-xs font-bold transition-all border border-cyan-500/30"
                      >
                        <ExternalLink className="w-3.5 h-3.5" />
                        <span>View</span>
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

"use client";

import React from "react";
import { EvidenceSummary, LedgerEntry } from "@/lib/types";
import { ArrowDownLeft, ArrowUpRight, FileSearch, AlertTriangle } from "lucide-react";

interface EvidenceWorkspaceProps {
  evidenceSummary: EvidenceSummary;
}

function formatCurrency(v: number) {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 2,
  }).format(v);
}

function formatTime(iso: string) {
  if (!iso) return "—";
  try {
    return new Date(iso).toLocaleString("en-US", {
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  } catch {
    return iso;
  }
}

export function EvidenceWorkspace({ evidenceSummary }: EvidenceWorkspaceProps) {
  const { ledger_history, kyc_notes, missing_evidence, balance_history, ledger_count, historical_cases_count } =
    (evidenceSummary as any) || {};

  const ledger: LedgerEntry[] = ledger_history || [];
  const missing: string[] = (evidenceSummary as any)?.missing_evidence || [];

  return (
    <div className="space-y-4">
      {/* KYC Notes */}
      <div className="bg-slate-800/60 border border-slate-700/60 rounded-xl p-4">
        <div className="flex items-center gap-2 mb-3">
          <FileSearch className="w-4 h-4 text-cyan-400" />
          <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-widest">
            KYC Intelligence
          </h3>
        </div>
        {kyc_notes ? (
          <div className="space-y-2">
            {kyc_notes.split("||").map((part: string, i: number) => (
              <p
                key={i}
                className={`text-sm ${
                  part.includes("ALERT")
                    ? "text-amber-300 bg-amber-400/10 border border-amber-500/30 rounded-lg px-3 py-2"
                    : "text-slate-300"
                }`}
              >
                {part.trim()}
              </p>
            ))}
          </div>
        ) : (
          <p className="text-slate-500 text-sm">KYC data not yet collected</p>
        )}
      </div>

      {/* Balance & Account Summary */}
      {balance_history && (
        <div className="grid grid-cols-3 gap-3">
          <div className="bg-slate-800/60 border border-slate-700/60 rounded-xl p-3">
            <p className="text-xs text-slate-400 mb-1">Primary Account</p>
            <p className="text-sm font-mono font-semibold text-white">
              {balance_history.primary_account_id || "—"}
            </p>
          </div>
          <div className="bg-slate-800/60 border border-slate-700/60 rounded-xl p-3">
            <p className="text-xs text-slate-400 mb-1">Account Status</p>
            <p className="text-sm font-semibold text-white">
              {balance_history.account_status || "—"}
            </p>
          </div>
          <div className="bg-slate-800/60 border border-slate-700/60 rounded-xl p-3">
            <p className="text-xs text-slate-400 mb-1">Historical Cases</p>
            <p className="text-sm font-semibold text-white">{historical_cases_count ?? 0}</p>
          </div>
        </div>
      )}

      {/* Missing Evidence */}
      {missing.length > 0 && (
        <div className="bg-amber-400/10 border border-amber-500/30 rounded-xl p-4">
          <div className="flex items-center gap-2 mb-2">
            <AlertTriangle className="w-4 h-4 text-amber-400" />
            <h3 className="text-xs font-semibold text-amber-400 uppercase tracking-widest">
              Missing Evidence ({missing.length})
            </h3>
          </div>
          <ul className="space-y-1">
            {missing.map((m, i) => (
              <li key={i} className="text-sm text-amber-300 font-mono">
                ⚠ {m}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Transaction Ledger */}
      <div className="bg-slate-800/60 border border-slate-700/60 rounded-xl overflow-hidden">
        <div className="px-4 py-3 border-b border-slate-700/60 flex items-center justify-between">
          <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-widest">
            Transaction Ledger
          </h3>
          <span className="text-xs text-slate-500">{ledger_count ?? ledger.length} records</span>
        </div>

        {ledger.length === 0 ? (
          <p className="text-slate-500 text-sm text-center py-6">
            No ledger records collected yet
          </p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-slate-700/40">
                  <th className="text-left text-xs text-slate-400 px-4 py-2 font-medium">ID</th>
                  <th className="text-left text-xs text-slate-400 px-4 py-2 font-medium">Dir</th>
                  <th className="text-right text-xs text-slate-400 px-4 py-2 font-medium">Amount</th>
                  <th className="text-left text-xs text-slate-400 px-4 py-2 font-medium">Channel</th>
                  <th className="text-left text-xs text-slate-400 px-4 py-2 font-medium">Time</th>
                </tr>
              </thead>
              <tbody>
                {ledger.map((entry, i) => (
                  <tr
                    key={i}
                    className="border-b border-slate-700/20 hover:bg-slate-700/20 transition-colors"
                  >
                    <td className="px-4 py-2 font-mono text-xs text-slate-300">
                      {entry.id}
                    </td>
                    <td className="px-4 py-2">
                      <span
                        className={`flex items-center gap-1 text-xs font-semibold ${
                          entry.dir === "IN"
                            ? "text-emerald-400"
                            : "text-red-400"
                        }`}
                      >
                        {entry.dir === "IN" ? (
                          <ArrowDownLeft className="w-3 h-3" />
                        ) : (
                          <ArrowUpRight className="w-3 h-3" />
                        )}
                        {entry.dir}
                      </span>
                    </td>
                    <td className="px-4 py-2 text-right font-semibold text-white">
                      {formatCurrency(entry.amount)}
                    </td>
                    <td className="px-4 py-2 text-xs text-slate-400 font-mono">
                      {entry.channel}
                    </td>
                    <td className="px-4 py-2 text-xs text-slate-400">
                      {formatTime(entry.time)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}

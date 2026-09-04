"use client";

import React, { useState } from "react";
import { Search, Download, ChevronLeft, ChevronRight } from "lucide-react";
import { ClassifiedAlert, RiskLevel } from "@/lib/types";
import { RiskBadge } from "@/components/common/RiskBadge";

interface AlertQueueTableProps {
  alerts: ClassifiedAlert[];
  totalAlerts: number;
  page: number;
  pageSize: number;
  totalPages: number;
  selectedRiskLevels: string[];
  searchQuery: string;
  onPageChange: (newPage: number) => void;
  onRiskFilterToggle: (risk: string) => void;
  onSearchChange: (query: string) => void;
  onSelectAlert: (alert: ClassifiedAlert) => void;
  isLoading?: boolean;
}

const RISK_LEVELS: { label: string; value: RiskLevel; colorClass: string; activeClass: string }[] = [
  {
    label: "CRITICAL",
    value: "CRITICAL",
    colorClass: "border-rose-500/30 text-rose-400 hover:bg-rose-950/40",
    activeClass: "bg-rose-950/80 border-rose-500 text-rose-300 shadow-glow-rose font-bold",
  },
  {
    label: "HIGH",
    value: "HIGH",
    colorClass: "border-amber-500/30 text-amber-400 hover:bg-amber-950/40",
    activeClass: "bg-amber-950/80 border-amber-500 text-amber-300 shadow-glow-amber font-bold",
  },
  {
    label: "MEDIUM",
    value: "MEDIUM",
    colorClass: "border-yellow-500/30 text-yellow-400 hover:bg-yellow-950/40",
    activeClass: "bg-yellow-950/80 border-yellow-500 text-yellow-300 shadow-glow-yellow font-bold",
  },
  {
    label: "LOW",
    value: "LOW",
    colorClass: "border-teal-500/30 text-teal-400 hover:bg-teal-950/40",
    activeClass: "bg-teal-950/80 border-teal-500 text-teal-300 shadow-glow-teal font-bold",
  },
];

export const AlertQueueTable: React.FC<AlertQueueTableProps> = ({
  alerts,
  totalAlerts,
  page,
  pageSize,
  totalPages,
  selectedRiskLevels,
  searchQuery,
  onPageChange,
  onRiskFilterToggle,
  onSearchChange,
  onSelectAlert,
  isLoading = false,
}) => {
  const [searchInput, setSearchInput] = useState(searchQuery);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSearchChange(searchInput);
  };

  const handleExportCsv = () => {
    if (!alerts || alerts.length === 0) return;
    const headers = [
      "classified_alert_id",
      "account_id",
      "risk_level",
      "risk_score",
      "alert_type",
      "triggered_rules",
      "detected_reason",
      "timestamp",
      "status",
    ];

    const csvRows = [
      headers.join(","),
      ...alerts.map((a) =>
        [
          `"${a.classified_alert_id ?? a.alert_id ?? ""}"`,
          `"${a.account_id ?? a.transaction?.account_id ?? ""}"`,
          `"${a.risk_level}"`,
          a.risk_score,
          `"${a.alert_type}"`,
          `"${(a.triggered_rules ?? [a.alert_type]).join(";")}"`,
          `"${(a.detected_reason ?? a.alert_type ?? "").replace(/"/g, '""')}"`,
          `"${a.timestamp ?? a.created_at ?? ""}"`,
          `"${a.status ?? ""}"`,
        ].join(",")
      ),
    ];

    const blob = new Blob([csvRows.join("\n")], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.setAttribute("href", url);
    link.setAttribute("download", `finspectra_alerts_p${page}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const startIdx = totalAlerts === 0 ? 0 : (page - 1) * pageSize + 1;
  const endIdx = Math.min(page * pageSize, totalAlerts);

  const getScoreBarColor = (score: number) => {
    if (score >= 90) return "bg-rose-500 shadow-glow-rose";
    if (score >= 70) return "bg-amber-500 shadow-glow-amber";
    if (score >= 40) return "bg-yellow-500 shadow-glow-yellow";
    return "bg-teal-500 shadow-glow-teal";
  };

  return (
    <div className="glass-card rounded-xl p-5 border border-cyan-500/15">
      {/* Header & Controls */}
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 pb-4 border-b border-white/5">
        <div>
          <div className="flex items-center space-x-2.5">
            <h2 className="text-sm font-bold text-white tracking-wide">
              Alert Classification — Prioritized Alert Queue
            </h2>
            <span className="px-2 py-0.5 rounded text-[9px] font-extrabold uppercase tracking-wider bg-teal-950/80 text-teal-300 border border-teal-500/30">
              LIVE PROD
            </span>
          </div>
          <p className="text-xs text-slate-400 mt-0.5">
            Showing Urgent Triage Cases requiring tier-1 escalation
          </p>
        </div>

        {/* Right Filter Chips, Search, Export */}
        <div className="flex flex-wrap items-center gap-2.5">
          {/* Risk Filters */}
          <div className="flex items-center space-x-1.5 bg-slate-900/60 p-1 rounded-lg border border-slate-800">
            {RISK_LEVELS.map((lvl) => {
              const isSelected = selectedRiskLevels.includes(lvl.value);
              return (
                <button
                  key={lvl.value}
                  onClick={() => onRiskFilterToggle(lvl.value)}
                  className={`px-2 py-1 rounded text-[10px] uppercase tracking-wider border transition-all flex items-center space-x-1 ${
                    isSelected ? lvl.activeClass : "border-transparent text-slate-400 hover:text-slate-200"
                  }`}
                >
                  <span
                    className={`w-1.5 h-1.5 rounded-full ${
                      lvl.value === "CRITICAL"
                        ? "bg-rose-400"
                        : lvl.value === "HIGH"
                        ? "bg-amber-400"
                        : lvl.value === "MEDIUM"
                        ? "bg-yellow-400"
                        : "bg-teal-400"
                    }`}
                  />
                  <span>{lvl.label}</span>
                </button>
              );
            })}
          </div>

          {/* Search Input */}
          <form onSubmit={handleSearchSubmit} className="relative">
            <Search className="w-3.5 h-3.5 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Search hash, account ID"
              value={searchInput}
              onChange={(e) => setSearchInput(e.target.value)}
              onBlur={() => onSearchChange(searchInput)}
              className="pl-8 pr-3 py-1.5 text-xs bg-slate-900/80 border border-slate-700/60 rounded-lg text-slate-200 placeholder-slate-500 focus:outline-none focus:border-cyan-400 focus:ring-1 focus:ring-cyan-400 w-48 sm:w-56"
            />
          </form>

          {/* Export CSV */}
          <button
            onClick={handleExportCsv}
            className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-cyan-950/50 hover:bg-cyan-900/60 border border-cyan-500/30 text-cyan-300 text-xs font-semibold transition-colors"
          >
            <Download className="w-3.5 h-3.5" />
            <span>Export CSV</span>
          </button>
        </div>
      </div>

      {/* Table */}
      <div className="overflow-x-auto mt-4">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="border-b border-white/5 text-[10px] font-bold uppercase tracking-widest text-slate-400">
              <th className="py-3 px-3">ALERT ID</th>
              <th className="py-3 px-3">ACCOUNT</th>
              <th className="py-3 px-3">RISK</th>
              <th className="py-3 px-3">RISK SCORE</th>
              <th className="py-3 px-3">ALERT TYPE</th>
              <th className="py-3 px-3">TRIGGERED RULES</th>
              <th className="py-3 px-3">DETECTED REASON</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-white/5 text-xs">
            {isLoading ? (
              <tr>
                <td colSpan={7} className="py-12 text-center text-slate-400">
                  <div className="inline-block animate-spin rounded-full h-6 w-6 border-2 border-cyan-500 border-t-transparent mb-2" />
                  <div>Loading prioritized alerts...</div>
                </td>
              </tr>
            ) : alerts.length === 0 ? (
              <tr>
                <td colSpan={7} className="py-12 text-center text-slate-400">
                  No alerts found matching the selected filters.
                </td>
              </tr>
            ) : (
              alerts.map((alert) => {
                const id = alert.classified_alert_id ?? alert.alert_id ?? "";
                const formattedId = id.startsWith("#")
                  ? id
                  : `#${id.replace("CALERT-", "ALT-")}`;

                return (
                  <tr
                    key={alert.classified_alert_id}
                    onClick={() => onSelectAlert(alert)}
                    className="hover:bg-cyan-950/20 cursor-pointer transition-colors group"
                  >
                    {/* Alert ID */}
                    <td className="py-3.5 px-3 font-mono text-cyan-400 font-bold group-hover:underline">
                      {formattedId}
                    </td>

                    {/* Account ID */}
                    <td className="py-3.5 px-3 font-mono text-slate-200">
                      {(alert.account_id ?? alert.transaction?.account_id ?? "—").replace("ACC", "ACCT-")}
                    </td>

                    {/* Risk Badge */}
                    <td className="py-3.5 px-3">
                      <RiskBadge level={alert.risk_level} />
                    </td>

                    {/* Risk Score */}
                    <td className="py-3.5 px-3">
                      <div className="flex items-center space-x-2">
                        <span className="font-mono font-bold text-slate-100 w-6">
                          {alert.risk_score}
                        </span>
                        <div className="w-16 h-1.5 rounded-full bg-slate-900 overflow-hidden">
                          <div
                            className={`h-full rounded-full ${getScoreBarColor(alert.risk_score)}`}
                            style={{ width: `${Math.min(100, alert.risk_score)}%` }}
                          />
                        </div>
                      </div>
                    </td>

                    {/* Alert Type */}
                    <td className="py-3.5 px-3 font-medium text-slate-200">
                      {alert.alert_type}
                    </td>

                    {/* Triggered Rules */}
                    <td className="py-3.5 px-3">
                      <div className="flex flex-wrap items-center gap-1">
                        {(alert.triggered_rules ?? [alert.alert_type]).slice(0, 2).map((rule) => (
                          <span
                            key={rule}
                            className="px-1.5 py-0.5 rounded text-[9px] font-mono font-bold bg-slate-800/80 text-slate-300 border border-slate-700/60"
                          >
                            {rule}
                          </span>
                        ))}
                        {(alert.triggered_rules ?? []).length > 2 && (
                          <span className="px-1 py-0.5 rounded text-[9px] font-mono bg-slate-800 text-cyan-300 border border-slate-700/60 font-semibold">
                            +{(alert.triggered_rules ?? []).length - 2}
                          </span>
                        )}
                      </div>
                    </td>

                    {/* Detected Reason */}
                    <td className="py-3.5 px-3 text-slate-300 text-[11px] max-w-xs truncate">
                      {alert.detected_reason ?? alert.alert_type}
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>

      {/* Footer / Pagination */}
      <div className="mt-4 pt-3 border-t border-white/5 flex flex-col sm:flex-row items-center justify-between gap-3 text-xs text-slate-400">
        <div>
          Showing <span className="font-bold text-slate-200">{startIdx}-{endIdx}</span> of{" "}
          <span className="font-bold text-slate-200">{totalAlerts}</span> prioritized alerts
        </div>

        {/* Pagination Buttons */}
        <div className="flex items-center space-x-1">
          <button
            onClick={() => onPageChange(Math.max(1, page - 1))}
            disabled={page <= 1}
            className="px-2.5 py-1 rounded bg-slate-900/60 border border-slate-800 text-slate-400 hover:text-slate-200 hover:border-slate-700 disabled:opacity-40 disabled:hover:text-slate-400 flex items-center space-x-1"
          >
            <ChevronLeft className="w-3.5 h-3.5" />
            <span>Previous</span>
          </button>

          {/* Page numbers */}
          {page > 2 && (
            <button
              onClick={() => onPageChange(1)}
              className="px-2.5 py-1 rounded bg-slate-900/60 border border-slate-800 text-slate-300 hover:border-cyan-500/40"
            >
              1
            </button>
          )}

          {page > 3 && <span className="px-1 text-slate-600">...</span>}

          {page > 1 && (
            <button
              onClick={() => onPageChange(page - 1)}
              className="px-2.5 py-1 rounded bg-slate-900/60 border border-slate-800 text-slate-300 hover:border-cyan-500/40"
            >
              {page - 1}
            </button>
          )}

          <button className="px-2.5 py-1 rounded bg-cyan-500 text-black font-bold shadow-glow-cyan">
            {page}
          </button>

          {page < totalPages && (
            <button
              onClick={() => onPageChange(page + 1)}
              className="px-2.5 py-1 rounded bg-slate-900/60 border border-slate-800 text-slate-300 hover:border-cyan-500/40"
            >
              {page + 1}
            </button>
          )}

          {page < totalPages - 2 && <span className="px-1 text-slate-600">...</span>}

          {page < totalPages - 1 && (
            <button
              onClick={() => onPageChange(totalPages)}
              className="px-2.5 py-1 rounded bg-slate-900/60 border border-slate-800 text-slate-300 hover:border-cyan-500/40"
            >
              {totalPages}
            </button>
          )}

          <button
            onClick={() => onPageChange(Math.min(totalPages, page + 1))}
            disabled={page >= totalPages}
            className="px-2.5 py-1 rounded bg-slate-900/60 border border-slate-800 text-slate-400 hover:text-slate-200 hover:border-slate-700 disabled:opacity-40 disabled:hover:text-slate-400 flex items-center space-x-1"
          >
            <span>Next</span>
            <ChevronRight className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>
    </div>
  );
};

"use client";

import React, { useEffect, useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import {
  Search,
  RotateCcw,
  ExternalLink,
  ChevronLeft,
  ChevronRight,
  ShieldAlert,
  ArrowUpDown,
  Filter,
} from "lucide-react";
import { fetchAlerts } from "@/lib/api";
import { ClassifiedAlert, RiskLevel } from "@/lib/types";
import { RiskBadge } from "@/components/common/RiskBadge";
import { AlertSlideOver } from "@/components/alert-detail/AlertSlideOver";

const TYPOLOGY_OPTIONS = [
  { label: "All Typologies", value: "ALL" },
  { label: "Large Amount", value: "LARGE_AMOUNT" },
  { label: "Fan-In Aggregation", value: "FAN_IN" },
  { label: "Fan-Out Dispersion", value: "FAN_OUT" },
  { label: "Pass-Through Layering", value: "PASS_THROUGH" },
  { label: "Structuring (Smurfing)", value: "STRUCTURING" },
  { label: "Round Amount Abuse", value: "ROUND_AMOUNT" },
  { label: "High Velocity Flow", value: "HIGH_VELOCITY" },
];

const SEVERITY_OPTIONS: { label: string; value: string }[] = [
  { label: "All Severities", value: "ALL" },
  { label: "Critical", value: "CRITICAL" },
  { label: "High", value: "HIGH" },
  { label: "Medium", value: "MEDIUM" },
  { label: "Low", value: "LOW" },
];

const STATUS_OPTIONS = [
  { label: "All Statuses", value: "ALL" },
  { label: "New", value: "NEW" },
  { label: "Triaged", value: "TRIAGED" },
  { label: "Pending Review", value: "PENDING" },
];

export default function AlertQueuePage() {
  const router = useRouter();

  // State
  const [alerts, setAlerts] = useState<ClassifiedAlert[]>([]);
  const [totalAlerts, setTotalAlerts] = useState(0);
  const [totalPages, setTotalPages] = useState(1);
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);

  // Filters
  const [searchQuery, setSearchQuery] = useState("");
  const [searchInput, setSearchInput] = useState("");
  const [selectedSeverity, setSelectedSeverity] = useState("ALL");
  const [selectedTypology, setSelectedTypology] = useState("ALL");
  const [selectedStatus, setSelectedStatus] = useState("ALL");

  // Interaction
  const [selectedAlert, setSelectedAlert] = useState<ClassifiedAlert | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Load Alerts from API
  const loadAlerts = useCallback(async () => {
    try {
      setIsLoading(true);
      const data = await fetchAlerts({
        risk_level: selectedSeverity !== "ALL" ? selectedSeverity : undefined,
        typology: selectedTypology !== "ALL" ? selectedTypology : undefined,
        status: selectedStatus !== "ALL" ? selectedStatus : undefined,
        search: searchQuery || undefined,
        page,
        page_size: pageSize,
      });

      setAlerts(data.alerts);
      setTotalAlerts(data.total);
      setTotalPages(data.total_pages);
    } catch (err) {
      console.error("Error loading alert queue:", err);
    } finally {
      setIsLoading(false);
    }
  }, [selectedSeverity, selectedTypology, selectedStatus, searchQuery, page, pageSize]);

  useEffect(() => {
    loadAlerts();
  }, [loadAlerts]);

  // Handle Search Submission
  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setPage(1);
    setSearchQuery(searchInput);
  };

  // Reset Filters
  const handleResetFilters = () => {
    setSearchInput("");
    setSearchQuery("");
    setSelectedSeverity("ALL");
    setSelectedTypology("ALL");
    setSelectedStatus("ALL");
    setPage(1);
  };

  const startIdx = totalAlerts === 0 ? 0 : (page - 1) * pageSize + 1;
  const endIdx = Math.min(page * pageSize, totalAlerts);

  return (
    <div className="space-y-6">
      {/* 1. Page Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center space-x-3">
            <h1 className="text-xl font-bold text-white tracking-tight">
              Alert Triage & Prioritization Queue
            </h1>
            <span className="px-2.5 py-0.5 rounded-full text-[10px] font-extrabold uppercase tracking-wider bg-cyan-950/80 text-cyan-300 border border-cyan-500/30 shadow-glow-cyan">
              PHASE 1 LIVE CORE
            </span>
          </div>
          <p className="text-xs text-slate-400 mt-1 leading-relaxed">
            Phase 1 Alert Triage: Deduplicate, categorize, rank by risk urgency, and trigger investigation.
          </p>
        </div>

        <div className="flex items-center space-x-3">
          <div className="px-3 py-1.5 rounded-lg bg-[#0D1526] border border-cyan-500/20 text-xs text-slate-300 flex items-center space-x-2">
            <ShieldAlert className="w-4 h-4 text-cyan-400" />
            <span className="font-mono font-bold text-cyan-300">
              {totalAlerts.toLocaleString()}
            </span>
            <span className="text-slate-400">Total Classified</span>
          </div>
        </div>
      </div>

      {/* 2. Filter Bar Row */}
      <div className="glass-card rounded-xl p-4 border border-cyan-500/15">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-12 gap-3 items-center">
          {/* Search Box */}
          <form
            onSubmit={handleSearchSubmit}
            className="lg:col-span-4 relative"
          >
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2 pointer-events-none" />
            <input
              type="text"
              placeholder="Search by Alert ID, Account ID, or reason..."
              value={searchInput}
              onChange={(e) => setSearchInput(e.target.value)}
              onBlur={() => {
                setPage(1);
                setSearchQuery(searchInput);
              }}
              className="w-full pl-9 pr-3 py-2 text-xs bg-slate-900/90 border border-slate-700/70 rounded-lg text-slate-200 placeholder-slate-500 focus:outline-none focus:border-cyan-400 focus:ring-1 focus:ring-cyan-400 transition-all"
            />
          </form>

          {/* Severity Dropdown */}
          <div className="lg:col-span-2">
            <select
              value={selectedSeverity}
              onChange={(e) => {
                setSelectedSeverity(e.target.value);
                setPage(1);
              }}
              className="w-full py-2 px-3 text-xs bg-slate-900/90 border border-slate-700/70 rounded-lg text-slate-200 focus:outline-none focus:border-cyan-400 focus:ring-1 focus:ring-cyan-400 cursor-pointer"
            >
              {SEVERITY_OPTIONS.map((opt) => (
                <option key={opt.value} value={opt.value} className="bg-slate-900 text-slate-200">
                  {opt.label}
                </option>
              ))}
            </select>
          </div>

          {/* Typology Dropdown */}
          <div className="lg:col-span-3">
            <select
              value={selectedTypology}
              onChange={(e) => {
                setSelectedTypology(e.target.value);
                setPage(1);
              }}
              className="w-full py-2 px-3 text-xs bg-slate-900/90 border border-slate-700/70 rounded-lg text-slate-200 focus:outline-none focus:border-cyan-400 focus:ring-1 focus:ring-cyan-400 cursor-pointer"
            >
              {TYPOLOGY_OPTIONS.map((opt) => (
                <option key={opt.value} value={opt.value} className="bg-slate-900 text-slate-200">
                  {opt.label}
                </option>
              ))}
            </select>
          </div>

          {/* Status Dropdown */}
          <div className="lg:col-span-2">
            <select
              value={selectedStatus}
              onChange={(e) => {
                setSelectedStatus(e.target.value);
                setPage(1);
              }}
              className="w-full py-2 px-3 text-xs bg-slate-900/90 border border-slate-700/70 rounded-lg text-slate-200 focus:outline-none focus:border-cyan-400 focus:ring-1 focus:ring-cyan-400 cursor-pointer"
            >
              {STATUS_OPTIONS.map((opt) => (
                <option key={opt.value} value={opt.value} className="bg-slate-900 text-slate-200">
                  {opt.label}
                </option>
              ))}
            </select>
          </div>

          {/* Reset Filters */}
          <div className="lg:col-span-1 flex justify-end">
            <button
              onClick={handleResetFilters}
              title="Reset all filters"
              className="p-2 rounded-lg bg-slate-900/80 border border-slate-700/60 text-slate-400 hover:text-cyan-300 hover:border-cyan-500/40 transition-colors"
            >
              <RotateCcw className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>

      {/* 3. Ranked Alert Queue Table */}
      <div className="glass-card rounded-xl p-5 border border-cyan-500/15 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse min-w-[950px]">
            <thead>
              <tr className="border-b border-white/5 text-[10px] font-bold uppercase tracking-widest text-slate-400">
                <th className="py-3 px-3 w-14">Rank</th>
                <th className="py-3 px-3">Alert ID</th>
                <th className="py-3 px-3">Entity Ref</th>
                <th className="py-3 px-3">Typology</th>
                <th className="py-3 px-3">Severity / Score</th>
                <th className="py-3 px-3 max-w-xs">Trigger Narrative</th>
                <th className="py-3 px-3 w-20">Status</th>
                <th className="py-3 px-3 text-right w-28">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/5 text-xs">
              {isLoading ? (
                <tr>
                  <td colSpan={8} className="py-16 text-center text-slate-400">
                    <div className="inline-block animate-spin rounded-full h-6 w-6 border-2 border-cyan-500 border-t-transparent mb-2" />
                    <div>Loading prioritized queue...</div>
                  </td>
                </tr>
              ) : alerts.length === 0 ? (
                <tr>
                  <td colSpan={8} className="py-16 text-center text-slate-400">
                    No alerts found matching the current search and filter criteria.
                  </td>
                </tr>
              ) : (
                alerts.map((alert, index) => {
                  const rank = (page - 1) * pageSize + index + 1;
                  const cid = alert.classified_alert_id ?? alert.alert_id ?? "";
                  const formattedAlertId = cid.startsWith("#")
                    ? cid
                    : `ALT_${cid.replace("CALERT-", "").replace("ACC", "ACC_")}`;

                  return (
                    <tr
                      key={alert.classified_alert_id}
                      onClick={() => setSelectedAlert(alert)}
                      className="hover:bg-cyan-950/20 cursor-pointer transition-colors group"
                    >
                      {/* Column 1: Rank */}
                      <td className="py-3.5 px-3 font-mono font-bold text-slate-400">
                        #{rank}
                      </td>

                      {/* Column 2: Alert ID */}
                      <td className="py-3.5 px-3 font-mono text-cyan-400 font-bold group-hover:underline">
                        {formattedAlertId}
                      </td>

                      {/* Column 3: Entity Ref (Account) */}
                      <td className="py-3.5 px-3">
                        <div className="flex flex-col">
                          <span className="text-[9px] font-bold uppercase tracking-wider text-slate-500">
                            ACCOUNT
                          </span>
                          <span className="font-mono text-slate-200 text-xs font-semibold">
                            {alert.account_id ?? alert.transaction?.account_id ?? "—"}
                          </span>
                        </div>
                      </td>

                      {/* Column 4: Typology */}
                      <td className="py-3.5 px-3">
                        <div className="flex flex-wrap items-center gap-1.5">
                          <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-slate-800/90 text-slate-200 border border-slate-700/80">
                            {alert.alert_type}
                          </span>
                          {(alert.triggered_rules?.length ?? 0) > 1 && (
                            <span className="px-1.5 py-0.5 rounded text-[9px] font-mono bg-slate-900 text-cyan-300 border border-cyan-500/20">
                              +{(alert.triggered_rules?.length ?? 1) - 1}
                            </span>
                          )}
                        </div>
                      </td>

                      {/* Column 5: Severity / Score */}
                      <td className="py-3.5 px-3">
                        <div className="flex items-center space-x-2">
                          <RiskBadge level={alert.risk_level} />
                          <span className="font-mono text-[11px] text-slate-300 font-bold">
                            ({alert.risk_score.toFixed(1)})
                          </span>
                        </div>
                      </td>

                      {/* Column 6: Trigger Narrative */}
                      <td className="py-3.5 px-3 text-slate-300 text-[11px] max-w-xs truncate" title={alert.detected_reason ?? alert.alert_type}>
                        {alert.detected_reason ?? alert.alert_type}
                      </td>

                      {/* Column 7: Status */}
                      <td className="py-3.5 px-3">
                        <span className="px-2 py-0.5 rounded text-[9px] font-bold tracking-wider uppercase bg-teal-950/70 text-teal-300 border border-teal-500/30">
                          {alert.status || "NEW"}
                        </span>
                      </td>

                      {/* Column 8: Action (Investigate) */}
                      <td className="py-3.5 px-3 text-right">
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            setSelectedAlert(alert);
                          }}
                          className="inline-flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-black text-xs font-bold transition-all shadow-glow-cyan"
                        >
                          <ExternalLink className="w-3.5 h-3.5" />
                          <span>Investigate</span>
                        </button>
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>

        {/* 4. Table Footer & Pagination Controls */}
        <div className="mt-4 pt-3 border-t border-white/5 flex flex-col sm:flex-row items-center justify-between gap-3 text-xs text-slate-400">
          <div>
            Showing <span className="font-bold text-slate-200">{startIdx}-{endIdx}</span> of{" "}
            <span className="font-bold text-slate-200">{totalAlerts.toLocaleString()}</span> ranked alerts
          </div>

          <div className="flex items-center space-x-1">
            <button
              onClick={() => setPage((p) => Math.max(1, p - 1))}
              disabled={page <= 1}
              className="px-2.5 py-1 rounded bg-slate-900/60 border border-slate-800 text-slate-400 hover:text-slate-200 hover:border-slate-700 disabled:opacity-40 disabled:hover:text-slate-400 flex items-center space-x-1"
            >
              <ChevronLeft className="w-3.5 h-3.5" />
              <span>Previous</span>
            </button>

            {/* Page buttons */}
            {page > 2 && (
              <button
                onClick={() => setPage(1)}
                className="px-2.5 py-1 rounded bg-slate-900/60 border border-slate-800 text-slate-300 hover:border-cyan-500/40"
              >
                1
              </button>
            )}

            {page > 3 && <span className="px-1 text-slate-600">...</span>}

            {page > 1 && (
              <button
                onClick={() => setPage(page - 1)}
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
                onClick={() => setPage(page + 1)}
                className="px-2.5 py-1 rounded bg-slate-900/60 border border-slate-800 text-slate-300 hover:border-cyan-500/40"
              >
                {page + 1}
              </button>
            )}

            {page < totalPages - 2 && <span className="px-1 text-slate-600">...</span>}

            {page < totalPages - 1 && (
              <button
                onClick={() => setPage(totalPages)}
                className="px-2.5 py-1 rounded bg-slate-900/60 border border-slate-800 text-slate-300 hover:border-cyan-500/40"
              >
                {totalPages}
              </button>
            )}

            <button
              onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
              disabled={page >= totalPages}
              className="px-2.5 py-1 rounded bg-slate-900/60 border border-slate-800 text-slate-400 hover:text-slate-200 hover:border-slate-700 disabled:opacity-40 disabled:hover:text-slate-400 flex items-center space-x-1"
            >
              <span>Next</span>
              <ChevronRight className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      </div>

      {/* 5. Slide-Over Investigation Drawer on Row Click */}
      <AlertSlideOver
        alert={selectedAlert}
        onClose={() => setSelectedAlert(null)}
      />
    </div>
  );
}
"use client";

import React, { useEffect, useState } from "react";
import {
  FileText,
  Download,
  ShieldCheck,
  ShieldAlert,
  Search,
  RefreshCw,
  CheckCircle2,
  AlertTriangle,
  XCircle,
  Filter,
  Eye,
  X,
  FileCheck,
  Building2,
  Activity,
  Layers,
} from "lucide-react";
import { fetchAuditLogs, getAuditPdfUrl, AuditLogItem } from "@/lib/api";

export default function AuditTrailPage() {
  const [logs, setLogs] = useState<AuditLogItem[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  
  // Search & Filters
  const [search, setSearch] = useState<string>("");
  const [decisionFilter, setDecisionFilter] = useState<string>("ALL");
  const [statusFilter, setStatusFilter] = useState<string>("ALL");
  
  // Modal Drawer for Viewing Details
  const [selectedCase, setSelectedCase] = useState<AuditLogItem | null>(null);

  const loadAuditLogs = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchAuditLogs();
      setLogs(data);
    } catch (err: any) {
      setError(err.message || "Failed to load audit logs from server.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAuditLogs();
  }, []);

  // Filtered logs calculation
  const filteredLogs = logs.filter((item) => {
    const matchesSearch =
      search === "" ||
      item.id?.toLowerCase().includes(search.toLowerCase()) ||
      item.alert_id?.toLowerCase().includes(search.toLowerCase()) ||
      item.entity_id?.toLowerCase().includes(search.toLowerCase()) ||
      item.typology?.toLowerCase().includes(search.toLowerCase());

    const matchesDecision =
      decisionFilter === "ALL" ||
      item.decision?.toUpperCase() === decisionFilter.toUpperCase();

    const matchesStatus =
      statusFilter === "ALL" ||
      item.status?.toUpperCase() === statusFilter.toUpperCase();

    return matchesSearch && matchesDecision && matchesStatus;
  });

  // KPI Calculations
  const totalCount = logs.length;
  const closedCount = logs.filter((l) => l.status === "CLOSED").length;
  const blockCount = logs.filter((l) => l.decision === "BLOCK").length;
  const reviewCount = logs.filter((l) => l.decision === "REVIEW").length;
  const allowCount = logs.filter((l) => l.decision === "ALLOW").length;

  const getDecisionBadge = (decision?: string) => {
    switch (decision?.toUpperCase()) {
      case "BLOCK":
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-red-500/10 text-red-400 border border-red-500/20">
            <XCircle className="w-3.5 h-3.5" />
            BLOCK
          </span>
        );
      case "ALLOW":
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
            <CheckCircle2 className="w-3.5 h-3.5" />
            ALLOW
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-amber-500/10 text-amber-400 border border-amber-500/20">
            <AlertTriangle className="w-3.5 h-3.5" />
            REVIEW
          </span>
        );
    }
  };

  const getScoreBadgeColor = (score?: number) => {
    const s = score || 0;
    if (s >= 75) return "text-red-400 bg-red-500/10 border-red-500/20";
    if (s >= 40) return "text-amber-400 bg-amber-500/10 border-amber-500/20";
    return "text-emerald-400 bg-emerald-500/10 border-emerald-500/20";
  };

  return (
    <div className="min-h-screen bg-[#090d16] text-slate-100 p-6 space-y-6 font-sans">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800/80 pb-5">
        <div>
          <div className="flex items-center gap-2.5">
            <div className="p-2 rounded-lg bg-sky-500/10 border border-sky-500/20 text-sky-400">
              <ShieldCheck className="w-6 h-6" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-white tracking-tight">
                Compliance Audit Trail & Dossiers
              </h1>
              <p className="text-sm text-slate-400">
                Immutable decision logging, multi-agent execution evidence & regulatory PDF export
              </p>
            </div>
          </div>
        </div>

        <button
          onClick={loadAuditLogs}
          disabled={loading}
          className="inline-flex items-center gap-2 px-4 py-2 text-xs font-semibold rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700/60 transition-all disabled:opacity-50"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? "animate-spin" : ""}`} />
          Refresh Trail
        </button>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-4">
        <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-4 space-y-1 backdrop-blur-md">
          <div className="flex items-center justify-between text-slate-400 text-xs font-medium">
            <span>Total Logged Cases</span>
            <Layers className="w-4 h-4 text-sky-400" />
          </div>
          <p className="text-2xl font-bold text-white">{totalCount}</p>
          <span className="text-[11px] text-slate-500">Database recorded</span>
        </div>

        <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-4 space-y-1 backdrop-blur-md">
          <div className="flex items-center justify-between text-slate-400 text-xs font-medium">
            <span>Completed Audits</span>
            <FileCheck className="w-4 h-4 text-indigo-400" />
          </div>
          <p className="text-2xl font-bold text-indigo-300">{closedCount}</p>
          <span className="text-[11px] text-slate-500">CLOSED status</span>
        </div>

        <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-4 space-y-1 backdrop-blur-md">
          <div className="flex items-center justify-between text-slate-400 text-xs font-medium">
            <span>Block Directives</span>
            <ShieldAlert className="w-4 h-4 text-red-400" />
          </div>
          <p className="text-2xl font-bold text-red-400">{blockCount}</p>
          <span className="text-[11px] text-slate-500">Critical risk action</span>
        </div>

        <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-4 space-y-1 backdrop-blur-md">
          <div className="flex items-center justify-between text-slate-400 text-xs font-medium">
            <span>Analyst Review</span>
            <AlertTriangle className="w-4 h-4 text-amber-400" />
          </div>
          <p className="text-2xl font-bold text-amber-300">{reviewCount}</p>
          <span className="text-[11px] text-slate-500">Manual review flag</span>
        </div>

        <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-4 space-y-1 backdrop-blur-md">
          <div className="flex items-center justify-between text-slate-400 text-xs font-medium">
            <span>Cleared (Allow)</span>
            <CheckCircle2 className="w-4 h-4 text-emerald-400" />
          </div>
          <p className="text-2xl font-bold text-emerald-300">{allowCount}</p>
          <span className="text-[11px] text-slate-500">Low risk passed</span>
        </div>
      </div>

      {/* Search & Filter Bar */}
      <div className="bg-slate-900/80 border border-slate-800/80 rounded-xl p-4 flex flex-col md:flex-row gap-4 items-stretch md:items-center justify-between shadow-lg">
        {/* Search */}
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
          <input
            type="text"
            placeholder="Search Case ID, Alert ID, Entity ID, or Typology..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-9 pr-4 py-2 bg-slate-950/70 border border-slate-800 rounded-lg text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-sky-500/50 transition-colors"
          />
        </div>

        {/* Filter Controls */}
        <div className="flex flex-wrap items-center gap-3 text-xs">
          <div className="flex items-center gap-1.5 text-slate-400 font-medium">
            <Filter className="w-3.5 h-3.5 text-sky-400" />
            <span>Decision:</span>
          </div>
          {["ALL", "BLOCK", "REVIEW", "ALLOW"].map((dec) => (
            <button
              key={dec}
              onClick={() => setDecisionFilter(dec)}
              className={`px-3 py-1.5 rounded-lg font-medium transition-all ${
                decisionFilter === dec
                  ? "bg-sky-500/20 text-sky-300 border border-sky-500/30"
                  : "bg-slate-950/50 text-slate-400 hover:bg-slate-800/60 border border-slate-800"
              }`}
            >
              {dec}
            </button>
          ))}

          <div className="h-4 w-px bg-slate-800 mx-1 hidden sm:block" />

          <div className="flex items-center gap-1.5 text-slate-400 font-medium">
            <span>Status:</span>
          </div>
          {["ALL", "CLOSED", "OPEN"].map((st) => (
            <button
              key={st}
              onClick={() => setStatusFilter(st)}
              className={`px-3 py-1.5 rounded-lg font-medium transition-all ${
                statusFilter === st
                  ? "bg-sky-500/20 text-sky-300 border border-sky-500/30"
                  : "bg-slate-950/50 text-slate-400 hover:bg-slate-800/60 border border-slate-800"
              }`}
            >
              {st}
            </button>
          ))}
        </div>
      </div>

      {/* Main Audit Trail Data Table */}
      <div className="bg-slate-900/60 border border-slate-800 rounded-xl overflow-hidden shadow-xl backdrop-blur-md">
        {loading ? (
          <div className="p-12 text-center text-slate-400 space-y-3">
            <RefreshCw className="w-8 h-8 animate-spin mx-auto text-sky-400" />
            <p className="text-sm font-medium">Loading compliance audit records from database...</p>
          </div>
        ) : error ? (
          <div className="p-8 text-center text-red-400 bg-red-500/5 space-y-2">
            <ShieldAlert className="w-8 h-8 mx-auto text-red-400" />
            <p className="text-sm font-semibold">{error}</p>
            <button
              onClick={loadAuditLogs}
              className="mt-2 px-3 py-1.5 text-xs bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-lg border border-slate-700"
            >
              Retry
            </button>
          </div>
        ) : filteredLogs.length === 0 ? (
          <div className="p-12 text-center text-slate-400 space-y-2">
            <FileText className="w-8 h-8 mx-auto text-slate-600" />
            <p className="text-sm font-medium">No audit records found matching your filters.</p>
            <p className="text-xs text-slate-500">Try adjusting your search query or decision filter.</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs text-slate-300">
              <thead className="bg-slate-950/80 text-slate-400 uppercase font-semibold text-[11px] border-b border-slate-800">
                <tr>
                  <th className="px-4 py-3.5">Case & Alert ID</th>
                  <th className="px-4 py-3.5">Entity / Customer</th>
                  <th className="px-4 py-3.5">Typology</th>
                  <th className="px-4 py-3.5">Risk Score</th>
                  <th className="px-4 py-3.5">Decision</th>
                  <th className="px-4 py-3.5">Status</th>
                  <th className="px-4 py-3.5">Timestamp</th>
                  <th className="px-4 py-3.5 text-right">Actions & Dossier</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {filteredLogs.map((log) => {
                  const pdfUrl = getAuditPdfUrl(log.id);
                  return (
                    <tr
                      key={log.id}
                      className="hover:bg-slate-800/40 transition-colors group"
                    >
                      <td className="px-4 py-4 font-medium">
                        <div className="text-sky-300 font-mono font-semibold">{log.id}</div>
                        <div className="text-[11px] text-slate-500 font-mono">Alert: {log.alert_id || "N/A"}</div>
                      </td>

                      <td className="px-4 py-4">
                        <div className="flex items-center gap-1.5 text-slate-200">
                          <Building2 className="w-3.5 h-3.5 text-slate-400" />
                          <span>{log.entity_id || "N/A"}</span>
                        </div>
                      </td>

                      <td className="px-4 py-4">
                        <span className="inline-block max-w-[160px] truncate text-slate-300 bg-slate-800/60 px-2 py-0.5 rounded text-[11px] border border-slate-700/50">
                          {log.typology || "Suspicious Activity"}
                        </span>
                      </td>

                      <td className="px-4 py-4">
                        <div className="flex items-center gap-2">
                          <span
                            className={`px-2 py-0.5 rounded font-mono font-bold text-xs border ${getScoreBadgeColor(
                              log.final_risk_score
                            )}`}
                          >
                            {(log.final_risk_score || 0).toFixed(1)}
                          </span>
                          <span className="text-[10px] text-slate-500 uppercase">{log.priority_band || "MED"}</span>
                        </div>
                      </td>

                      <td className="px-4 py-4">{getDecisionBadge(log.decision)}</td>

                      <td className="px-4 py-4">
                        <span
                          className={`inline-flex items-center gap-1 px-2 py-0.5 rounded text-[11px] font-medium ${
                            log.status === "CLOSED"
                              ? "bg-indigo-500/10 text-indigo-400 border border-indigo-500/20"
                              : "bg-amber-500/10 text-amber-400 border border-amber-500/20"
                          }`}
                        >
                          <Activity className="w-3 h-3" />
                          {log.status}
                        </span>
                      </td>

                      <td className="px-4 py-4 text-slate-400 font-mono text-[11px]">
                        {log.updated_at || log.created_at || "—"}
                      </td>

                      <td className="px-4 py-4 text-right">
                        <div className="flex items-center justify-end gap-2">
                          <button
                            onClick={() => setSelectedCase(log)}
                            className="inline-flex items-center gap-1 px-2.5 py-1.5 text-[11px] font-medium rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 transition-colors"
                            title="View Summary"
                          >
                            <Eye className="w-3.5 h-3.5 text-sky-400" />
                            View
                          </button>

                          <a
                            href={pdfUrl}
                            download
                            target="_blank"
                            rel="noopener noreferrer"
                            className="inline-flex items-center gap-1.5 px-3 py-1.5 text-[11px] font-semibold rounded-lg bg-sky-500/20 hover:bg-sky-500/30 text-sky-300 border border-sky-500/30 transition-all shadow-sm"
                            title="Download Official Audit PDF"
                          >
                            <Download className="w-3.5 h-3.5" />
                            PDF
                          </a>
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Detail Slide-over Modal */}
      {selectedCase && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex justify-end transition-opacity">
          <div className="w-full max-w-xl bg-[#0f172a] border-l border-slate-800 h-full p-6 space-y-6 overflow-y-auto shadow-2xl">
            {/* Modal Header */}
            <div className="flex items-center justify-between border-b border-slate-800 pb-4">
              <div className="space-y-1">
                <div className="flex items-center gap-2">
                  <span className="text-xs font-mono text-sky-400 bg-sky-500/10 px-2 py-0.5 rounded border border-sky-500/20">
                    {selectedCase.id}
                  </span>
                  {getDecisionBadge(selectedCase.decision)}
                </div>
                <h2 className="text-lg font-bold text-white">Audit Case Details</h2>
              </div>
              <button
                onClick={() => setSelectedCase(null)}
                className="p-1.5 text-slate-400 hover:text-white rounded-lg bg-slate-800/60 hover:bg-slate-800"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Overview Attributes */}
            <div className="grid grid-cols-2 gap-3 text-xs bg-slate-900/80 p-4 rounded-xl border border-slate-800">
              <div>
                <span className="text-slate-500 block">Alert ID</span>
                <span className="font-mono text-slate-200 font-medium">{selectedCase.alert_id || "N/A"}</span>
              </div>
              <div>
                <span className="text-slate-500 block">Entity ID</span>
                <span className="font-mono text-slate-200 font-medium">{selectedCase.entity_id || "N/A"}</span>
              </div>
              <div>
                <span className="text-slate-500 block">Risk Score</span>
                <span className="font-mono font-bold text-sky-400">
                  {(selectedCase.final_risk_score || 0).toFixed(1)} / 100
                </span>
              </div>
              <div>
                <span className="text-slate-500 block">Priority Band</span>
                <span className="font-semibold text-amber-300">{selectedCase.priority_band || "MEDIUM"}</span>
              </div>
              <div>
                <span className="text-slate-500 block">Typology</span>
                <span className="text-slate-200">{selectedCase.typology || "Suspicious Activity"}</span>
              </div>
              <div>
                <span className="text-slate-500 block">Recorded Date</span>
                <span className="font-mono text-slate-400">{selectedCase.updated_at || selectedCase.created_at || "—"}</span>
              </div>
            </div>

            {/* Case Objective */}
            <div className="space-y-2">
              <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Investigation Scope</h3>
              <p className="text-xs text-slate-300 bg-slate-900/60 p-3 rounded-lg border border-slate-800">
                {selectedCase.objective || `Detailed compliance analysis for entity ${selectedCase.entity_id}`}
              </p>
            </div>

            {/* Summary Notes */}
            <div className="space-y-2">
              <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Executive Summary & Audit Notes</h3>
              <div className="text-xs text-slate-300 bg-slate-900/60 p-3.5 rounded-lg border border-slate-800 leading-relaxed whitespace-pre-wrap">
                {selectedCase.summary_notes || "Multi-agent graph executed. Full state decision snapshot stored."}
              </div>
            </div>

            {/* Download Action Footer */}
            <div className="pt-4 border-t border-slate-800 flex items-center justify-between">
              <span className="text-[11px] text-slate-500">Official Regulatory Export</span>
              <a
                href={getAuditPdfUrl(selectedCase.id)}
                download
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-2 px-4 py-2 bg-sky-500 hover:bg-sky-400 text-slate-950 text-xs font-bold rounded-lg transition-all shadow-lg shadow-sky-500/20"
              >
                <Download className="w-4 h-4" />
                Download Compliance PDF
              </a>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

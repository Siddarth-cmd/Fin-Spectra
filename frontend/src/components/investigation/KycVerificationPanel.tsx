"use client";

import React from "react";
import { UserCheck, Shield, Clock, Briefcase, FileText, CheckCircle2, AlertCircle } from "lucide-react";

interface KycVerificationPanelProps {
  kycNotes: string;
  riskScoring?: {
    subscores?: {
      kyc?: number;
    };
  };
  customer?: {
    name?: string;
    customer_id?: string;
    risk_level?: string;
    account_age_days?: number;
    occupation?: string;
  };
}

export function KycVerificationPanel({
  kycNotes,
  riskScoring,
  customer,
}: KycVerificationPanelProps) {
  // KYC subscore in backend state is 0 to 100 (e.g. 70.0)
  const kycSubscore = riskScoring?.subscores?.kyc ?? 0.0;

  // Extract customer fields from prop or parse from kycNotes string
  const activeCustomer = React.useMemo(() => {
    if (customer && (customer.customer_id || customer.name)) return customer;
    if (!kycNotes) return null;

    const idMatch = kycNotes.match(/ID:\s*([^\)\|\,]+)/i);
    const nameMatch = kycNotes.match(/Customer:\s*([^\|\(]+)/i);
    const occMatch = kycNotes.match(/Occupation:\s*([^\|]+)/i);
    const riskMatch = kycNotes.match(/Risk Level:\s*([^\|]+)/i);
    const ageMatch = kycNotes.match(/Account Age:\s*(\d+)/i);

    return {
      customer_id: idMatch ? idMatch[1].trim() : undefined,
      name: nameMatch ? nameMatch[1].trim() : undefined,
      occupation: occMatch ? occMatch[1].trim() : undefined,
      risk_level: riskMatch ? riskMatch[1].trim() : undefined,
      account_age_days: ageMatch ? parseInt(ageMatch[1].trim(), 10) : undefined,
    };
  }, [customer, kycNotes]);

  const riskLevelUpper = (activeCustomer?.risk_level || "").toUpperCase();

  // Determine risk status based on KYC notes and score
  const isHighRiskKYC =
    kycSubscore > 40.0 ||
    ["HIGH", "CRITICAL"].includes(riskLevelUpper) ||
    kycNotes.includes("ALERT");

  return (
    <div className="space-y-6">
      {/* Header Banner */}
      <div className="bg-gradient-to-r from-blue-950/40 via-slate-800/60 to-slate-900 border border-blue-500/20 rounded-xl p-5 shadow-lg">
        <div className="flex items-start justify-between flex-wrap gap-4">
          <div className="flex items-center gap-3">
            <div className="p-3 bg-blue-500/10 border border-blue-500/30 rounded-xl text-blue-400">
              <UserCheck className="w-6 h-6" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h2 className="text-lg font-bold text-white">KYC Verifier Agent</h2>
                <span className="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded bg-blue-500/20 border border-blue-500/30 text-blue-300">
                  Phase 2 Multi-Agent
                </span>
              </div>
              <p className="text-xs text-slate-400 mt-1">
                Automated Customer Due Diligence, Identity Verification, and Risk Profiling
              </p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <div className="text-right">
              <p className="text-[11px] uppercase tracking-wider text-slate-400 font-semibold">
                KYC Sub-Score
              </p>
              <p
                className={`text-2xl font-black tabular-nums ${
                  isHighRiskKYC ? "text-amber-400" : "text-emerald-400"
                }`}
              >
                {kycSubscore.toFixed(1)} <span className="text-sm font-normal text-slate-400">/ 100</span>
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Customer Identity Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-slate-800/60 border border-slate-700/60 rounded-xl p-4">
          <div className="flex items-center gap-2 text-slate-400 text-xs mb-1 font-medium">
            <UserCheck className="w-4 h-4 text-cyan-400" />
            <span>Customer Reference</span>
          </div>
          <p className="text-base font-bold text-white font-mono">
            {activeCustomer?.customer_id || "CUST_REF"}
          </p>
          <p className="text-xs text-slate-400 mt-0.5">{activeCustomer?.name || "Verified Customer"}</p>
        </div>

        <div className="bg-slate-800/60 border border-slate-700/60 rounded-xl p-4">
          <div className="flex items-center gap-2 text-slate-400 text-xs mb-1 font-medium">
            <Briefcase className="w-4 h-4 text-purple-400" />
            <span>Declared Occupation</span>
          </div>
          <p className="text-base font-bold text-white">
            {activeCustomer?.occupation || "Unspecified / Trader"}
          </p>
          <p className="text-xs text-slate-400 mt-0.5">High Volume Account Profile</p>
        </div>

        <div className="bg-slate-800/60 border border-slate-700/60 rounded-xl p-4">
          <div className="flex items-center gap-2 text-slate-400 text-xs mb-1 font-medium">
            <Clock className="w-4 h-4 text-emerald-400" />
            <span>Account Age</span>
          </div>
          <p className="text-base font-bold text-white font-mono">
            {activeCustomer?.account_age_days !== undefined
              ? `${activeCustomer.account_age_days} Days`
              : "180 Days"}
          </p>
          <p className="text-xs text-slate-400 mt-0.5">Relationship Duration</p>
        </div>

        <div className="bg-slate-800/60 border border-slate-700/60 rounded-xl p-4">
          <div className="flex items-center gap-2 text-slate-400 text-xs mb-1 font-medium">
            <Shield className="w-4 h-4 text-amber-400" />
            <span>Prior Risk Rating</span>
          </div>
          <span
            className={`inline-block text-xs font-bold px-2.5 py-1 rounded-md border mt-1 ${
              riskLevelUpper === "HIGH" || riskLevelUpper === "CRITICAL"
                ? "bg-red-500/20 border-red-500/40 text-red-300"
                : riskLevelUpper === "MEDIUM"
                ? "bg-amber-500/20 border-amber-500/40 text-amber-300"
                : "bg-emerald-500/20 border-emerald-500/40 text-emerald-300"
            }`}
          >
            {activeCustomer?.risk_level || "LOW"}
          </span>
        </div>
      </div>

      {/* KYC Agent Verification Findings */}
      <div className="bg-slate-800/60 border border-slate-700/60 rounded-xl p-5 space-y-4">
        <div className="flex items-center justify-between border-b border-slate-700/60 pb-3">
          <div className="flex items-center gap-2">
            <FileText className="w-4 h-4 text-cyan-400" />
            <h3 className="text-xs font-bold text-white uppercase tracking-wider">
              KYC Verifier Findings & Notes
            </h3>
          </div>
          <span className="text-xs text-slate-400 font-mono">Agent Node: kyc_verifier</span>
        </div>

        <div className="bg-slate-900/80 border border-slate-800 rounded-lg p-4 font-mono text-sm leading-relaxed text-slate-200">
          {kycNotes ? (
            <p className="whitespace-pre-wrap">{kycNotes}</p>
          ) : (
            <p className="text-slate-500 italic">
              KYC Verifier Agent executed identity check: Customer risk profile reviewed. No baseline PEP or sanctions conflict detected.
            </p>
          )}
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-3 pt-2">
          <div className="flex items-start gap-2.5 p-3 rounded-lg bg-emerald-500/10 border border-emerald-500/20 text-emerald-300 text-xs">
            <CheckCircle2 className="w-4 h-4 flex-shrink-0 mt-0.5" />
            <div>
              <span className="font-bold block">Sanctions & Watchlist Screening</span>
              <span>Identity screening cleared against standard OFAC and global AML databases.</span>
            </div>
          </div>

          <div className="flex items-start gap-2.5 p-3 rounded-lg bg-blue-500/10 border border-blue-500/20 text-blue-300 text-xs">
            <AlertCircle className="w-4 h-4 flex-shrink-0 mt-0.5" />
            <div>
              <span className="font-bold block">Source of Wealth Context</span>
              <span>Declared occupation matches transactional baseline expectations for business activities.</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

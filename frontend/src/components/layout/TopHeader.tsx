"use client";

import React, { useState } from "react";
import { RefreshCw, User, ShieldAlert } from "lucide-react";

interface TopHeaderProps {
  lastRun?: string;
  isRefreshing?: boolean;
  onRefresh?: () => void;
  title?: string;
  subtitle?: string;
}

export const TopHeader: React.FC<TopHeaderProps> = ({
  lastRun = "42s ago",
  isRefreshing = false,
  onRefresh,
  title = "FinSpectra AML",
  subtitle = "Intelligent Surveillance Core",
}) => {
  const [spin, setSpin] = useState(false);

  const handleRefresh = () => {
    setSpin(true);
    if (onRefresh) onRefresh();
    setTimeout(() => setSpin(false), 800);
  };

  return (
    <header className="sticky top-0 z-20 h-16 bg-[#080B12]/90 backdrop-blur-xl border-b border-cyan-500/10 px-6 flex items-center justify-between">
      {/* Title & Brand */}
      <div className="flex items-center space-x-3">
        <div className="w-6 h-6 rounded bg-cyan-500/10 border border-cyan-400/30 flex items-center justify-center">
          <ShieldAlert className="w-3.5 h-3.5 text-cyan-400" />
        </div>
        <div className="flex items-baseline space-x-2">
          <h1 className="text-sm font-bold text-white tracking-wide">
            {title}
          </h1>
          <span className="text-xs text-slate-400 font-normal">
            {subtitle}
          </span>
        </div>
      </div>

      {/* Status & Actions */}
      <div className="flex items-center space-x-4">
        {/* Pipeline Status Pill */}
        <div className="flex items-center space-x-2 px-3 py-1 rounded-full bg-[#0D1526] border border-cyan-500/25 shadow-glow-cyan">
          <span className="w-2 h-2 rounded-full bg-cyan-400 pulse-live" />
          <span className="text-[10px] font-bold tracking-widest uppercase text-cyan-300">
            PIPELINE: HEALTHY
          </span>
        </div>

        {/* Last Run */}
        <div className="text-xs text-slate-400 font-medium">
          Last run: <span className="text-slate-300">{lastRun}</span>
        </div>

        {/* Refresh Button */}
        <button
          onClick={handleRefresh}
          className="p-1.5 rounded-lg bg-slate-900/60 border border-slate-700/60 text-slate-400 hover:text-cyan-300 hover:border-cyan-500/40 transition-colors"
          title="Refresh telemetry & pipeline status"
        >
          <RefreshCw
            className={`w-4 h-4 ${isRefreshing || spin ? "animate-spin text-cyan-400" : ""}`}
          />
        </button>

        {/* Analyst Avatar Icon */}
        <div className="w-8 h-8 rounded-full bg-teal-950/60 border border-teal-500/30 flex items-center justify-center text-teal-300 shadow-glow-teal">
          <User className="w-4 h-4" />
        </div>
      </div>
    </header>
  );
};

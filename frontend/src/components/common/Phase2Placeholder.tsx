import React from "react";
import Link from "next/link";
import { ArrowRight } from "lucide-react";

interface FeatureCard {
  icon: string;
  title: string;
  description: string;
}

interface Phase2PlaceholderProps {
  badge: string;
  icon: React.ComponentType<{ className?: string }>;
  title: string;
  description: string;
  features: FeatureCard[];
  primaryButtonText?: string;
  primaryButtonHref?: string;
  secondaryButtonText?: string;
  secondaryButtonHref?: string;
  footerNote: string;
}

export const Phase2Placeholder: React.FC<Phase2PlaceholderProps> = ({
  badge,
  icon: Icon,
  title,
  description,
  features,
  primaryButtonText = "View Phase 1 Dashboard",
  primaryButtonHref = "/",
  secondaryButtonText = "Return to Core",
  secondaryButtonHref = "/",
  footerNote,
}) => {
  return (
    <div className="flex-1 flex flex-col items-center justify-center p-6 md:p-12 min-h-[calc(100vh-5rem)]">
      <div className="w-full max-w-3xl glass-card rounded-2xl p-8 sm:p-10 border border-cyan-500/20 text-center relative overflow-hidden shadow-glow">
        {/* Glow ambient background circles */}
        <div className="absolute -top-24 left-1/2 -translate-x-1/2 w-96 h-96 bg-cyan-500/10 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute -bottom-24 left-1/2 -translate-x-1/2 w-96 h-96 bg-blue-600/10 rounded-full blur-3xl pointer-events-none" />

        {/* Top Scope Pill */}
        <div className="inline-flex items-center space-x-2 px-3.5 py-1 rounded-full bg-cyan-950/70 border border-cyan-500/30 text-cyan-300 text-[10px] font-extrabold tracking-widest uppercase mb-6 shadow-glow-cyan">
          <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 pulse-live" />
          <span>{badge}</span>
        </div>

        {/* Center Glowing Icon */}
        <div className="mx-auto w-16 h-16 rounded-2xl bg-[#0F172A]/90 border border-cyan-400/40 flex items-center justify-center text-cyan-400 mb-5 shadow-glow-cyan ring-4 ring-cyan-500/10">
          <Icon className="w-8 h-8" />
        </div>

        {/* Title & Subtitle */}
        <h2 className="text-2xl sm:text-3xl font-black text-white tracking-tight">
          {title}
        </h2>
        <p className="text-xs sm:text-sm text-slate-300 max-w-xl mx-auto mt-3 leading-relaxed">
          {description}
        </p>

        {/* 3 Feature Highlight Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3.5 my-8 text-left">
          {features.map((feat, idx) => (
            <div
              key={idx}
              className="p-4 rounded-xl bg-slate-900/70 border border-white/5 hover:border-cyan-500/30 transition-all duration-200"
            >
              <div className="text-lg mb-2">{feat.icon}</div>
              <div className="text-xs font-bold text-slate-100">{feat.title}</div>
              <div className="text-[11px] text-slate-400 mt-1 leading-snug">
                {feat.description}
              </div>
            </div>
          ))}
        </div>

        {/* Action Buttons */}
        <div className="flex flex-wrap items-center justify-center gap-3">
          <Link
            href={primaryButtonHref}
            className="flex items-center space-x-2 px-5 py-2.5 rounded-lg bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-black text-xs font-bold transition-all shadow-glow-cyan"
          >
            <span>{primaryButtonText}</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </Link>
          <Link
            href={secondaryButtonHref}
            className="px-5 py-2.5 rounded-lg bg-slate-900/80 hover:bg-slate-800 border border-slate-700/60 text-slate-300 text-xs font-semibold transition-colors"
          >
            {secondaryButtonText}
          </Link>
        </div>

        {/* Footer Note */}
        <div className="mt-8 pt-4 border-t border-white/5 text-[11px] text-slate-500 font-mono tracking-tight">
          {footerNote}
        </div>
      </div>
    </div>
  );
};

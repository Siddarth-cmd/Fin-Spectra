"use client";

import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  AlertTriangle,
  GitFork,
  ShieldCheck,
  Gauge,
  MoreVertical,
  ShieldAlert,
} from "lucide-react";

interface NavItem {
  name: string;
  href: string;
  icon: React.ComponentType<{ className?: string }>;
}

const navItems: NavItem[] = [
  { name: "Dashboard", href: "/", icon: LayoutDashboard },
  { name: "Alert Queue", href: "/alert-queue", icon: AlertTriangle },
  { name: "Investigation", href: "/investigations", icon: GitFork },
  { name: "Audit Trail", href: "/audit-trail", icon: ShieldCheck },
  { name: "Evaluation", href: "/evaluation", icon: Gauge },
];

export const Sidebar: React.FC = () => {
  const pathname = usePathname();

  return (
    <aside className="fixed left-0 top-0 bottom-0 w-64 bg-[#090D16]/95 backdrop-blur-xl border-r border-cyan-500/10 flex flex-col justify-between z-30 select-none">
      <div>
        {/* Brand Logo Header */}
        <div className="p-5 border-b border-white/5 flex items-center space-x-3">
          <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-cyan-500/20 via-blue-600/20 to-transparent border border-cyan-400/40 flex items-center justify-center shadow-glow-cyan">
            <ShieldAlert className="w-5 h-5 text-cyan-400" />
          </div>
          <div>
            <div className="flex items-center space-x-1.5">
              <span className="text-xs font-black tracking-widest text-cyan-400">FIN</span>
              <span className="text-xs font-black tracking-widest text-slate-200">SPECTRA</span>
            </div>
            <div className="text-[9px] tracking-widest uppercase font-semibold text-slate-400">
              AML PLATFORM
            </div>
          </div>
        </div>

        {/* Navigation Section */}
        <div className="px-3 py-4">
          <div className="px-3 pb-2 text-[10px] font-bold tracking-widest uppercase text-slate-500">
            OPERATIONS
          </div>
          <nav className="space-y-1">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive =
                item.href === "/"
                  ? pathname === "/"
                  : pathname.startsWith(item.href);

              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={`group relative flex items-center space-x-3 px-3.5 py-2.5 rounded-lg text-xs font-medium transition-all duration-200 ${
                    isActive
                      ? "bg-cyan-950/40 border border-cyan-500/30 text-cyan-300 shadow-glow-cyan"
                      : "text-slate-400 hover:text-slate-200 hover:bg-slate-800/40 border border-transparent"
                  }`}
                >
                  <Icon
                    className={`w-4 h-4 transition-colors ${
                      isActive ? "text-cyan-400" : "text-slate-400 group-hover:text-slate-300"
                    }`}
                  />
                  <span>{item.name}</span>
                  {isActive && (
                    <span className="absolute right-2 w-1.5 h-1.5 rounded-full bg-cyan-400 shadow-glow-cyan" />
                  )}
                </Link>
              );
            })}
          </nav>
        </div>
      </div>

      {/* Bottom Analyst Profile Chip */}
      <div className="p-3 border-t border-white/5 bg-[#070A11]/60">
        <div className="flex items-center justify-between p-2.5 rounded-lg bg-[#0E1524] border border-cyan-500/15 hover:border-cyan-500/30 transition-all cursor-pointer">
          <div className="flex items-center space-x-2.5">
            <div className="w-8 h-8 rounded-full bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center text-xs font-bold text-black ring-2 ring-cyan-400/20">
              AR
            </div>
            <div className="truncate">
              <div className="text-xs font-semibold text-slate-200 truncate">
                Alex Rivera
              </div>
              <div className="text-[10px] text-slate-400 truncate">
                Sr AML Analyst - Tier 1
              </div>
            </div>
          </div>
          <MoreVertical className="w-3.5 h-3.5 text-slate-400 flex-shrink-0" />
        </div>
      </div>
    </aside>
  );
};

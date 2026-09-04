import React from "react";
import { RiskLevel } from "@/lib/types";

interface RiskBadgeProps {
  level: RiskLevel | string;
  showDot?: boolean;
  size?: "sm" | "md" | "lg";
}

export const RiskBadge: React.FC<RiskBadgeProps> = ({
  level,
  showDot = true,
  size = "sm",
}) => {
  const normLevel = (level || "MEDIUM").toUpperCase();

  const getStyle = () => {
    switch (normLevel) {
      case "CRITICAL":
        return {
          container: "bg-rose-950/50 border-rose-500/40 text-rose-300 shadow-glow-rose",
          dot: "bg-rose-400",
        };
      case "HIGH":
        return {
          container: "bg-amber-950/50 border-amber-500/40 text-amber-300 shadow-glow-amber",
          dot: "bg-amber-400",
        };
      case "MEDIUM":
        return {
          container: "bg-yellow-950/40 border-yellow-500/30 text-yellow-300 shadow-glow-yellow",
          dot: "bg-yellow-400",
        };
      case "LOW":
      default:
        return {
          container: "bg-teal-950/40 border-teal-500/30 text-teal-300 shadow-glow-teal",
          dot: "bg-teal-400",
        };
    }
  };

  const { container, dot } = getStyle();

  const sizeClasses = {
    sm: "px-2 py-0.5 text-[10px]",
    md: "px-2.5 py-1 text-xs",
    lg: "px-3 py-1.5 text-sm",
  }[size];

  return (
    <span
      className={`inline-flex items-center space-x-1.5 rounded-full font-bold tracking-wider uppercase border ${sizeClasses} ${container}`}
    >
      {showDot && <span className={`w-1.5 h-1.5 rounded-full ${dot}`} />}
      <span>{normLevel}</span>
    </span>
  );
};

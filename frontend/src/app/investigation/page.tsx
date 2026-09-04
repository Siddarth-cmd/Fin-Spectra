import React from "react";
import { GitFork } from "lucide-react";
import { Phase2Placeholder } from "@/components/common/Phase2Placeholder";

export default function InvestigationPage() {
  return (
    <Phase2Placeholder
      badge="MULTI-AGENT REASONING • PHASE 2 SCOPE"
      icon={GitFork}
      title="Investigation Details — Coming in Phase 2"
      description="Deep entity graph exploration, forensic transaction timelines, counterparty analysis, and LLM-assisted investigative summaries will be powered by Phase 2 agent swarms."
      features={[
        {
          icon: "🕸️",
          title: "Graph Engine",
          description: "Multi-hop money flow graph topology visualization.",
        },
        {
          icon: "⏱️",
          title: "Forensic Timeline",
          description: "Chronological transaction sequence and cycle reconstruction.",
        },
        {
          icon: "📑",
          title: "SAR Generator",
          description: "Automated Suspicious Activity Report drafting and evidence collation.",
        },
      ]}
      primaryButtonText="Explore Alert Traceability"
      primaryButtonHref="/"
      secondaryButtonText="View Architecture Specs"
      secondaryButtonHref="/"
      footerNote="Target Release: Phase 2 • Graph Neural Network + LLM Multi-Agent Framework"
    />
  );
}

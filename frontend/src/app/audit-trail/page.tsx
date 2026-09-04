import React from "react";
import { ShieldCheck } from "lucide-react";
import { Phase2Placeholder } from "@/components/common/Phase2Placeholder";

export default function AuditTrailPage() {
  return (
    <Phase2Placeholder
      badge="COMPLIANCE LOGGING • PHASE 2 SCOPE"
      icon={ShieldCheck}
      title="Audit Trail — Coming in Phase 2"
      description="Immutable compliance logging, revision histories, automated regulatory reporting, and full traceability verification are scheduled for delivery in Phase 2."
      features={[
        {
          icon: "🔒",
          title: "WORM Storage Engine",
          description: "Write-Once-Read-Many cryptographic audit log persistence.",
        },
        {
          icon: "📋",
          title: "FinCEN Standard Export",
          description: "One-click regulatory filing formats and compliance extracts.",
        },
        {
          icon: "🔍",
          title: "Verifiable Lineage",
          description: "Cryptographic proof of alert scoring and analyst decision lineage.",
        },
      ]}
      primaryButtonText="View Governance Policies"
      primaryButtonHref="/"
      secondaryButtonText="Return to Core"
      secondaryButtonHref="/"
      footerNote="Immutable event streams • Zero-trust verification architecture • Target Release: Q3"
    />
  );
}

import React from "react";
import { Gauge } from "lucide-react";
import { Phase2Placeholder } from "@/components/common/Phase2Placeholder";

export default function EvaluationPage() {
  return (
    <Phase2Placeholder
      badge="ML METRICS & TUNING • PHASE 2 SCOPE"
      icon={Gauge}
      title="Model Evaluation — Coming in Phase 2"
      description="Precision/Recall benchmarking against AMLSim-R ground truth, rule weight auto-tuning, false positive drift analysis, and model governance dashboards are in Phase 2 development."
      features={[
        {
          icon: "🎯",
          title: "PR Benchmarking",
          description: "Precision, Recall, F1 against AMLSim-R isFraud ground truth.",
        },
        {
          icon: "⚖️",
          title: "Auto-Calibration",
          description: "Automated Bayesian threshold and weight optimization.",
        },
        {
          icon: "📊",
          title: "Drift Detection",
          description: "Rule decay monitoring and transaction distribution shift alerts.",
        },
      ]}
      primaryButtonText="View Ground Truth Labels"
      primaryButtonHref="/"
      secondaryButtonText="Open Tuning Config"
      secondaryButtonHref="/"
      footerNote="Supports AMLSim-R ground truth evaluation • SR11-7 model risk management compliant"
    />
  );
}

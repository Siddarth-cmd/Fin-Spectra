"use client";

import React, { useEffect, useState, useCallback } from "react";
import { fetchSummary, fetchAlerts } from "@/lib/api";
import { PipelineSummary, ClassifiedAlert } from "@/lib/types";
import { PipelineFlowStrip } from "@/components/dashboard/PipelineFlowStrip";
import { KpiCards } from "@/components/dashboard/KpiCards";
import { DetectionRuleChart } from "@/components/dashboard/DetectionRuleChart";
import { RiskDonutChart } from "@/components/dashboard/RiskDonutChart";
import { AlertQueueTable } from "@/components/dashboard/AlertQueueTable";
import { AlertSlideOver } from "@/components/alert-detail/AlertSlideOver";

export default function DashboardPage() {
  const [summary, setSummary] = useState<PipelineSummary | undefined>();
  const [alerts, setAlerts] = useState<ClassifiedAlert[]>([]);
  const [totalAlerts, setTotalAlerts] = useState(0);
  const [totalPages, setTotalPages] = useState(1);
  const [page, setPage] = useState(1);
  const [pageSize] = useState(5);
  const [selectedRiskLevels, setSelectedRiskLevels] = useState<string[]>([
    "CRITICAL",
    "HIGH",
  ]);
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedAlert, setSelectedAlert] = useState<ClassifiedAlert | null>(null);
  const [isLoadingSummary, setIsLoadingSummary] = useState(true);
  const [isLoadingAlerts, setIsLoadingAlerts] = useState(true);

  // Load Pipeline Summary
  const loadSummary = useCallback(async () => {
    try {
      setIsLoadingSummary(true);
      const data = await fetchSummary();
      setSummary(data);
    } catch (err) {
      console.error("Error loading summary:", err);
    } finally {
      setIsLoadingSummary(false);
    }
  }, []);

  // Load Filtered Alerts
  const loadAlerts = useCallback(async () => {
    try {
      setIsLoadingAlerts(true);
      const riskLevelParam = selectedRiskLevels.length > 0 ? selectedRiskLevels.join(",") : undefined;
      const data = await fetchAlerts({
        risk_level: riskLevelParam,
        search: searchQuery || undefined,
        page,
        page_size: pageSize,
      });
      setAlerts(data.alerts);
      setTotalAlerts(data.total);
      setTotalPages(data.total_pages);
    } catch (err) {
      console.error("Error loading alerts:", err);
    } finally {
      setIsLoadingAlerts(false);
    }
  }, [selectedRiskLevels, searchQuery, page, pageSize]);

  useEffect(() => {
    loadSummary();
  }, [loadSummary]);

  useEffect(() => {
    loadAlerts();
  }, [loadAlerts]);

  // Risk filter toggle handler
  const handleRiskFilterToggle = (risk: string) => {
    setPage(1);
    setSelectedRiskLevels((prev) =>
      prev.includes(risk) ? prev.filter((r) => r !== risk) : [...prev, risk]
    );
  };

  // Search handler
  const handleSearchChange = (query: string) => {
    setPage(1);
    setSearchQuery(query);
  };

  return (
    <div className="space-y-6">
      {/* Row 1: Pipeline Flow Strip */}
      <PipelineFlowStrip summary={summary} />

      {/* Row 2: 4 KPI Summary Cards */}
      <KpiCards summary={summary} />

      {/* Row 3: Visual Analytics (Rules Horizontal Bars + Risk Donut) */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        <div className="lg:col-span-6">
          <DetectionRuleChart summary={summary} />
        </div>
        <div className="lg:col-span-6">
          <RiskDonutChart summary={summary} />
        </div>
      </div>

      {/* Row 4: Prioritized Alert Queue Table */}
      <AlertQueueTable
        alerts={alerts}
        totalAlerts={totalAlerts}
        page={page}
        pageSize={pageSize}
        totalPages={totalPages}
        selectedRiskLevels={selectedRiskLevels}
        searchQuery={searchQuery}
        onPageChange={setPage}
        onRiskFilterToggle={handleRiskFilterToggle}
        onSearchChange={handleSearchChange}
        onSelectAlert={setSelectedAlert}
        isLoading={isLoadingAlerts}
      />

      {/* Slide-Over Inspection Drawer */}
      <AlertSlideOver
        alert={selectedAlert}
        onClose={() => setSelectedAlert(null)}
      />
    </div>
  );
}

"use client";

import { useEffect, useState } from "react";

import { BotStream } from "../../components/BotStream";
import { ChatPanel } from "../../components/ChatPanel";
import { MetricsCards } from "../../components/MetricsCards";
import { OnboardingModal } from "../../components/OnboardingModal";
import { PlanUpgradeBanner } from "../../components/PlanUpgradeBanner";
import { dashboardApi } from "../../lib/api";

interface Summary {
  total_pnl: number;
  trades: number;
  paper_mode: boolean;
}

export default function DashboardPage() {
  const [summary, setSummary] = useState<Summary | null>(null);
  const [loading, setLoading] = useState(true);
  const [showOnboarding, setShowOnboarding] = useState(false);

  useEffect(() => {
    const seen = typeof window !== "undefined" ? localStorage.getItem("investia_onboard_seen") : "true";
    setShowOnboarding(seen !== "true");
    const load = async () => {
      try {
        const res = await dashboardApi.summary();
        setSummary(res);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  const closeOnboarding = () => {
    if (typeof window !== "undefined") localStorage.setItem("investia_onboard_seen", "true");
    setShowOnboarding(false);
  };

  return (
    <main className="min-h-screen px-6 py-10 sm:px-12 lg:px-20">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-slate-400">Dashboard</p>
          <h1 className="text-3xl font-semibold">Welcome back</h1>
        </div>
      </div>

      <div className="mt-4">
        <PlanUpgradeBanner />
      </div>

      <div className="mt-6 space-y-6">
        {summary && !loading && (
          <MetricsCards totalPnl={summary.total_pnl} trades={summary.trades} paperMode={summary.paper_mode} />
        )}
        {loading && <p className="text-slate-400">Loading your summary...</p>}

        <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
          <div className="lg:col-span-2">
            <BotStream />
          </div>
          <div className="lg:col-span-1">
            <ChatPanel />
          </div>
        </div>
      </div>

      <OnboardingModal open={showOnboarding} onClose={closeOnboarding} />
    </main>
  );
}

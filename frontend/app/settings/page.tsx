"use client";

import { useState } from "react";

import { PlanUpgradeBanner } from "../../components/PlanUpgradeBanner";
import { dashboardApi } from "../../lib/api";

export default function SettingsPage() {
  const [brokerName, setBrokerName] = useState("Alpaca");
  const [apiKey, setApiKey] = useState("");
  const [apiSecret, setApiSecret] = useState("");
  const [liveTrading, setLiveTrading] = useState(false);
  const [status, setStatus] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [currentPlan] = useState("Free (paper)");

  const connect = async (e: React.FormEvent) => {
    e.preventDefault();
    setStatus(null);
    setError(null);
    try {
      await dashboardApi.connectBroker({
        broker_name: brokerName,
        api_key: apiKey,
        api_secret: apiSecret,
        live_trading_enabled: liveTrading,
      });
      setStatus("Broker connected and encrypted successfully.");
      setApiKey("");
      setApiSecret("");
    } catch (err: any) {
      setError(err?.message || "Failed to connect broker");
    }
  };

  return (
    <main className="min-h-screen px-6 py-10 sm:px-12 lg:px-20">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-slate-400">Settings</p>
          <h1 className="text-3xl font-semibold">Connectivity & Plans</h1>
        </div>
      </div>

      <div className="mt-4">
        <PlanUpgradeBanner />
      </div>

      <div className="mt-6 grid grid-cols-1 gap-4 lg:grid-cols-2">
        <div className="card p-5">
          <h3 className="text-xl font-semibold">Connect broker</h3>
          <p className="text-sm text-slate-400">Keys are encrypted with your workspace secret before storage.</p>
          <form onSubmit={connect} className="mt-4 space-y-3">
            <div className="space-y-1">
              <label className="text-sm text-slate-300">Broker</label>
              <select value={brokerName} onChange={(e) => setBrokerName(e.target.value)} className="w-full">
                {['Alpaca', 'Binance', 'Interactive Brokers', 'Robinhood'].map((broker) => (
                  <option key={broker}>{broker}</option>
                ))}
              </select>
            </div>
            <div className="space-y-1">
              <label className="text-sm text-slate-300">API Key</label>
              <input value={apiKey} onChange={(e) => setApiKey(e.target.value)} required />
            </div>
            <div className="space-y-1">
              <label className="text-sm text-slate-300">API Secret</label>
              <input value={apiSecret} onChange={(e) => setApiSecret(e.target.value)} type="password" required />
            </div>
            <label className="flex items-center gap-2 text-sm text-slate-300">
              <input type="checkbox" checked={liveTrading} onChange={(e) => setLiveTrading(e.target.checked)} />
              Enable live trading on connect
            </label>
            {status && <p className="text-sm text-emerald-300">{status}</p>}
            {error && <p className="text-sm text-rose-400">{error}</p>}
            <button
              type="submit"
              className="w-full rounded-xl bg-emerald-500 px-4 py-2 text-slate-900 font-semibold hover:bg-emerald-400"
            >
              Save connection
            </button>
          </form>
        </div>

        <div className="card p-5 space-y-4">
          <div>
            <p className="text-sm text-slate-400">Current plan</p>
            <h3 className="text-xl font-semibold">{currentPlan}</h3>
          </div>
          <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
            <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-4">
              <p className="text-sm text-emerald-300">Pro</p>
              <p className="text-slate-200">Enhanced ML model, faster refresh, broker connectivity.</p>
              <button className="mt-3 w-full rounded-xl border border-emerald-400/60 px-3 py-2 text-sm font-semibold text-emerald-200">
                Upgrade to Pro
              </button>
            </div>
            <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-4">
              <p className="text-sm text-emerald-300">Enterprise</p>
              <p className="text-slate-200">Deep data coverage, multiple brokers, dedicated support.</p>
              <button className="mt-3 w-full rounded-xl bg-emerald-500 px-3 py-2 text-sm font-semibold text-slate-900 hover:bg-emerald-400">
                Talk to us
              </button>
            </div>
          </div>
        </div>
      </div>
    </main>
  );
}

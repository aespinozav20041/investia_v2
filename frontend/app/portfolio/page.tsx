"use client";

import { useEffect, useMemo, useState } from "react";

import { dashboardApi } from "../../lib/api";

interface Metric {
  date: string;
  pnl: number;
  sharpe_ratio: number;
  win_rate: number;
}

export default function PortfolioPage() {
  const [metrics, setMetrics] = useState<Metric[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const load = async () => {
      try {
        const res = await dashboardApi.portfolioMetrics();
        setMetrics(res);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  const summary = useMemo(() => {
    const latest = metrics[0];
    const totalPnl = metrics.reduce((acc, m) => acc + m.pnl, 0);
    return {
      latestSharpe: latest?.sharpe_ratio ?? 0,
      latestWin: latest?.win_rate ?? 0,
      totalPnl,
    };
  }, [metrics]);

  return (
    <main className="min-h-screen px-6 py-10 sm:px-12 lg:px-20">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-slate-400">Portfolio</p>
          <h1 className="text-3xl font-semibold">Performance</h1>
        </div>
      </div>

      {loading && <p className="mt-4 text-slate-400">Loading portfolio metrics...</p>}

      {!loading && (
        <div className="mt-6 space-y-6">
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
            <div className="card p-4">
              <p className="text-sm text-slate-400">Latest Sharpe</p>
              <p className="text-2xl font-semibold text-emerald-300">{summary.latestSharpe.toFixed(2)}</p>
            </div>
            <div className="card p-4">
              <p className="text-sm text-slate-400">Latest win %</p>
              <p className="text-2xl font-semibold text-emerald-300">{(summary.latestWin * 100).toFixed(1)}%</p>
            </div>
            <div className="card p-4">
              <p className="text-sm text-slate-400">Total simulated PnL</p>
              <p className={`text-2xl font-semibold ${summary.totalPnl >= 0 ? "text-emerald-300" : "text-rose-400"}`}>
                {summary.totalPnl.toFixed(2)}
              </p>
            </div>
          </div>

          <div className="card p-4">
            <h3 className="text-lg font-semibold">Daily metrics</h3>
            <div className="mt-3 overflow-x-auto">
              <table className="min-w-full text-sm">
                <thead className="text-left text-slate-400">
                  <tr>
                    <th className="pb-2">Date</th>
                    <th className="pb-2">PnL</th>
                    <th className="pb-2">Sharpe</th>
                    <th className="pb-2">Win %</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800">
                  {metrics.map((metric) => (
                    <tr key={metric.date} className="text-slate-200">
                      <td className="py-2">{metric.date}</td>
                      <td className="py-2">{metric.pnl.toFixed(2)}</td>
                      <td className="py-2">{metric.sharpe_ratio.toFixed(2)}</td>
                      <td className="py-2">{(metric.win_rate * 100).toFixed(1)}%</td>
                    </tr>
                  ))}
                  {metrics.length === 0 && (
                    <tr>
                      <td colSpan={4} className="py-4 text-center text-slate-500">
                        No metrics yet. Keep the paper bot running to populate performance.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}
    </main>
  );
}

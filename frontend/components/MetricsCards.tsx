"use client";

interface MetricsCardsProps {
  totalPnl: number;
  trades: number;
  paperMode: boolean;
}

export function MetricsCards({ totalPnl, trades, paperMode }: MetricsCardsProps) {
  const cards = [
    { label: "Total simulated PnL", value: totalPnl.toFixed(2), tone: totalPnl >= 0 ? "text-emerald-400" : "text-rose-400" },
    { label: "Trades executed", value: trades.toString(), tone: "text-slate-100" },
    { label: "Mode", value: paperMode ? "Paper" : "Live", tone: paperMode ? "text-amber-300" : "text-emerald-300" },
  ];

  return (
    <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
      {cards.map((card) => (
        <div key={card.label} className="card p-4">
          <p className="text-sm text-slate-400">{card.label}</p>
          <p className={`text-2xl font-semibold ${card.tone}`}>{card.value}</p>
        </div>
      ))}
    </div>
  );
}

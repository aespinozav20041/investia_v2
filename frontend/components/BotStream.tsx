"use client";

import { useEffect, useState } from "react";

import { createWebSocket } from "../lib/websocket";

interface TradePayload {
  symbol: string;
  side: string;
  quantity: number;
  price: number;
  pnl: number;
  explanation?: string;
  created_at?: string;
}

export function BotStream() {
  const [trades, setTrades] = useState<TradePayload[]>([]);
  const [connected, setConnected] = useState(false);

  useEffect(() => {
    const ws = createWebSocket("/ws/paper-stream");
    ws.onopen = () => setConnected(true);
    ws.onclose = () => setConnected(false);
    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.type === "trade" && data.payload) {
          setTrades((prev) => [data.payload as TradePayload, ...prev].slice(0, 30));
        }
      } catch (err) {
        console.error("Failed to parse WS payload", err);
      }
    };

    return () => ws.close();
  }, []);

  return (
    <div className="card h-full p-4">
      <div className="flex items-center justify-between pb-3">
        <div>
          <p className="text-sm text-slate-400">Paper-trading feed</p>
          <h3 className="text-xl font-semibold">Bot stream</h3>
        </div>
        <span className={`flex items-center gap-2 text-sm ${connected ? "text-emerald-400" : "text-amber-400"}`}>
          <span className={`h-2 w-2 rounded-full ${connected ? "bg-emerald-400" : "bg-amber-400"}`} />
          {connected ? "Live" : "Reconnecting"}
        </span>
      </div>
      <div className="mt-2 space-y-2 max-h-[420px] overflow-y-auto pr-1">
        {trades.length === 0 && <p className="text-sm text-slate-500">Waiting for simulated trades...</p>}
        {trades.map((trade, idx) => (
          <div
            key={`${trade.symbol}-${idx}-${trade.created_at ?? idx}`}
            className="flex items-center justify-between rounded-xl border border-slate-800 bg-slate-900/60 px-3 py-2"
          >
            <div>
              <p className="text-sm text-slate-400">{trade.symbol}</p>
              <p className="text-xs text-slate-500">{trade.explanation || "Model-driven signal"}</p>
            </div>
            <div className="text-right">
              <p className={`text-sm font-semibold ${trade.side === "buy" ? "text-emerald-300" : "text-rose-300"}`}>
                {trade.side.toUpperCase()} {trade.quantity}
              </p>
              <p className="text-sm text-slate-300">@ ${trade.price}</p>
              <p className={`text-xs ${trade.pnl >= 0 ? "text-emerald-400" : "text-rose-400"}`}>
                PnL {trade.pnl.toFixed(2)}
              </p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

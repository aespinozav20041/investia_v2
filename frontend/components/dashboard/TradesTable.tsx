"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { TradeRow } from "@/lib/types";

interface Props {
  trades: TradeRow[];
}

export function TradesTable({ trades }: Props) {
  return (
    <Card>
      <CardHeader className="flex items-center justify-between">
        <CardTitle>Trades simulados</CardTitle>
        <span className="text-xs text-slate-500">Paper trading</span>
      </CardHeader>
      <CardContent>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-slate-500">
                <th className="py-2 pr-3">Fecha</th>
                <th className="py-2 pr-3">Símbolo</th>
                <th className="py-2 pr-3">Lado</th>
                <th className="py-2 pr-3">Cantidad</th>
                <th className="py-2 pr-3">Precio</th>
                <th className="py-2 pr-3 text-right">PnL</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {trades.map((trade) => (
                <tr key={trade.id} className="hover:bg-slate-50/50">
                  <td className="py-2 pr-3">{new Date(trade.timestamp).toLocaleString()}</td>
                  <td className="py-2 pr-3 font-semibold">{trade.symbol}</td>
                  <td className="py-2 pr-3">
                    <span
                      className={`rounded-full px-2 py-1 text-xs font-semibold ${trade.side === "BUY" ? "bg-emerald-50 text-emerald-700" : "bg-rose-50 text-rose-700"}`}
                    >
                      {trade.side}
                    </span>
                  </td>
                  <td className="py-2 pr-3">{trade.quantity}</td>
                  <td className="py-2 pr-3">${trade.price.toFixed(2)}</td>
                  <td className={`py-2 pr-3 text-right font-semibold ${trade.pnl >= 0 ? "text-emerald-600" : "text-rose-600"}`}>
                    {trade.pnl >= 0 ? "+" : ""}${trade.pnl.toFixed(2)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </CardContent>
    </Card>
  );
}

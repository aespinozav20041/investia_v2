"use client";

import { Area, AreaChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { PaperPerformance } from "@/lib/types";

interface Props {
  data: PaperPerformance;
}

export function PaperPerformanceCard({ data }: Props) {
  return (
    <Card>
      <CardHeader className="flex items-center justify-between">
        <CardTitle>Equity curve</CardTitle>
        <div className="text-sm text-slate-500">Bot {data.status === "running" ? "activo" : "pausado"}</div>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-2 gap-4 mb-4 text-sm">
          <Stat label="Saldo inicial" value={`$${data.initialBalance.toLocaleString()}`} />
          <Stat label="Valor actual" value={`$${data.currentBalance.toLocaleString()}`} />
          <Stat label="PnL total" value={`${data.totalPnL > 0 ? "+" : ""}$${data.totalPnL.toLocaleString()}`} />
          <Stat label="PnL diario" value={`${data.dailyPnL > 0 ? "+" : ""}$${data.dailyPnL.toLocaleString()}`} />
        </div>
        <div className="h-72">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={data.equityCurve}>
              <defs>
                <linearGradient id="colorBalance" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#3563ff" stopOpacity={0.5} />
                  <stop offset="95%" stopColor="#3563ff" stopOpacity={0} />
                </linearGradient>
              </defs>
              <XAxis dataKey="timestamp" hide />
              <YAxis hide domain={["dataMin", "dataMax"]} />
              <Tooltip formatter={(value: number) => `$${value.toLocaleString()}`} />
              <Area
                type="monotone"
                dataKey="value"
                stroke="#3563ff"
                strokeWidth={2.4}
                fill="url(#colorBalance)"
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </CardContent>
    </Card>
  );
}

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-xl border border-slate-100 bg-slate-50/60 px-4 py-3">
      <p className="text-xs text-slate-500">{label}</p>
      <p className="font-semibold text-slate-900">{value}</p>
    </div>
  );
}

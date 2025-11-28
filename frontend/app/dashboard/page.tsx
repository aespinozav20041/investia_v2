"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ConnectBrokerModal } from "@/components/dashboard/ConnectBrokerModal";
import { ModelCard } from "@/components/dashboard/ModelCard";
import { PaperPerformanceCard } from "@/components/dashboard/PaperPerformanceCard";
import { TradesTable } from "@/components/dashboard/TradesTable";
import { api } from "@/lib/api";
import type { ModelSummary, PaperPerformance, TradeRow, UserProfile } from "@/lib/types";

const mockPerformance: PaperPerformance = {
  equityCurve: Array.from({ length: 20 }).map((_, i) => ({
    timestamp: `Día ${i + 1}`,
    value: 10000 + i * 120 + Math.random() * 200,
  })),
  totalPnL: 1240,
  dailyPnL: 120,
  initialBalance: 10000,
  currentBalance: 11240,
  status: "running",
};

const mockTrades: TradeRow[] = [
  { id: "1", timestamp: new Date().toISOString(), symbol: "AAPL", side: "BUY", quantity: 10, price: 190.2, pnl: 120 },
  { id: "2", timestamp: new Date().toISOString(), symbol: "ETH-USD", side: "SELL", quantity: 0.5, price: 3400, pnl: -35 },
  { id: "3", timestamp: new Date().toISOString(), symbol: "NVDA", side: "BUY", quantity: 5, price: 850.5, pnl: 54 },
];

const mockModels: ModelSummary[] = [
  {
    id: "momentum-v3",
    name: "Momentum ML v3",
    description: "Detecta rupturas de tendencia y las confirma con señales de volumen.",
    assetClass: "Acciones US",
    sharpe: 1.9,
    drawdown: -3.4,
    historicalPnl: 32,
    price: "$49/mes",
    active: true,
  },
  {
    id: "volatility-rl",
    name: "Volatility Arbitrage RL",
    description: "Rebalanceo dinámico entre activos volátiles y defensivos usando RL.",
    assetClass: "Cripto",
    sharpe: 1.4,
    drawdown: -5.1,
    historicalPnl: 21,
    price: "$79/mes",
  },
];

export default function DashboardPage() {
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [performance, setPerformance] = useState<PaperPerformance | null>(null);
  const [trades, setTrades] = useState<TradeRow[]>([]);
  const [models, setModels] = useState<ModelSummary[]>(mockModels);
  const [message, setMessage] = useState<string | null>(null);

  useEffect(() => {
    const load = async () => {
      try {
        const me = await api.get<UserProfile>("/users/me");
        setProfile(me);
      } catch {
        setProfile({
          id: "demo",
          email: "demo@investia.live",
          state: "REGISTERED_PAPER",
          createdAt: new Date().toISOString(),
          tradesCount: mockTrades.length,
          positivePnL: true,
        });
      }

      try {
        const perf = await api.get<PaperPerformance>("/trading/paper/performance");
        setPerformance(perf);
      } catch {
        setPerformance(mockPerformance);
      }

      try {
        const tradeRows = await api.get<TradeRow[]>("/trading/paper/trades");
        setTrades(tradeRows);
      } catch {
        setTrades(mockTrades);
      }
    };

    load();
  }, []);

  const showBrokerCTA = useMemo(() => {
    if (!profile) return false;
    if (profile.state === "UNREGISTERED") return false;
    if (profile.state === "BROKER_CONNECTED" || profile.state === "ML_MODEL_ACTIVE") return false;
    return Boolean(profile.positivePnL || (profile.tradesCount ?? 0) >= 3);
  }, [profile]);

  const onPurchaseModel = async (id: string) => {
    setMessage(null);
    try {
      await api.post("/models/purchase", { modelId: id });
      setModels((prev) => prev.map((m) => (m.id === id ? { ...m, active: true } : m)));
      setMessage("Modelo activado. Las señales premium se enviarán al bot.");
    } catch (err: any) {
      setMessage(err.message || "No se pudo comprar el modelo");
    }
  };

  if (!profile || !performance) {
    return <p className="py-10 text-center text-slate-600">Cargando tu dashboard...</p>;
  }

  return (
    <div className="space-y-8">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <p className="text-sm text-slate-500">Bienvenido de vuelta</p>
          <h1 className="text-3xl font-bold text-slate-900">Paper trading en marcha</h1>
        </div>
        <div className="flex items-center gap-3 text-sm text-slate-600">
          Estado de usuario:
          <span className="rounded-full bg-brand-50 px-3 py-1 font-semibold text-brand-700">{profile.state}</span>
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <div className="lg:col-span-2">
          <PaperPerformanceCard data={performance} />
        </div>
        <div className="space-y-4">
          {showBrokerCTA && (
            <Card className="border-amber-200 bg-amber-50/80">
              <CardHeader>
                <CardTitle>Próximo paso: conecta tu broker</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3 text-sm text-amber-900">
                <p>¿Te gustaría que estas mismas señales se apliquen en tu broker real?</p>
                <ConnectBrokerModal />
              </CardContent>
            </Card>
          )}

          {profile.state === "BROKER_CONNECTED" && (
            <Card className="bg-emerald-50">
              <CardHeader>
                <CardTitle>Broker conectado</CardTitle>
              </CardHeader>
              <CardContent className="text-sm text-emerald-900">
                Las señales se enviarán a tu cuenta real. Considera activar un modelo ML premium para mayor edge.
                <div className="mt-3">
                  <Button asChild variant="outline">
                    <Link href="/models">Ver modelos</Link>
                  </Button>
                </div>
              </CardContent>
            </Card>
          )}

          <Card>
            <CardHeader>
              <CardTitle>Compra modelos premium</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <p className="text-sm text-slate-600">Añade inteligencia extra a tu bot con modelos ML listos para usar.</p>
              <div className="space-y-3">
                {models.map((model) => (
                  <ModelCard key={model.id} model={model} onPurchase={onPurchaseModel} />
                ))}
              </div>
            </CardContent>
          </Card>
          {message && <p className="text-sm text-emerald-700">{message}</p>}
        </div>
      </div>

      <TradesTable trades={trades} />
    </div>
  );
}

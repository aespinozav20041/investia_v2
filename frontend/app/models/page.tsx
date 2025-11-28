"use client";

import { useEffect, useState } from "react";
import { ModelCard } from "@/components/dashboard/ModelCard";
import { api } from "@/lib/api";
import type { ModelSummary } from "@/lib/types";

const fallbackModels: ModelSummary[] = [
  {
    id: "momentum-v3",
    name: "Momentum ML v3",
    description: "Tendencias de mediano plazo con confirmación de volumen y volatilidad.",
    assetClass: "Acciones",
    sharpe: 1.9,
    drawdown: -3.4,
    historicalPnl: 32,
    price: "$49/mes",
  },
  {
    id: "mean-reversion",
    name: "Mean Reversion Edge",
    description: "Aprovecha retrocesos en activos líquidos con stops dinámicos.",
    assetClass: "ETFs",
    sharpe: 1.5,
    drawdown: -4.2,
    historicalPnl: 18,
    price: "$59/mes",
  },
];

export default function ModelsPage() {
  const [models, setModels] = useState<ModelSummary[]>(fallbackModels);
  const [message, setMessage] = useState<string | null>(null);

  useEffect(() => {
    const loadModels = async () => {
      try {
        const response = await api.get<ModelSummary[]>("/models");
        setModels(response);
      } catch {
        // usar mocks
      }
    };
    loadModels();
  }, []);

  const onPurchaseModel = async (id: string) => {
    setMessage(null);
    try {
      await api.post("/models/purchase", { modelId: id });
      setModels((prev) => prev.map((m) => (m.id === id ? { ...m, active: true } : m)));
      setMessage("Modelo activado. Pronto podrás configurar el cobro.");
    } catch (err: any) {
      setMessage(err.message || "No se pudo procesar la compra");
    }
  };

  return (
    <div className="space-y-6 py-10">
      <div className="space-y-2">
        <p className="text-sm font-semibold uppercase tracking-[0.2em] text-brand-700">Modelos ML</p>
        <h1 className="text-3xl font-bold text-slate-900">Impulsa tus retornos con inteligencia premium</h1>
        <p className="text-slate-600">
          Activa modelos entrenados con datos de mercado en tiempo real. Deja listo el flujo para integrar pagos más adelante.
        </p>
      </div>
      <div className="grid gap-6 md:grid-cols-2">
        {models.map((model) => (
          <ModelCard key={model.id} model={model} onPurchase={onPurchaseModel} />
        ))}
      </div>
      {message && <p className="text-sm text-emerald-700">{message}</p>}
    </div>
  );
}

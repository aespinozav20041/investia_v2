"use client";

import { useMemo, useState } from "react";
import { PlanCard } from "@/components/dashboard/PlanCard";
import { api } from "@/lib/api";
import type { Plan } from "@/lib/types";

const plans: Plan[] = [
  {
    id: "freemium",
    name: "Freemium",
    price: "$0",
    description: "Paper trading con métricas básicas",
    features: ["Paper trading", "1 modelo básico", "Alertas por email"],
  },
  {
    id: "plus",
    name: "Plus",
    price: "$49/mes",
    description: "Paper + live trading en tu broker",
    features: ["Live trading", "1 broker conectado", "Modelo ML avanzado"],
    recommended: true,
  },
  {
    id: "enterprise",
    name: "Enterprise",
    price: "Custom",
    description: "Varios modelos y soporte prioritario",
    features: ["Varios modelos ML", "Más capital gestionado", "Soporte prioritario"],
  },
];

export default function PricingPage() {
  const [selectedPlan, setSelectedPlan] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);

  const ctaMessage = useMemo(() => {
    if (!selectedPlan) return "Elige un plan para continuar";
    if (selectedPlan === "freemium") return "Te llevaremos al registro para empezar gratis.";
    return "Abriremos un modal de confirmación y pronto integraremos el pago.";
  }, [selectedPlan]);

  const onSelectPlan = async (planId: string) => {
    setSelectedPlan(planId);
    setMessage(null);
    try {
      await api.post("/billing/intent", { planId });
      setMessage("Plan seleccionado. Prepara el flujo de pago/confirmación.");
    } catch {
      setMessage("Plan marcado localmente. Integraremos el endpoint real luego.");
    }
  };

  return (
    <div className="space-y-6 py-10">
      <div className="space-y-2">
        <p className="text-sm font-semibold uppercase tracking-[0.2em] text-brand-700">Planes</p>
        <h1 className="text-3xl font-bold text-slate-900">Escala a tu ritmo</h1>
        <p className="text-slate-600">Si no estás logueado te llevaremos a registrarte. Si ya tienes cuenta, confirmaremos tu plan.</p>
      </div>
      <div className="grid gap-6 md:grid-cols-3">
        {plans.map((plan) => (
          <PlanCard key={plan.id} plan={plan} onSelect={onSelectPlan} />
        ))}
      </div>
      <div className="rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-700">
        {ctaMessage}
      </div>
      {message && <p className="text-sm text-emerald-700">{message}</p>}
    </div>
  );
}

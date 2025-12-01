"use client";

import { useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";

import { billingApi } from "../../../lib/api";
import { CheckoutConfirmModal } from "../../../components/billing/CheckoutConfirmModal";
import { PlanCard } from "../../../components/billing/PlanCard";

interface BillingStatus {
  plan: string;
  upgraded_at: string | null;
  enterprise_requested: boolean;
  last_payment_id: string | null;
  last_payment_status: string | null;
}

const PLAN_COPY = {
  free: { name: "Free", price: "$0", description: "Paper trading with baseline signals." },
  pro: { name: "Pro", price: "$29/mo", description: "Advanced signals and broker connectivity." },
  enterprise: { name: "Enterprise", price: "$99/mo", description: "Premium models, priority support, multi-broker." },
};

export default function BillingPage() {
  const [status, setStatus] = useState<BillingStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [modalPlan, setModalPlan] = useState<"pro" | "enterprise" | null>(null);
  const searchParams = useSearchParams();

  const fetchStatus = async () => {
    try {
      const res = await billingApi.status();
      setStatus(res);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStatus();
  }, []);

  useEffect(() => {
    const statusParam = searchParams.get("status");
    if (statusParam) {
      fetchStatus();
    }
  }, [searchParams]);

  const isCurrent = (plan: string) => status?.plan === plan;

  const handleUpgrade = (plan: "pro" | "enterprise") => {
    setModalPlan(plan);
  };

  const confirmCheckout = async () => {
    if (!modalPlan) return;
    const res = await billingApi.createCheckout(modalPlan);
    window.location.href = res.init_point;
  };

  return (
    <main className="min-h-screen px-6 py-10 sm:px-12 lg:px-20">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-slate-400">Billing</p>
          <h1 className="text-3xl font-semibold">Manage your plan</h1>
          {status?.last_payment_status && (
            <p className="text-sm text-slate-400">Last payment: {status.last_payment_status}</p>
          )}
        </div>
      </div>

      {loading && <p className="mt-4 text-slate-400">Loading billing status...</p>}

      {!loading && status && (
        <div className="mt-6 grid grid-cols-1 gap-4 md:grid-cols-3">
          <PlanCard
            name={PLAN_COPY.free.name}
            description={PLAN_COPY.free.description}
            price={PLAN_COPY.free.price}
            isCurrent={isCurrent("free")}
            ctaLabel="Stay on Free"
            onSelect={() => {}}
          />
          <PlanCard
            name={PLAN_COPY.pro.name}
            description={PLAN_COPY.pro.description}
            price={PLAN_COPY.pro.price}
            isCurrent={isCurrent("pro")}
            ctaLabel="Upgrade to Pro"
            onSelect={() => handleUpgrade("pro")}
          />
          <PlanCard
            name={PLAN_COPY.enterprise.name}
            description={PLAN_COPY.enterprise.description}
            price={PLAN_COPY.enterprise.price}
            isCurrent={isCurrent("enterprise")}
            ctaLabel={status.enterprise_requested && !isCurrent("enterprise") ? "Requested" : "Upgrade to Enterprise"}
            onSelect={() => handleUpgrade("enterprise")}
          />
        </div>
      )}

      <CheckoutConfirmModal
        open={!!modalPlan}
        onClose={() => setModalPlan(null)}
        plan={modalPlan || "pro"}
        price={modalPlan === "enterprise" ? PLAN_COPY.enterprise.price : PLAN_COPY.pro.price}
        onConfirm={confirmCheckout}
      />
    </main>
  );
}

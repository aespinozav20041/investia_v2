"use client";

import { useState } from "react";

interface CheckoutConfirmModalProps {
  open: boolean;
  onClose: () => void;
  plan: "pro" | "enterprise";
  price: string;
  onConfirm: () => Promise<void>;
}

export function CheckoutConfirmModal({ open, onClose, plan, price, onConfirm }: CheckoutConfirmModalProps) {
  const [loading, setLoading] = useState(false);

  if (!open) return null;

  const handleConfirm = async () => {
    setLoading(true);
    try {
      await onConfirm();
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 px-4">
      <div className="card max-w-md w-full p-6">
        <h3 className="text-xl font-semibold text-slate-100">Confirm upgrade</h3>
        <p className="mt-2 text-sm text-slate-300">
          You are about to upgrade to <span className="font-semibold text-emerald-300">{plan.toUpperCase()}</span> for
          {" "}{price}/month. Continue to Mercado Pago checkout?
        </p>
        <div className="mt-4 flex justify-end gap-2">
          <button onClick={onClose} className="rounded-xl border border-slate-700 px-3 py-2 text-sm text-slate-200">
            Cancel
          </button>
          <button
            onClick={handleConfirm}
            disabled={loading}
            className="rounded-xl bg-emerald-500 px-4 py-2 text-sm font-semibold text-slate-900 hover:bg-emerald-400"
          >
            {loading ? "Redirecting..." : "Confirm"}
          </button>
        </div>
      </div>
    </div>
  );
}

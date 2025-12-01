"use client";

interface PlanCardProps {
  name: string;
  description: string;
  price: string;
  isCurrent: boolean;
  onSelect: () => void;
  ctaLabel: string;
}

export function PlanCard({ name, description, price, isCurrent, onSelect, ctaLabel }: PlanCardProps) {
  return (
    <div className={`rounded-2xl border ${isCurrent ? "border-emerald-400/70" : "border-slate-800"} bg-slate-900/60 p-5 shadow-card`}>
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-slate-400">{name}</p>
          <h3 className="text-2xl font-semibold text-slate-100">{price}</h3>
        </div>
        {isCurrent && <span className="rounded-full bg-emerald-500/20 px-3 py-1 text-xs text-emerald-200">Current</span>}
      </div>
      <p className="mt-2 text-sm text-slate-300">{description}</p>
      <button
        onClick={onSelect}
        disabled={isCurrent}
        className={`mt-4 w-full rounded-xl px-4 py-2 text-sm font-semibold ${
          isCurrent
            ? "bg-slate-800 text-slate-400 cursor-not-allowed"
            : "bg-emerald-500 text-slate-900 hover:bg-emerald-400"
        }`}
      >
        {isCurrent ? "Active" : ctaLabel}
      </button>
    </div>
  );
}

"use client";

import Link from "next/link";

export function PlanUpgradeBanner() {
  return (
    <div className="card flex flex-col gap-2 border-emerald-500/40 bg-emerald-500/10 p-4 sm:flex-row sm:items-center sm:justify-between">
      <div>
        <p className="text-sm text-emerald-200">Paper mode</p>
        <h3 className="text-lg font-semibold text-slate-100">
          Connect a broker and upgrade to Pro/Enterprise for higher fidelity models.
        </h3>
      </div>
      <Link
        href="/settings"
        className="rounded-xl bg-emerald-500 px-4 py-2 text-slate-900 font-semibold shadow-card hover:bg-emerald-400"
      >
        Go to settings
      </Link>
    </div>
  );
}

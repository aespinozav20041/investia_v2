"use client";

interface OnboardingModalProps {
  open: boolean;
  onClose: () => void;
}

export function OnboardingModal({ open, onClose }: OnboardingModalProps) {
  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 px-4">
      <div className="card max-w-lg w-full p-6">
        <div className="flex items-start justify-between">
          <div>
            <p className="text-sm text-emerald-300">Welcome to Investia</p>
            <h3 className="text-2xl font-semibold">You are in paper mode</h3>
          </div>
          <button
            onClick={onClose}
            className="rounded-full border border-slate-700 px-3 py-1 text-xs uppercase tracking-wide text-slate-200"
          >
            Close
          </button>
        </div>
        <div className="mt-4 space-y-3 text-slate-300">
          <p>
            Watch the bot stream simulated trades using order book, sentiment, and quantitative factors. Ask the bot why
            it acted, and connect your broker when you are ready to level up.
          </p>
          <ul className="list-disc pl-5 space-y-1 text-sm text-slate-400">
            <li>Live paper-trading feed with synthetic events</li>
            <li>Chat with the bot to understand model reasoning</li>
            <li>Upgrade to Plus/Enterprise for higher fidelity signals</li>
          </ul>
        </div>
      </div>
    </div>
  );
}

import Link from "next/link";

export default function HomePage() {
  return (
    <main className="min-h-screen px-6 py-10 sm:px-12 lg:px-20">
      <div className="max-w-6xl mx-auto">
        <div className="flex flex-col gap-12 lg:flex-row lg:items-center">
          <div className="flex-1 space-y-6">
            <p className="inline-flex items-center rounded-full border border-emerald-500/40 bg-emerald-500/10 px-3 py-1 text-sm text-emerald-300">
              Live paper-trading bot - Chat-native explanations
            </p>
            <h1 className="text-4xl font-bold leading-tight sm:text-5xl lg:text-6xl">
              INVESTIA helps you understand every move your trading bot makes.
            </h1>
            <p className="max-w-2xl text-lg text-slate-300">
              Start in paper mode, watch signals in real time, and ask questions in a chat interface. Connect your
              broker and upgrade to unlock higher fidelity models when you are ready.
            </p>
            <div className="flex flex-wrap items-center gap-4">
              <Link
                href="/auth/register"
                className="rounded-xl bg-emerald-500 px-5 py-3 text-slate-900 font-semibold shadow-card hover:translate-y-[-1px] hover:shadow-lg"
              >
                Get started free
              </Link>
              <Link
                href="/auth/login"
                className="rounded-xl border border-slate-700 px-5 py-3 font-semibold text-slate-100 hover:border-emerald-400/60"
              >
                I already have an account
              </Link>
            </div>
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
              {["Paper trades", "Chat explanations", "Broker upgrades"].map((item) => (
                <div key={item} className="card p-4 text-sm text-slate-300">
                  <p className="font-semibold text-slate-100">{item}</p>
                  <p className="text-slate-400">Simulated flows built to be production-ready.</p>
                </div>
              ))}
            </div>
          </div>
          <div className="flex-1">
            <div className="card p-6 backdrop-blur">
              <p className="text-sm text-emerald-300">Live bot feed</p>
              <h3 className="text-2xl font-semibold mb-4">Signals streaming in real time</h3>
              <div className="space-y-3">
                {["AAPL", "BTC-USD", "NVDA", "ETH-USD"].map((symbol, idx) => (
                  <div key={symbol} className="flex items-center justify-between rounded-xl border border-slate-800 bg-slate-900/50 px-3 py-2">
                    <div>
                      <p className="text-sm text-slate-400">{new Date(Date.now() - idx * 120000).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}</p>
                      <p className="font-semibold">{symbol}</p>
                    </div>
                    <div className="text-right">
                      <p className="text-sm text-emerald-400">Momentum + sentiment</p>
                      <p className="text-lg font-bold text-emerald-300">+{(Math.random() * 12).toFixed(2)}%</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>
  );
}

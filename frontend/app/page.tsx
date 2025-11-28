import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

const steps = [
  {
    title: "Regístrate y prueba el bot",
    description: "Crea tu cuenta y obtén acceso inmediato al paper trading sin riesgo.",
  },
  {
    title: "Mira tu PnL en vivo",
    description: "Seguimos las señales cuantitativas y te mostramos rendimiento simulado en tiempo real.",
  },
  {
    title: "Conecta tu broker o compra modelos",
    description: "Lleva las mismas señales a tu cuenta real o añade modelos ML premium.",
  },
];

const trust = ["Sin custodia de fondos", "Conexión segura por API", "Backtesting continuo"];

export default function LandingPage() {
  return (
    <main className="space-y-16">
      <section className="grid gap-10 lg:grid-cols-2 lg:items-center">
        <div className="space-y-6">
          <div className="inline-flex items-center gap-2 rounded-full bg-brand-50 px-3 py-1 text-sm font-semibold text-brand-700">
            Bots cuantitativos sin fricción
          </div>
          <div className="space-y-3">
            <h1 className="text-4xl font-bold tracking-tight text-slate-900 md:text-5xl">
              Tu bot de trading cuantitativo, sin complicarte.
            </h1>
            <p className="text-lg text-slate-600">
              Empieza en paper trading para ver cómo operamos. Cuando estés listo, conecta tu broker y deja que las señales trabajen
              por ti.
            </p>
          </div>
          <div className="flex flex-wrap items-center gap-3">
            <Button asChild size="lg">
              <Link href="/auth/register">Empieza gratis</Link>
            </Button>
            <Link href="#como-funciona" className="text-sm font-semibold text-slate-700">
              Ver cómo funciona →
            </Link>
          </div>
          <div className="flex flex-wrap gap-4 text-sm text-slate-600">
            {trust.map((item) => (
              <span key={item} className="flex items-center gap-2">
                <span className="h-2 w-2 rounded-full bg-emerald-500" />
                {item}
              </span>
            ))}
          </div>
        </div>
        <Card className="border-brand-100 bg-white/80 shadow-xl">
          <CardHeader>
            <CardTitle>Paper trading en vivo</CardTitle>
            <p className="text-sm text-slate-600">Visualiza PnL simulado y la estrategia que opera tras bambalinas.</p>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="rounded-xl bg-slate-900 p-6 text-white shadow-inner">
              <div className="flex items-center justify-between text-sm text-slate-200">
                <span>Saldo inicial</span>
                <span>$10,000</span>
              </div>
              <div className="mt-4 text-3xl font-semibold text-emerald-300">$11,240 (+12.4%)</div>
              <div className="mt-2 text-sm text-slate-300">Estrategia Momentum ML v3 en paper trading.</div>
            </div>
            <div className="grid grid-cols-3 gap-3 text-sm">
              <Metric label="Drawdown" value="-3.4%" />
              <Metric label="Sharpe" value="1.9" />
              <Metric label="Trades" value="142" />
            </div>
          </CardContent>
        </Card>
      </section>

      <section id="como-funciona" className="space-y-10">
        <div className="space-y-3">
          <p className="text-sm font-semibold uppercase tracking-[0.2em] text-brand-700">Cómo funciona</p>
          <h2 className="text-3xl font-bold text-slate-900">Empieza en minutos</h2>
          <p className="text-slate-600">Paper trading para validar, broker conectado para escalar.</p>
        </div>
        <div className="grid gap-6 md:grid-cols-3">
          {steps.map((step, index) => (
            <Card key={step.title}>
              <CardHeader>
                <div className="flex items-center justify-between text-sm text-brand-700">Paso {index + 1}</div>
                <CardTitle>{step.title}</CardTitle>
              </CardHeader>
              <CardContent className="text-slate-600">{step.description}</CardContent>
            </Card>
          ))}
        </div>
      </section>

      <section className="space-y-8">
        <div className="space-y-3">
          <p className="text-sm font-semibold uppercase tracking-[0.2em] text-brand-700">Seguridad</p>
          <h2 className="text-3xl font-bold text-slate-900">Construido para la confianza</h2>
          <p className="text-slate-600">
            Operamos solo con tus permisos del broker. Las señales viajan por API segura y puedes pausar el bot cuando quieras.
          </p>
        </div>
        <div className="grid gap-6 md:grid-cols-3">
          {["Sin custodia", "API segura", "Control total"].map((item) => (
            <Card key={item}>
              <CardHeader>
                <CardTitle>{item}</CardTitle>
              </CardHeader>
              <CardContent className="text-slate-600">
                Nunca movemos tu dinero directamente. Puedes revocar las llaves y pausar el bot en cualquier momento.
              </CardContent>
            </Card>
          ))}
        </div>
      </section>

      <section className="space-y-6">
        <div className="flex items-center justify-between">
          <div className="space-y-2">
            <h2 className="text-3xl font-bold text-slate-900">Planes para cada etapa</h2>
            <p className="text-slate-600">Empieza gratis y escala cuando estés listo.</p>
          </div>
          <Button asChild>
            <Link href="/pricing">Ver precios</Link>
          </Button>
        </div>
        <div className="grid gap-6 md:grid-cols-3">
          {[
            { title: "Freemium", price: "$0", desc: "Paper trading y métricas básicas" },
            { title: "Plus", price: "$49/mes", desc: "Paper + live trading en un broker" },
            { title: "Enterprise", price: "Custom", desc: "Varios modelos ML y soporte prioritario" },
          ].map((plan) => (
            <Card key={plan.title}>
              <CardHeader>
                <CardTitle>{plan.title}</CardTitle>
              </CardHeader>
              <CardContent className="space-y-2 text-slate-600">
                <p className="text-2xl font-semibold text-slate-900">{plan.price}</p>
                <p>{plan.desc}</p>
                <Button asChild className="w-full">
                  <Link href="/pricing">Elegir plan</Link>
                </Button>
              </CardContent>
            </Card>
          ))}
        </div>
      </section>
    </main>
  );
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-xl border border-slate-200 bg-slate-50 px-3 py-2 text-center">
      <p className="text-xs text-slate-500">{label}</p>
      <p className="text-lg font-semibold text-slate-900">{value}</p>
    </div>
  );
}

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { ModelSummary } from "@/lib/types";

interface Props {
  model: ModelSummary;
  onPurchase: (id: string) => void;
}

export function ModelCard({ model, onPurchase }: Props) {
  return (
    <Card className="h-full">
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          {model.name}
          {model.active && (
            <span className="rounded-full bg-emerald-50 px-3 py-1 text-xs font-semibold text-emerald-700">
              Activo
            </span>
          )}
        </CardTitle>
        <p className="text-sm text-slate-600">{model.description}</p>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex items-center justify-between text-sm text-slate-600">
          <span>Clase de activo</span>
          <span className="font-semibold text-slate-900">{model.assetClass}</span>
        </div>
        <div className="grid grid-cols-3 gap-3 text-sm">
          <Metric label="Sharpe" value={model.sharpe.toFixed(2)} />
          <Metric label="Drawdown" value={`${model.drawdown}%`} />
          <Metric label="PnL histórico" value={`${model.historicalPnl}%`} />
        </div>
        <div className="flex items-center justify-between">
          <div>
            <p className="text-xs text-slate-500">Precio</p>
            <p className="text-lg font-semibold text-slate-900">{model.price}</p>
          </div>
          <Button onClick={() => onPurchase(model.id)}>{model.active ? "Gestionar" : "Comprar modelo"}</Button>
        </div>
      </CardContent>
    </Card>
  );
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-xl border border-slate-100 bg-slate-50/60 px-3 py-2 text-center">
      <p className="text-xs text-slate-500">{label}</p>
      <p className="font-semibold text-slate-900">{value}</p>
    </div>
  );
}

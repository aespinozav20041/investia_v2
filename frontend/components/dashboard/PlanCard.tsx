import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { Plan } from "@/lib/types";

interface Props {
  plan: Plan;
  onSelect: (id: string) => void;
}

export function PlanCard({ plan, onSelect }: Props) {
  return (
    <Card className={`h-full ${plan.recommended ? "border-brand-300 shadow-md" : ""}`}>
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          {plan.name}
          {plan.recommended && (
            <span className="rounded-full bg-brand-50 px-3 py-1 text-xs font-semibold text-brand-700">Recomendado</span>
          )}
        </CardTitle>
        <p className="text-2xl font-semibold text-slate-900">{plan.price}</p>
        <p className="text-sm text-slate-600">{plan.description}</p>
      </CardHeader>
      <CardContent className="space-y-3">
        <ul className="space-y-2 text-sm text-slate-700">
          {plan.features.map((feature) => (
            <li key={feature} className="flex items-start gap-2">
              <span className="mt-1 h-2 w-2 rounded-full bg-brand-500" />
              <span>{feature}</span>
            </li>
          ))}
        </ul>
        <Button className="w-full" onClick={() => onSelect(plan.id)}>
          Empezar con este plan
        </Button>
      </CardContent>
    </Card>
  );
}

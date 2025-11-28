"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { BrokerConnectionPayload } from "@/lib/types";
import { api } from "@/lib/api";

interface Props {
  defaultOpen?: boolean;
}

export function ConnectBrokerModal({ defaultOpen = false }: Props) {
  const [open, setOpen] = useState(defaultOpen);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [form, setForm] = useState<BrokerConnectionPayload>({
    broker: "Alpaca",
    apiKey: "",
    apiSecret: "",
    passphrase: "",
    accountId: "",
  });

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setMessage(null);
    try {
      await api.post("/broker/connect", form);
      setMessage("Broker conectado exitosamente. El bot enviará órdenes reales.");
    } catch (err: any) {
      setMessage(err.message || "No se pudo conectar el broker");
    } finally {
      setLoading(false);
    }
  };

  if (!open) {
    return <Button onClick={() => setOpen(true)}>Conectar mi broker</Button>;
  }

  return (
    <Card className="border-brand-100 bg-white shadow-lg">
      <CardHeader>
        <CardTitle>Conecta tu broker</CardTitle>
        <p className="text-sm text-slate-600">
          Nunca tomamos custodia de tu dinero. Solo usamos tu API del broker para enviar las órdenes según las señales del bot.
        </p>
      </CardHeader>
      <CardContent>
        <form className="space-y-4" onSubmit={onSubmit}>
          <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
            <label className="text-sm font-medium text-slate-800">
              Broker
              <select
                className="mt-1 w-full rounded-lg border border-slate-200 px-3 py-2 text-sm"
                value={form.broker}
                onChange={(e) => setForm({ ...form, broker: e.target.value })}
              >
                <option>Alpaca</option>
                <option>Binance</option>
                <option>Interactive Brokers</option>
              </select>
            </label>
            <label className="text-sm font-medium text-slate-800">
              API Key
              <input
                className="mt-1 w-full rounded-lg border border-slate-200 px-3 py-2 text-sm"
                required
                value={form.apiKey}
                onChange={(e) => setForm({ ...form, apiKey: e.target.value })}
              />
            </label>
            <label className="text-sm font-medium text-slate-800">
              API Secret
              <input
                className="mt-1 w-full rounded-lg border border-slate-200 px-3 py-2 text-sm"
                required
                type="password"
                value={form.apiSecret}
                onChange={(e) => setForm({ ...form, apiSecret: e.target.value })}
              />
            </label>
            <label className="text-sm font-medium text-slate-800">
              Passphrase / Account ID
              <input
                className="mt-1 w-full rounded-lg border border-slate-200 px-3 py-2 text-sm"
                placeholder="Opcional según broker"
                value={form.passphrase}
                onChange={(e) => setForm({ ...form, passphrase: e.target.value })}
              />
            </label>
          </div>
          <Button type="submit" className="w-full" disabled={loading}>
            {loading ? "Conectando..." : "Conectar"}
          </Button>
          {message && <p className="text-sm text-slate-700">{message}</p>}
        </form>
      </CardContent>
    </Card>
  );
}

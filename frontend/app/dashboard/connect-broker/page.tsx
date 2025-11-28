"use client";

import { ConnectBrokerModal } from "@/components/dashboard/ConnectBrokerModal";

export default function ConnectBrokerPage() {
  return (
    <div className="max-w-3xl space-y-4 py-10">
      <h1 className="text-3xl font-bold text-slate-900">Conecta tu broker</h1>
      <p className="text-slate-600">
        Usa tus credenciales del broker para que el bot ejecute las mismas señales en tu cuenta real. Puedes revocar el acceso en
        cualquier momento.
      </p>
      <ConnectBrokerModal defaultOpen />
    </div>
  );
}

"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { api } from "@/lib/api";
import { saveToken } from "@/lib/auth";

interface RegisterResponse {
  access_token?: string;
}

export default function RegisterPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [acceptTerms, setAcceptTerms] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    if (password !== confirmPassword) {
      setError("Las contraseñas no coinciden");
      return;
    }
    if (!acceptTerms) {
      setError("Debes aceptar los Términos y Condiciones");
      return;
    }

    setLoading(true);
    try {
      const response = await api.post<RegisterResponse>("/auth/register", { email, password });
      if (response.access_token) {
        saveToken(response.access_token);
      }
      router.push("/dashboard");
    } catch (err: any) {
      setError(err.message || "No se pudo completar el registro");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="mx-auto max-w-lg py-10">
      <Card>
        <CardHeader>
          <CardTitle>Crea tu cuenta</CardTitle>
          <p className="text-sm text-slate-600">Empieza en paper trading y mira tu PnL en minutos.</p>
        </CardHeader>
        <CardContent>
          <form className="space-y-4" onSubmit={onSubmit}>
            <label className="block text-sm font-medium text-slate-800">
              Email
              <input
                type="email"
                required
                className="mt-1 w-full rounded-lg border border-slate-200 px-3 py-2 text-sm"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
            </label>
            <label className="block text-sm font-medium text-slate-800">
              Contraseña
              <input
                type="password"
                required
                className="mt-1 w-full rounded-lg border border-slate-200 px-3 py-2 text-sm"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
            </label>
            <label className="block text-sm font-medium text-slate-800">
              Confirmar contraseña
              <input
                type="password"
                required
                className="mt-1 w-full rounded-lg border border-slate-200 px-3 py-2 text-sm"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
              />
            </label>
            <label className="flex items-center gap-2 text-sm text-slate-700">
              <input
                type="checkbox"
                className="h-4 w-4 rounded border-slate-300"
                checked={acceptTerms}
                onChange={(e) => setAcceptTerms(e.target.checked)}
              />
              Acepto los
              <Link href="/legal" className="text-brand-700 hover:underline">
                Términos y Condiciones
              </Link>
            </label>
            {error && <p className="text-sm text-rose-600">{error}</p>}
            <Button type="submit" className="w-full" disabled={loading}>
              {loading ? "Creando cuenta..." : "Registrarme"}
            </Button>
            <p className="text-center text-sm text-slate-600">
              ¿Ya tienes cuenta? <Link href="/auth/login" className="text-brand-700 hover:underline">Inicia sesión</Link>
            </p>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}

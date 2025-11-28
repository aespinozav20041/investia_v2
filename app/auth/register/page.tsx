"use client";

import { FormEvent, useState } from "react";

type RegisterResponse = {
  id: string;
  email: string;
  plan_code: string;
  created_at: string;
};

const PLAN_CODE_DEMO = "demo";

export default function RegisterPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [message, setMessage] = useState<string | null>(null);

  const register = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setMessage(null);

    const response = await fetch("/api/v1/auth/register", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        email,
        password,
        password_confirm: confirmPassword,
        plan_code: PLAN_CODE_DEMO,
      }),
    });

    if (!response.ok) {
      setMessage("No se pudo completar el registro. Verifica los datos e inténtalo de nuevo.");
      return;
    }

    const payload = (await response.json()) as RegisterResponse;
    setMessage(`Registro creado para ${payload.email} en el plan ${payload.plan_code}`);
  };

  return (
    <main className="mx-auto max-w-md p-6">
      <h1 className="mb-4 text-2xl font-bold">Crear cuenta</h1>
      <form onSubmit={register} className="space-y-4">
        <label className="flex flex-col gap-2">
          <span>Email</span>
          <input
            type="email"
            name="email"
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            className="rounded border px-3 py-2"
            required
          />
        </label>
        <label className="flex flex-col gap-2">
          <span>Contraseña</span>
          <input
            type="password"
            name="password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            className="rounded border px-3 py-2"
            required
          />
        </label>
        <label className="flex flex-col gap-2">
          <span>Confirmar contraseña</span>
          <input
            type="password"
            name="password_confirm"
            value={confirmPassword}
            onChange={(event) => setConfirmPassword(event.target.value)}
            className="rounded border px-3 py-2"
            required
          />
        </label>
        <button type="submit" className="w-full rounded bg-blue-600 px-4 py-2 font-semibold text-white">
          Registrarme
        </button>
      </form>
      {message && <p className="mt-4 text-sm text-gray-700">{message}</p>}
    </main>
  );
}

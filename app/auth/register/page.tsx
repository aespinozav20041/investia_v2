"use client";

import { FormEvent, useState } from "react";

type RegisterResponseDetail = string | { msg?: string; detail?: string; loc?: string[] };

type RegisterFormState = {
  email: string;
  password: string;
  planCode: string;
};

function extractErrorMessage(detail: unknown): string {
  if (!detail) return "No se pudo completar el registro.";

  if (typeof detail === "string") return detail;

  if (Array.isArray(detail)) {
    const messages = detail
      .map((item: RegisterResponseDetail) => {
        if (typeof item === "string") return item;
        if (typeof item === "object" && item !== null) return item.msg ?? item.detail;
        return undefined;
      })
      .filter(Boolean);
    if (messages.length) return messages.join("; ");
  }

  if (typeof detail === "object" && detail !== null && "detail" in detail) {
    const nested = (detail as { detail?: unknown }).detail;
    if (typeof nested === "string") return nested;
  }

  return "No se pudo completar el registro.";
}

export default function RegisterPage() {
  const [form, setForm] = useState<RegisterFormState>({ email: "", password: "", planCode: "demo" });
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setLoading(true);
    setError(null);
    setMessage(null);

    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/auth/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          email: form.email,
          password: form.password,
          plan_code: form.planCode || "demo",
        }),
      });

      if (!response.ok) {
        let errorMessage = "No se pudo completar el registro.";
        try {
          const data = await response.json();
          errorMessage = extractErrorMessage((data as { detail?: unknown })?.detail);
        } catch (parseError) {
          console.error("No se pudo leer el error de la API", parseError);
        }
        throw new Error(errorMessage);
      }

      setMessage("Cuenta creada correctamente");
    } catch (requestError) {
      const friendlyMessage = requestError instanceof Error ? requestError.message : "No se pudo completar el registro.";
      setError(friendlyMessage);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h1>Registro</h1>
      <form onSubmit={handleSubmit}>
        <div>
          <label htmlFor="email">Correo</label>
          <input
            id="email"
            name="email"
            type="email"
            required
            value={form.email}
            onChange={(event) => setForm({ ...form, email: event.target.value })}
          />
        </div>
        <div>
          <label htmlFor="password">Contraseña</label>
          <input
            id="password"
            name="password"
            type="password"
            required
            value={form.password}
            onChange={(event) => setForm({ ...form, password: event.target.value })}
          />
        </div>
        <div>
          <label htmlFor="plan_code">Plan</label>
          <input
            id="plan_code"
            name="plan_code"
            type="text"
            placeholder="demo"
            value={form.planCode}
            onChange={(event) => setForm({ ...form, planCode: event.target.value })}
          />
        </div>
        <button type="submit" disabled={loading}>
          {loading ? "Registrando..." : "Registrarse"}
        </button>
      </form>
      {message && <p>{message}</p>}
      {error && <p role="alert">{error}</p>}
    </div>
  );
}

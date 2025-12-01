"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

import { authStore } from "../../../lib/auth";
import { authApi } from "../../../lib/api";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      const res = await authApi.login(email, password);
      authStore.save(res.access_token);
      router.push("/dashboard");
    } catch (err: any) {
      setError(err?.message || "Unable to login");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen px-6 py-10 sm:px-12 lg:px-20">
      <div className="mx-auto max-w-md card p-6">
        <h1 className="text-2xl font-semibold">Welcome back</h1>
        <p className="text-sm text-slate-400">Log in to see your paper-trading feed.</p>
        <form onSubmit={handleSubmit} className="mt-4 space-y-3">
          <div className="space-y-1">
            <label className="text-sm text-slate-300">Email</label>
            <input value={email} onChange={(e) => setEmail(e.target.value)} type="email" required />
          </div>
          <div className="space-y-1">
            <label className="text-sm text-slate-300">Password</label>
            <input
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              type="password"
              minLength={6}
              required
            />
          </div>
          {error && <p className="text-sm text-rose-400">{error}</p>}
          <button
            type="submit"
            disabled={loading}
            className="w-full rounded-xl bg-emerald-500 px-4 py-2 text-slate-900 font-semibold hover:bg-emerald-400"
          >
            {loading ? "Signing in..." : "Log in"}
          </button>
        </form>
        <p className="mt-3 text-sm text-slate-400">
          Need an account? <a href="/auth/register" className="text-emerald-300">Register</a>
        </p>
      </div>
    </main>
  );
}

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

type RequestOptions = RequestInit & { auth?: boolean };

export async function apiFetch<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const { auth, ...rest } = options;
  const headers: HeadersInit = {
    "Content-Type": "application/json",
    ...(rest.headers || {}),
  };

  if (auth && typeof window !== "undefined") {
    const token = localStorage.getItem("access_token");
    if (token) headers["Authorization"] = `Bearer ${token}`;
  }

  const res = await fetch(`${API_URL}${path}`, {
    ...rest,
    headers,
  });

  if (!res.ok) {
    const message = await res.text();
    throw new Error(message || res.statusText);
  }

  return res.json();
}

export const authApi = {
  async register(email: string, password: string) {
    return apiFetch<{ access_token: string }>(`/api/v1/auth/register`, {
      method: "POST",
      body: JSON.stringify({ email, password }),
    });
  },
  async login(email: string, password: string) {
    return apiFetch<{ access_token: string }>(`/api/v1/auth/login`, {
      method: "POST",
      body: JSON.stringify({ email, password }),
    });
  },
};

export const dashboardApi = {
  async summary() {
    return apiFetch<{ total_pnl: number; trades: number; paper_mode: boolean }>(`/api/v1/dashboard/summary`, {
      auth: true,
    });
  },
  async portfolioMetrics() {
    return apiFetch<Array<{ date: string; pnl: number; sharpe_ratio: number; win_rate: number }>>(
      `/api/v1/portfolio/metrics`,
      { auth: true }
    );
  },
  async askChat(question: string, tradeId?: number) {
    return apiFetch<{ answer: string }>(`/api/v1/chat/ask`, {
      method: "POST",
      auth: true,
      body: JSON.stringify({ question, trade_id: tradeId }),
    });
  },
  async connectBroker(payload: { broker_name: string; api_key: string; api_secret: string; live_trading_enabled?: boolean }) {
    return apiFetch<{ id: number; broker_name: string; is_live_trading_enabled: boolean }>(`/api/v1/brokers/connect`, {
      method: "POST",
      auth: true,
      body: JSON.stringify(payload),
    });
  },
};

export const WS_URL = process.env.NEXT_PUBLIC_API_WS_URL || "ws://localhost:8000";

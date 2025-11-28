const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL;

type HttpMethod = "GET" | "POST" | "PUT" | "PATCH" | "DELETE";

async function request<T>(path: string, options: RequestInit & { method?: HttpMethod } = {}): Promise<T> {
  if (!API_BASE_URL) {
    console.warn("NEXT_PUBLIC_API_URL no está configurado; usando datos mock.");
  }

  const res = await fetch(`${API_BASE_URL ?? ""}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
    ...options,
  });

  if (!res.ok) {
    const errorBody = await res.json().catch(() => ({}));
    throw new Error(errorBody.detail || "Ocurrió un error en la solicitud");
  }

  return res.json();
}

export const api = {
  get: <T>(path: string) => request<T>(path, { method: "GET" }),
  post: <T>(path: string, body?: unknown) =>
    request<T>(path, { method: "POST", body: body ? JSON.stringify(body) : undefined }),
};

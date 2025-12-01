"use client";

import { FormEvent, useState } from "react";

import { dashboardApi } from "../lib/api";

interface ChatMessage {
  role: "user" | "assistant";
  content: string;
}

export function ChatPanel() {
  const [messages, setMessages] = useState<ChatMessage[]>([
    { role: "assistant", content: "Ask me why the bot took a trade or which data sources it is tracking right now." },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  const sendMessage = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!input.trim()) return;
    const userMessage: ChatMessage = { role: "user", content: input.trim() };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setLoading(true);
    try {
      const res = await dashboardApi.askChat(userMessage.content);
      setMessages((prev) => [...prev, { role: "assistant", content: res.answer }]);
    } catch (err: any) {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: err?.message || "Unable to reach chat service" },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card flex h-full flex-col p-4">
      <div className="pb-3">
        <p className="text-sm text-slate-400">Chat with your bot</p>
        <h3 className="text-xl font-semibold">Explain decisions</h3>
      </div>
      <div className="flex-1 space-y-3 overflow-y-auto rounded-xl border border-slate-800 bg-slate-900/60 p-3">
        {messages.map((message, idx) => (
          <div key={idx} className="space-y-1">
            <p className="text-xs uppercase tracking-wide text-slate-500">{message.role}</p>
            <p className="leading-relaxed text-slate-200">{message.content}</p>
          </div>
        ))}
      </div>
      <form onSubmit={sendMessage} className="mt-3 flex flex-col gap-2">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask anything: why did the bot buy NVDA?"
          className="w-full rounded-xl border border-slate-800 bg-slate-900 px-3 py-2 text-sm"
        />
        <button
          type="submit"
          disabled={loading}
          className="inline-flex items-center justify-center rounded-xl bg-emerald-500 px-4 py-2 font-semibold text-slate-900 hover:bg-emerald-400"
        >
          {loading ? "Thinking..." : "Send"}
        </button>
      </form>
    </div>
  );
}

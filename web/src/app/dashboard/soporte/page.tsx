"use client";
import { useEffect, useState } from "react";

type Ticket = {
  id: number;
  firstName: string;
  lastName: string;
  email: string;
  reason: string;
  status: string;
  createdAt: string;
  assignedTo?: { id: number; name: string } | null;
  _count: { messages: number };
};

type Message = { id: number; author: "user" | "agent"; name?: string | null; body: string; createdAt: string };

export default function SoportePage() {
  const [tickets, setTickets] = useState<Ticket[]>([]);
  const [selected, setSelected] = useState<number | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [text, setText] = useState("");
  const [loading, setLoading] = useState(false);

  // cargar tickets
  async function loadTickets() {
    const res = await fetch("/api/support/tickets", { cache: "no-store" });
    const data = await res.json();
    if (data.ok) setTickets(data.tickets as Ticket[]);
  }

  // cargar mensajes del ticket seleccionado
  async function loadMessages(id: number) {
    const res = await fetch(`/api/support/tickets/${id}/messages`, { cache: "no-store" });
    const data = await res.json();
    if (data.ok) setMessages(data.messages as Message[]);
  }

  useEffect(() => {
    loadTickets();
    const i = setInterval(loadTickets, 10_000); // refresco liviano
    return () => clearInterval(i);
  }, []);

  useEffect(() => {
    if (!selected) return;
    loadMessages(selected);
    const i = setInterval(() => loadMessages(selected), 5_000); // refresco chat
    return () => clearInterval(i);
  }, [selected]);

  async function send() {
    if (!selected || !text.trim()) return;
    setLoading(true);
    const res = await fetch(`/api/support/tickets/${selected}/messages`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ body: text }),
    });
    setLoading(false);
    if (res.ok) {
      setText("");
      loadMessages(selected);
    }
  }

  return (
    <section className="max-w-6xl mx-auto px-4 py-8 grid md:grid-cols-[280px_1fr] gap-6">
      <aside className="rounded-xl border p-3 h-[70vh] overflow-auto bg-white">
        <h2 className="font-semibold mb-3">Tickets</h2>
        <ul className="space-y-2">
          {tickets.map(t => (
            <li key={t.id}>
              <button
                onClick={() => setSelected(t.id)}
                className={`w-full text-left p-2 rounded border hover:bg-slate-50 ${selected===t.id ? "bg-slate-100" : ""}`}
              >
                <div className="font-medium">#{t.id} {t.firstName} {t.lastName}</div>
                <div className="text-xs text-slate-500">
                  {t.reason} · {new Date(t.createdAt).toLocaleString()} · {t._count.messages} msgs
                </div>
              </button>
            </li>
          ))}
        </ul>
      </aside>

      <div className="rounded-xl border p-4 bg-white">
        <div className="h-[60vh] rounded border bg-slate-50 p-4 overflow-auto">
          {!selected ? (
            <div className="text-slate-500">Selecciona un ticket para ver el chat.</div>
          ) : (
            <ul className="space-y-3">
              {messages.map(m => (
                <li key={m.id} className={m.author === "agent" ? "text-right" : ""}>
                  <div className="inline-block max-w-[80%] rounded-xl px-3 py-2
                                  bg-white shadow-sm border
                                  {m.author === 'agent' ? 'bg-brand text-white border-transparent' : ''}">
                    <div className="text-xs opacity-70">
                      {m.author === "agent" ? (m.name ?? "Agente") : (m.name ?? "Usuario")}
                      {" · "}{new Date(m.createdAt).toLocaleString()}
                    </div>
                    <div className="whitespace-pre-wrap">{m.body}</div>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </div>

        <div className="mt-3 flex gap-2">
          <input
            className="flex-1 border p-2 rounded"
            placeholder="Escribe un mensaje..."
            value={text}
            onChange={(e) => setText(e.target.value)}
            disabled={!selected || loading}
          />
          <button
            onClick={send}
            disabled={!selected || loading || !text.trim()}
            className="px-4 rounded bg-brand text-white disabled:opacity-60"
          >
            {loading ? "Enviando..." : "Enviar"}
          </button>
        </div>
      </div>
    </section>
  );
}

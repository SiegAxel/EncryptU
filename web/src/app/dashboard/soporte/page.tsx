"use client";

import { useCallback, useEffect, useMemo, useRef, useState } from "react";

type Ticket = {
  id: number;
  firstName: string;
  lastName: string;
  email: string;
  reason: string;      // "soporte" | "consulta"
  status: string;      // "open" | "closed" | etc
  createdAt: string;   // ISO
  _count?: { messages?: number };
};

type Message = {
  id: number;
  author: "user" | "agent";
  name?: string | null;
  body: string;
  createdAt: string; // ISO
};

const fmtTime = (iso: string) =>
  new Intl.DateTimeFormat(undefined, { hour: "2-digit", minute: "2-digit" }).format(
    new Date(iso)
  );

// ───────── badges con chips ─────────
const ReasonBadge = ({ reason }: { reason: string }) => (
  <span className={"chip " + (reason === "soporte" ? "chip--brand" : "chip--accent")}>
    {reason}
  </span>
);

const StatusBadge = ({ status }: { status: string }) => {
  const map: Record<string, string> = {
    open: "chip chip--success",
    closed: "chip",
    pending: "chip chip--accent",
  };
  return <span className={map[status] ?? "chip"}>{status}</span>;
};

export default function SoportePage() {
  const [tickets, setTickets] = useState<Ticket[] | null>(null);
  const [filter, setFilter] = useState("");
  const [activeId, setActiveId] = useState<number | null>(null);
  const [messages, setMessages] = useState<Message[] | null>(null);
  const [sending, setSending] = useState(false);
  const [draft, setDraft] = useState("");
  const listRef = useRef<HTMLDivElement>(null);

  // cargar tickets
  const loadTickets = useCallback(async () => {
    const res = await fetch("/api/support/tickets", { cache: "no-store" });
    const data = await res.json();
    if (data.ok) {
      setTickets(data.tickets as Ticket[]);
      if (!activeId && data.tickets.length) setActiveId(data.tickets[0].id);
    } else {
      setTickets([]);
    }
  }, [activeId]);

  // cargar mensajes del ticket activo
  const loadMessages = useCallback(async () => {
    if (!activeId) return;
    const res = await fetch(`/api/support/tickets/${activeId}/messages`, { cache: "no-store" });
    const data = await res.json();
    if (data.ok) setMessages(data.messages as Message[]);
    else setMessages([]);
  }, [activeId]);

  // inicial + refresco periódico
  useEffect(() => {
    loadTickets();
    const i = setInterval(loadTickets, 15_000);
    return () => clearInterval(i);
  }, [loadTickets]);

  useEffect(() => {
    loadMessages();
    const i = setInterval(loadMessages, 5_000);
    return () => clearInterval(i);
  }, [loadMessages]);

  // autoscroll
  useEffect(() => {
    if (!listRef.current) return;
    listRef.current.scrollTop = listRef.current.scrollHeight;
  }, [messages]);

  const activeTicket = useMemo(
    () => tickets?.find((t) => t.id === activeId) ?? null,
    [tickets, activeId]
  );

  const filtered = useMemo(() => {
    if (!tickets) return null;
    const q = filter.trim().toLowerCase();
    if (!q) return tickets;
    return tickets.filter(
      (t) =>
        `${t.firstName} ${t.lastName} ${t.email} ${t.reason}`.toLowerCase().includes(q) ||
        String(t.id).includes(q)
    );
  }, [tickets, filter]);

  // enviar mensaje
  const send = async () => {
    if (!activeId || !draft.trim()) return;
    setSending(true);
    const res = await fetch(`/api/support/tickets/${activeId}/messages`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ body: draft }),
    });
    setSending(false);
    if (res.ok) {
      setDraft("");
      loadMessages();
    }
  };

  const onKeyDown: React.KeyboardEventHandler<HTMLInputElement> = (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {
      e.preventDefault();
      void send();
    }
  };

  return (
    <section className="mx-auto grid max-w-6xl grid-cols-1 gap-6 px-4 py-8 md:grid-cols-[320px_1fr]">
      {/* Sidebar */}
      <aside className="rounded-2xl border p-3 bg-white/80 bg-tickets-surface">
        <div className="mb-3 flex items-center justify-between">
          <h2 className="text-sm font-semibold">Tickets</h2>
          <span className="text-xs text-slate-500">{tickets?.length ?? 0} total</span>
        </div>

        <div className="mb-3">
          <input
            className="input w-full"
            placeholder="Buscar por nombre, mail, #id…"
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
          />
        </div>

        <div className="space-y-2 overflow-auto pr-1" style={{ maxHeight: "68vh" }}>
          {!filtered ? (
            <TicketSkeleton />
          ) : filtered.length === 0 ? (
            <EmptyState text="Sin resultados" />
          ) : (
            filtered.map((t) => (
              <button
                key={t.id}
                onClick={() => setActiveId(t.id)}
                className={[
                  "w-full rounded-xl border px-3 py-2 text-left transition",
                  activeId === t.id ? "ticket-item--active" : "hover:bg-slate-50"
                ].join(" ")}

              >
                <div className="flex items-center justify-between gap-2">
                  <div className="truncate text-[13px] font-medium">
                    #{t.id} {t.firstName} {t.lastName}
                  </div>
                  <ReasonBadge reason={t.reason} />
                </div>
                <div className="mt-1 flex items-center justify-between text-[11px] text-slate-500">
                  <span className="truncate">{t.email}</span>
                  <span>{t._count?.messages ?? 0} msgs</span>
                </div>
              </button>
            ))
          )}
        </div>
      </aside>

      {/* Chat */}
      <div className="rounded-2xl border overflow-hidden">
        {/* Header chat */}
        <div className="flex items-center justify-between gap-3 border-b bg-white/70 px-4 py-3">
          {activeTicket ? (
            <>
              <div className="min-w-0">
                <div className="flex items-center gap-2">
                  <h3 className="truncate text-sm font-semibold">
                    Ticket #{activeTicket.id} — {activeTicket.firstName} {activeTicket.lastName}
                  </h3>
                  <ReasonBadge reason={activeTicket.reason} />
                  <StatusBadge status={activeTicket.status} />
                </div>
                <div className="truncate text-xs text-slate-500">{activeTicket.email}</div>
              </div>
              <span className="text-xs text-slate-500">
                {new Intl.DateTimeFormat(undefined, { dateStyle: "medium" }).format(
                  new Date(activeTicket.createdAt)
                )}
              </span>
            </>
          ) : (
            <div className="text-sm text-slate-500">Selecciona un ticket…</div>
          )}
        </div>

        {/* Mensajes */}
        <div
          ref={listRef}
          className="h-[60vh] overflow-auto bg-slate-50 bg-chat-surface px-3 py-4"
        >
          {!activeTicket ? (
            <div className="flex h-full items-center justify-center text-sm text-slate-600">
              Selecciona un ticket para ver el chat.
            </div>
          ) : !messages ? (
            <MessagesSkeleton />
          ) : messages.length === 0 ? (
            <EmptyState text="Aún no hay mensajes en este ticket." />
          ) : (
            <div className="space-y-2">
              {messages.map((m) => (
                <div
                  key={m.id}
                  className={"flex " + (m.author === "agent" ? "justify-end" : "justify-start")}
                >
                  <div
                    className={[
                      "max-w-[80%] rounded-2xl px-3 py-2 shadow-sm",
                      m.author === "agent"
                        ? "bubble bubble--agent"
                        : "bubble bubble--user border"
                    ].join(" ")}
                  >
                    <div className="text-[11px] opacity-80">
                      {m.author === "agent" ? m.name || "soporte" : "usuario"} · {fmtTime(m.createdAt)}
                    </div>
                    <div className="whitespace-pre-wrap text-sm leading-relaxed">{m.body}</div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Composer */}
        <form
          className="flex items-center gap-2 border-t bg-white/80 p-3"
          onSubmit={(e) => {
            e.preventDefault();
            void send();
          }}
        >
          <input
            className="input flex-1"
            placeholder="Escribe un mensaje…  (Ctrl/⌘ + Enter para enviar)"
            value={draft}
            onChange={(e) => setDraft(e.target.value)}
            onKeyDown={onKeyDown}
            disabled={!activeTicket || sending}
          />
          <button
            type="submit"
            disabled={!activeTicket || !draft.trim() || sending}
            className="btn-brand rounded-lg px-4 py-2 text-sm font-medium disabled:opacity-50"
          >
            {sending ? "Enviando…" : "Enviar"}
          </button>

        </form>
      </div>
    </section>
  );
}

/* ── estados ─────────────────────────── */

function EmptyState({ text }: { text: string }) {
  return (
    <div className="rounded-xl border border-dashed bg-white/70 p-6 text-center text-sm text-slate-600">
      {text}
    </div>
  );
}

function TicketSkeleton() {
  return (
    <div className="space-y-2">
      {[...Array(5)].map((_, i) => (
        <div key={i} className="h-12 animate-pulse rounded-xl border bg-white/70" />
      ))}
    </div>
  );
}

function MessagesSkeleton() {
  return (
    <div className="space-y-2">
      {[...Array(5)].map((_, i) => (
        <div key={i} className={"flex " + (i % 2 ? "justify-end" : "justify-start")}>
          <div className="h-12 w-1/2 animate-pulse rounded-2xl bg-slate-200/70" />
        </div>
      ))}
    </div>
  );
}

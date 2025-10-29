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
  const [tab, setTab] = useState<"pending" | "resolved">("pending");
  const listRef = useRef<HTMLDivElement>(null);
  const [closing, setClosing] = useState(false);

  // helpers de lista
  const pending = useMemo(() => (tickets ?? []).filter(t => t.status !== "closed"), [tickets]);
  const resolved = useMemo(() => (tickets ?? []).filter(t => t.status === "closed"), [tickets]);

  const displayed = useMemo(() => {
    const base = tab === "pending" ? pending : resolved;
    const q = filter.trim().toLowerCase();
    if (!q) return base;
    return base.filter(
      (t) =>
        `${t.firstName} ${t.lastName} ${t.email} ${t.reason}`.toLowerCase().includes(q) ||
        String(t.id).includes(q)
    );
  }, [tab, pending, resolved, filter]);

  // cargar tickets
  const loadTickets = useCallback(async () => {
    const res = await fetch("/api/support/tickets", { cache: "no-store" });
    const data = await res.json();
    if (data.ok) {
      const list = data.tickets as Ticket[];
      setTickets(list);

      if (!activeId) {
        const firstVisible =
          (tab === "pending" ? list.filter(l => l.status !== "closed") : list.filter(l => l.status === "closed"))[0]
          ?? list[0];
        if (firstVisible) setActiveId(firstVisible.id);
      } else {
        if (!list.find(t => t.id === activeId)) {
          const first = list[0];
          setActiveId(first ? first.id : null);
        }
      }
    } else {
      setTickets([]);
    }
  }, [activeId, tab]);

  // cargar mensajes del ticket activo
  const loadMessages = useCallback(async () => {
    if (!activeId) return;
    const res = await fetch(`/api/support/tickets/${activeId}/messages`, { cache: "no-store" });
    const data = await res.json();
    if (data.ok) setMessages(data.messages as Message[]);
    else setMessages([]);
  }, [activeId]);

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

  useEffect(() => {
    if (!tickets) return;
    const list = tab === "pending" ? pending : resolved;
    if (!activeId || !list.find(t => t.id === activeId)) {
      setActiveId(list[0]?.id ?? null);
    }
  }, [tab, tickets, pending, resolved, activeId]);

  // autoscroll
  useEffect(() => {
    if (!listRef.current) return;
    listRef.current.scrollTop = listRef.current.scrollHeight;
  }, [messages]);

  const activeTicket = useMemo(
    () => tickets?.find((t) => t.id === activeId) ?? null,
    [tickets, activeId]
  );

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
      <aside className="tickets-sidebar p-3">
        <div className="mb-3 flex items-center justify-between">
          <h2 className="text-sm font-semibold">Tickets</h2>
          <span className="text-xs text-slate-500">{tickets?.length ?? 0} total</span>
        </div>

        {/* Tabs: Pendientes / Resueltos */}
        <div className="mb-3 flex gap-2">
          <button
            className={[
              "rounded-lg px-3 py-1 text-xs border",
              tab === "pending" ? "bg-white shadow-sm border-slate-300" : "hover:bg-slate-50 border-transparent"
            ].join(" ")}
            onClick={() => setTab("pending")}
          >
            Pendientes <span className="ml-1 chip chip--success">{pending.length}</span>
          </button>
          <button
            className={[
              "rounded-lg px-3 py-1 text-xs border",
              tab === "resolved" ? "bg-white shadow-sm border-slate-300" : "hover:bg-slate-50 border-transparent"
            ].join(" ")}
            onClick={() => setTab("resolved")}
          >
            Resueltos <span className="ml-1 chip">{resolved.length}</span>
          </button>
        </div>

        <div className="mb-3">
          <input
            className="input w-full"
            placeholder="Buscar por nombre, mail, #id…"
            width={2}
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
          />
        </div>

        <div className="space-y-2 overflow-auto pr-1" style={{ maxHeight: "68vh" }}>
          {tickets === null ? (
            <TicketSkeleton />
          ) : displayed.length === 0 ? (
            <EmptyState text={tab === "pending" ? "No hay tickets pendientes" : "No hay tickets resueltos"} />
          ) : (
            displayed.map((t) => (
              <button
                key={t.id}
                onClick={() => setActiveId(t.id)}
                className={["ticket-item w-full text-left", activeId === t.id ? "ticket-item--active" : ""].join(" ")}
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
      <div className="ticket-chat overflow-hidden">
        {/* Header chat */}
        <div className="ticket-header flex items-center justify-between gap-3 px-4 py-3 rounded-t-[1.1rem]">
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

              <div className="flex items-center gap-3">
                <span className="text-xs text-slate-500">
                  {new Intl.DateTimeFormat(undefined, { dateStyle: "medium" }).format(
                    new Date(activeTicket.createdAt)
                  )}
                </span>

                {activeTicket.status !== "closed" && (
                  <button
                    onClick={async () => {
                      try {
                        setClosing(true);
                        const res = await fetch(`/api/support/tickets/${activeTicket.id}/close`, { method: "POST" });
                        const data = await res.json();
                        if (!res.ok) throw new Error(data?.error || "Error al cerrar el ticket");
                        await loadTickets();
                        await loadMessages();
                      } catch (e) {
                        alert((e as Error).message);
                      } finally {
                        setClosing(false);
                      }
                    }}
                    className="btn-outline text-xs px-3 py-1.5 disabled:opacity-50"
                    disabled={closing}
                    title="Cerrar ticket"
                  >
                    {closing ? "Cerrando…" : "Cerrar Ticket"}
                  </button>
                )}
              </div>
            </>
          ) : (
            <div className="text-sm text-slate-500">Selecciona un ticket…</div>
          )}
        </div>

        {/* Mensajes */}
        <div ref={listRef} className="h-[60vh] overflow-auto px-3 py-4">
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
                <div key={m.id} className={"flex " + (m.author === "agent" ? "justify-end" : "justify-start")}>
                  <div
                    className={[
                      "max-w-[80%] rounded-2xl px-3 py-2 shadow-sm",
                      m.author === "agent" ? "bubble bubble--agent" : "bubble bubble--user border"
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
        {activeTicket && activeTicket.status === "closed" ? (
          <div className="flex items-center justify-center border-t bg-white/80 p-4 text-sm text-slate-500">
            Este ticket está <span className="ml-1 font-medium text-rose-600">cerrado</span>. No se pueden enviar más mensajes.
          </div>
        ) : (
          <form
            className="flex items-center gap-2 border-t bg-white/80 p-3"
            onSubmit={(e) => {
              e.preventDefault();
              void send();
            }}
          >
            <input
              className="ticket-input input flex-1"
              placeholder="Escribe un mensaje…  (Ctrl/⌘ + Enter para enviar)"
              value={draft}
              onChange={(e) => setDraft(e.target.value)}
              onKeyDown={onKeyDown}
              disabled={!activeTicket || sending}
            />
            <button
              type="submit"
              disabled={!activeTicket || !draft.trim() || sending}
              className="ticket-send disabled:opacity-50"
            >
              {sending ? "Enviando…" : "Enviar"}
            </button>
          </form>
        )}
      </div>
    </section>
  );
}

/* ── estados ─────────────────────────── */

function EmptyState({ text }: { text: string }) {
  return <div className="ticket-empty">{text}</div>;
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

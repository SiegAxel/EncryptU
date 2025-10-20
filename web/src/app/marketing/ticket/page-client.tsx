"use client";

import { useMemo, useState } from "react";

/* Tipos */
type Ticket = {
    id: number;
    reason: string;
    status: string;        // "open" | "closed" | ...
    createdAt: string;     // ISO string
    _count: { messages: number };
};

type Message = {
    id: number;
    author: "user" | "agent";
    name?: string | null;
    body: string;
    createdAt: string;     // ISO string
};

export default function TicketsPageClient({ tickets = [] as Ticket[] }) {
    // UI state
    const [openId, setOpenId] = useState<number | null>(null);
    const [messagesById, setMessagesById] = useState<Record<number, Message[]>>({});
    const [loadingId, setLoadingId] = useState<number | null>(null);
    const [sendingId, setSendingId] = useState<number | null>(null);
    const [draftById, setDraftById] = useState<Record<number, string>>({});
    const [filter, setFilter] = useState("");

    /* Helpers de formato */
    const fmtDT = (iso: string) =>
        new Intl.DateTimeFormat(undefined, { dateStyle: "medium", timeStyle: "short" }).format(
            new Date(iso)
        );
    const fmtTime = (iso: string) =>
        new Intl.DateTimeFormat(undefined, { hour: "2-digit", minute: "2-digit" }).format(
            new Date(iso)
        );

    /* Secciones */
    const pending = useMemo(() => tickets.filter(t => t.status !== "closed"), [tickets]);
    const resolved = useMemo(() => tickets.filter(t => t.status === "closed"), [tickets]);

    const filterFn = (t: Ticket) => {
        const q = filter.trim().toLowerCase();
        if (!q) return true;
        return (`${t.id} ${t.reason} ${t.status}`).toLowerCase().includes(q);
    };

    const pendFiltered = useMemo(() => pending.filter(filterFn), [pending, filter]);
    const resoFiltered = useMemo(() => resolved.filter(filterFn), [resolved, filter]);

    /* Cargar mensajes al abrir un acordeón */
    async function toggle(id: number) {
        if (openId === id) {
            setOpenId(null);
            return;
        }
        setOpenId(id);

        if (!messagesById[id]) {
            setLoadingId(id);
            try {
                const res = await fetch(`/api/userTicket?ticketId=${id}`, { cache: "no-store" });
                const data = await res.json();
                setMessagesById(m => ({
                    ...m,
                    [id]: (res.ok && data.ok ? (data.messages as Message[]) : []),
                }));
            } finally {
                setLoadingId(null);
            }
        }
    }

    /* Enviar mensaje del usuario (solo si el ticket no está cerrado) */
    async function sendMessage(ticketId: number) {
        const draft = (draftById[ticketId] ?? "").trim();
        if (!draft) return;

        setSendingId(ticketId);
        try {
            const res = await fetch("/api/userTicket", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ ticketId, body: draft }),
            });
            const data = await res.json();

            if (!res.ok || !data.ok) {
                alert(data?.error || "No se pudo enviar el mensaje");
                return;
            }

            // Añade el nuevo mensaje al final de la conversación
            setMessagesById(m => ({
                ...m,
                [ticketId]: [...(m[ticketId] ?? []), data.message as Message],
            }));
            setDraftById(d => ({ ...d, [ticketId]: "" }));
        } finally {
            setSendingId(null);
        }
    }

    return (
        <section className="container-default my-8 rounded-2xl overflow-hidden bg-split-element-v p-6">
            <h1 className="mb-4 text-xl font-semibold">Mis tickets</h1>

            <div className="mb-3">
                <input
                    className="input w-full md:w-96"
                    placeholder="Buscar por asunto, estado o #id…"
                    value={filter}
                    onChange={(e) => setFilter(e.target.value)}
                />
            </div>

            {tickets.length === 0 ? (
                <p className="text-slate-600">Aún no has enviado tickets.</p>
            ) : (
                <div className="space-y-6">
                    {/* ── Pendientes ───────────────────────────── */}
                    <SectionHeader title="Pendientes" count={pending.length} accent />
                    <TicketList
                        items={pendFiltered}
                        openId={openId}
                        onToggle={toggle}
                        messagesById={messagesById}
                        loadingId={loadingId}
                        sendingId={sendingId}
                        draftById={draftById}
                        setDraftById={setDraftById}
                        sendMessage={sendMessage}
                        fmtDT={fmtDT}
                        fmtTime={fmtTime}
                    />

                    {/* ── Resueltos ────────────────────────────── */}
                    <SectionHeader title="Resueltos" count={resolved.length} />
                    <TicketList
                        items={resoFiltered}
                        openId={openId}
                        onToggle={toggle}
                        messagesById={messagesById}
                        loadingId={loadingId}
                        sendingId={sendingId}
                        draftById={draftById}
                        setDraftById={setDraftById}
                        sendMessage={sendMessage}
                        fmtDT={fmtDT}
                        fmtTime={fmtTime}
                    />
                </div>
            )}
        </section>
    );
}

/* ── Subcomponentes ────────────────────────────────────────────── */

function SectionHeader({ title, count, accent = false }: { title: string; count: number; accent?: boolean }) {
    return (
        <div className="mb-2 flex items-center gap-2">
            <h2 className="text-sm font-semibold">{title}</h2>
            <span className={["chip", accent ? "chip--success" : ""].join(" ")}>{count}</span>
        </div>
    );
}

function TicketList(props: {
    items: Ticket[];
    openId: number | null;
    onToggle: (id: number) => void;
    messagesById: Record<number, Message[]>;
    loadingId: number | null;
    sendingId: number | null;
    draftById: Record<number, string>;
    setDraftById: React.Dispatch<React.SetStateAction<Record<number, string>>>;
    sendMessage: (ticketId: number) => Promise<void>;
    fmtDT: (iso: string) => string;
    fmtTime: (iso: string) => string;
}) {
    const {
        items, openId, onToggle, messagesById, loadingId, sendingId,
        draftById, setDraftById, sendMessage, fmtDT, fmtTime,
    } = props;

    if (items.length === 0) {
        return (
            <div className="rounded-xl border border-dashed bg-white/70 p-4 text-center text-sm text-slate-600">
                No hay items en esta sección.
            </div>
        );
    }

    return (
        <div className="space-y-3">
            {items.map((t, idx) => {
                const open = openId === t.id;
                const msgs = messagesById[t.id] ?? [];
                const draft = draftById[t.id] ?? "";

                // ⇩ Intercalar colores (rosa/azul) en tickets abiertos; cerrados siguen blancos
                const bubbleColor =
                    t.status === "closed"
                        ? "bubble--user border"
                        : (idx % 2 === 0 ? "bubble--agent" : "bubble--accent");

                const metaTextColor =
                    t.status === "closed" ? "text-slate-600/80" : "text-white/90";

                return (
                    <div key={t.id} className="rounded-2xl border bg-white p-1">
                        {/* Cabezera del acordeón — estilo burbuja */}
                        <button
                            onClick={() => onToggle(t.id)}
                            className="w-full rounded-2xl p-0 text-left"
                        >
                            <div
                                className={[
                                    "bubble bubble--full flex w-full items-center justify-between gap-2",
                                    open ? "ring-2 ring-[var(--brand-600)]/25" : "",
                                    bubbleColor,
                                ].join(" ")}
                            >
                                <div className="px-3 py-2">
                                    <div className="text-sm font-medium">
                                        #{t.id} — {t.reason}
                                    </div>
                                    <div className={["text-xs", metaTextColor].join(" ")}>
                                        {fmtDT(t.createdAt)} · {t._count.messages} mensaje
                                        {t._count.messages === 1 ? "" : "s"}
                                    </div>
                                </div>

                                <span
                                    className={[
                                        "chip mr-3",
                                        t.status === "closed" ? "" : "chip--inverted",
                                    ].join(" ")}
                                >
                                    {t.status}
                                </span>
                            </div>
                        </button>

                        {/* Panel desplegado */}
                        {open && (
                            <div className="border-t">
                                {t.status === "closed" && (
                                    <div className="border-b bg-rose-50 px-4 py-2 text-xs text-rose-700">
                                        Este ticket está <b>cerrado</b>. No se pueden enviar más mensajes.
                                    </div>
                                )}

                                <div className="h-[50vh] overflow-auto bg-slate-50 bg-chat-surface px-3 py-4">
                                    {loadingId === t.id ? (
                                        <MessagesSkeleton />
                                    ) : msgs.length === 0 ? (
                                        <div className="flex h-full items-center justify-center text-sm text-slate-600">
                                            Aún no hay mensajes en este ticket.
                                        </div>
                                    ) : (
                                        <div className="space-y-2">
                                            {msgs.map((m, i) => {
                                                const isAgent = m.author === "agent";

                                                // Agente alterna rosa/azul por índice; usuario queda blanco
                                                const bubbleMsg = isAgent
                                                    ? (i % 2 === 0 ? "bubble bubble--agent" : "bubble bubble--accent")
                                                    : "bubble bubble--user border";

                                                return (
                                                    <div key={m.id} className={"flex " + (isAgent ? "justify-end" : "justify-start")}>
                                                        <div className={["max-w-[80%] rounded-2xl px-3 py-2 shadow-sm", bubbleMsg].join(" ")}>
                                                            <div className="text-[11px] opacity-80">
                                                                {isAgent ? (m.name || "soporte") : "tú"} · {fmtTime(m.createdAt)}
                                                            </div>
                                                            <div className="whitespace-pre-wrap text-sm leading-relaxed">{m.body}</div>
                                                        </div>
                                                    </div>
                                                );
                                            })}
                                        </div>
                                    )}
                                </div>


                                {/* Pie: solo lectura si closed, composer si abierto */}
                                {t.status === "closed" ? (
                                    <div className="border-t bg-white/80 px-4 py-2 text-xs text-slate-500">
                                        Vista de solo lectura. Para una nueva consulta, usa{" "}
                                        <a href="/marketing/contacto" className="underline">Contacto</a>.
                                    </div>
                                ) : (
                                    <form
                                        className="flex items-center gap-2 border-t bg-white/80 px-3 py-2"
                                        onSubmit={(e) => { e.preventDefault(); void sendMessage(t.id); }}
                                    >
                                        <input
                                            className="input flex-1"
                                            placeholder="Escribe un mensaje…"
                                            value={draft}
                                            onChange={(e) => setDraftById(d => ({ ...d, [t.id]: e.target.value }))}
                                            disabled={sendingId === t.id}
                                        />
                                        <button
                                            type="submit"
                                            disabled={sendingId === t.id || !draft.trim()}
                                            className="btn-brand rounded-lg px-4 py-2 text-sm font-medium disabled:opacity-50"
                                        >
                                            {sendingId === t.id ? "Enviando…" : "Enviar"}
                                        </button>
                                    </form>
                                )}
                            </div>
                        )}
                    </div>
                );
            })}
        </div>
    );
}

function MessagesSkeleton() {
    return (
        <div className="space-y-2">
            {[...Array(6)].map((_, i) => (
                <div key={i} className={"flex " + (i % 2 ? "justify-end" : "justify-start")}>
                    <div className="h-12 w-1/2 animate-pulse rounded-2xl bg-slate-200/70" />
                </div>
            ))}
        </div>
    );
}

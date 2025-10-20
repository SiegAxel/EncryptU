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
        <section className="container-default py-8">
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
            {items.map((t) => {
                const open = openId === t.id;
                const msgs = messagesById[t.id] ?? [];
                const draft = draftById[t.id] ?? "";

                return (
                    <div key={t.id} className="rounded-2xl border bg-white">
                        {/* Cabezera del acordeón */}
                        <button
                            onClick={() => onToggle(t.id)}
                            className={[
                                "flex w-full items-center justify-between gap-2 rounded-2xl px-4 py-3 text-left transition",
                                open ? "bg-slate-50" : "hover:bg-slate-50",
                            ].join(" ")}
                        >
                            <div>
                                <div className="text-sm font-medium">
                                    #{t.id} — {t.reason}
                                </div>
                                <div className="text-xs text-slate-500">
                                    {fmtDT(t.createdAt)} · {t._count.messages} mensaje{t._count.messages === 1 ? "" : "s"}
                                </div>
                            </div>
                            <span className={["chip", t.status === "closed" ? "" : "chip--success"].join(" ")}>{t.status}</span>
                        </button>

                        {/* Panel desplegado */}
                        {open && (
                            <div className="border-t">
                                {t.status === "closed" && (
                                    <div className="bg-rose-50 text-rose-700 border-b border-rose-200 px-4 py-2 text-xs">
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
                                            {msgs.map((m) => (
                                                <div key={m.id} className={"flex " + (m.author === "agent" ? "justify-end" : "justify-start")}>
                                                    <div
                                                        className={[
                                                            "max-w-[80%] rounded-2xl px-3 py-2 shadow-sm",
                                                            m.author === "agent" ? "bubble bubble--agent" : "bubble bubble--user border",
                                                        ].join(" ")}
                                                    >
                                                        <div className="text-[11px] opacity-80">
                                                            {m.author === "agent" ? (m.name || "soporte") : "tú"} · {fmtTime(m.createdAt)}
                                                        </div>
                                                        <div className="whitespace-pre-wrap text-sm leading-relaxed">{m.body}</div>
                                                    </div>
                                                </div>
                                            ))}
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

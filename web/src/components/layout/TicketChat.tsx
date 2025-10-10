"use client";
import { useState } from "react";
import Card from "@/components/ui/Card";
import Button from "@/components/ui/Button";
import Input from "@/components/ui/Input";

type Msg = { from: "yo" | "soporte"; text: string };

export default function TicketChat() {
  const [messages, setMessages] = useState<Msg[]>([
    { from: "soporte", text: "Hola, ¿en qué puedo ayudarte?" },
  ]);
  const [text, setText] = useState("");

  const send = () => {
    if (!text.trim()) return;
    setMessages((m) => [...m, { from: "yo", text }]);
    setText("");
  };

  return (
    <div className="grid gap-6 md:grid-cols-[280px,1fr]">
      <Card>
        <div className="space-y-3">
          <div className="font-medium">Conversaciones</div>
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="rounded-lg border p-3 text-sm">
              Ticket #{i} — abierto
            </div>
          ))}
        </div>
      </Card>
      <Card>
        <div className="flex h-[420px] flex-col">
          <div className="mb-3 font-medium">Ticket #46564</div>
          <div className="flex-1 space-y-3 overflow-auto rounded-lg border p-4">
            {messages.map((m, idx) => (
              <div key={idx} className={m.from === "yo" ? "text-right" : "text-left"}>
                <span
                  className={
                    m.from === "yo"
                      ? "inline-block rounded-xl bg-brand px-3 py-2 text-white"
                      : "inline-block rounded-xl bg-slate-100 px-3 py-2"
                  }
                >
                  {m.text}
                </span>
              </div>
            ))}
          </div>
          <div className="mt-3 flex items-center gap-2">
            <Input
              placeholder="Escribe tu mensaje…"
              value={text}
              onChange={(e) => setText(e.target.value)}
            />
            <Button onClick={send}>Enviar</Button>
          </div>
        </div>
      </Card>
    </div>
  );
}

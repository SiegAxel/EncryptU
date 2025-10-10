"use client";
import { useState, type ChangeEvent } from "react";
import Container from "@/components/layout/ui/Container";
import Section from "@/components/layout/ui/Section";
import Card from "@/components/layout/ui/Card";
import Input from "@/components/layout/ui/Input";
import Button from "@/components/layout/ui/Button";

type Form = {
  firstName: string;
  lastName: string;
  email: string;
  reason: string;
  phone: string;
  description: string;
};

type ApiResponse = { ok: boolean; id?: number; error?: string };

export default function ContactPage() {
  const [form, setForm] = useState<Form>({
    firstName: "", lastName: "", email: "", reason: "", phone: "", description: ""
  });
  const [sending, setSending] = useState(false);
  const [msg, setMsg] = useState<string | null>(null);

  // ✅ Handlers tipados (sin any)
  const onInput =
    (k: keyof Form) =>
    (e: ChangeEvent<HTMLInputElement>) =>
      setForm((f) => ({ ...f, [k]: e.target.value }));

  const onTextArea =
    (k: keyof Form) =>
    (e: ChangeEvent<HTMLTextAreaElement>) =>
      setForm((f) => ({ ...f, [k]: e.target.value }));

  const submit = async () => {
    setSending(true);
    setMsg(null);

    const res = await fetch("/api/contact", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(form),
    });

    const data: ApiResponse = await res.json();
    if (res.ok) {
      setMsg(`¡Enviado! ID #${data.id}`);
      setForm({ firstName:"", lastName:"", email:"", reason:"", phone:"", description:"" });
    } else {
      setMsg(data?.error ?? "Revisa los datos");
    }
    setSending(false);
  };

  return (
    <Section>
      <Container>
        <div className="grid gap-6 md:grid-cols-2">
          <Card>
            <h1 className="mb-3 text-xl font-semibold">Contáctanos</h1>
            <div className="space-y-3">
              <Input label="Nombre" value={form.firstName} onChange={onInput("firstName")} />
              <Input label="Apellido" value={form.lastName} onChange={onInput("lastName")} />
              <Input label="Correo electrónico" type="email" value={form.email} onChange={onInput("email")} />
              <Input label="Motivo" placeholder="Soporte / Consulta" value={form.reason} onChange={onInput("reason")} />
              <Input label="Número de teléfono" value={form.phone} onChange={onInput("phone")} />
              <label className="block space-y-1">
                <span className="text-sm text-slate-600">Descripción</span>
                <textarea
                  className="input min-h-[120px]"
                  value={form.description}
                  onChange={onTextArea("description")}
                />
              </label>
              <Button className="w-full" onClick={submit} disabled={sending}>
                {sending ? "Enviando..." : "Enviar formulario"}
              </Button>
              {msg && <p className="text-sm text-slate-600">{msg}</p>}
            </div>
          </Card>
          <div className="rounded-2xl bg-gradient-to-tr from-slate-100 to-slate-50" />
        </div>
      </Container>
    </Section>
  );
}

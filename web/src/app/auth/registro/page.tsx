"use client";
import { useState } from "react";
import Button from "@/components/layout/ui/Button";
import ButtonLink from "@/components/layout/ui/ButtonLink";

export default function RegistroPage() {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [msg, setMsg] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function onSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setMsg(null);
    setLoading(true);

    const res = await fetch("/api/auth", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name, email, password }),
    });

    const data = await res.json();
    if (res.ok) {
      setMsg(`Cuenta creada (id ${data.id}). Ya puedes iniciar sesión.`);
      setName(""); setEmail(""); setPassword("");
    } else {
      setMsg(data?.error ?? "No se pudo crear la cuenta");
    }
    setLoading(false);
  }

  return (
    <section className="max-w-md mx-auto px-4 py-16">
      <h1 className="text-3xl font-bold text-center">Crear cuenta</h1>

      <form onSubmit={onSubmit} className="mt-8 space-y-4">{/* ← ABRE */}
        <input
          className="w-full border p-2 rounded"
          placeholder="Nombre"
          value={name}
          onChange={(e) => setName(e.target.value)}
          required
        />
        <input
          className="w-full border p-2 rounded"
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
        />
        <input
          className="w-full border p-2 rounded"
          type="password"
          placeholder="Contraseña"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          minLength={8}
          required
        />

        <Button type="submit" className="w-full" size="lg" disabled={loading}>
          {loading ? "Creando..." : "Crear cuenta"}
        </Button>
        {msg && <p className="text-sm text-slate-600">{msg}</p>}
      </form> {/* ← CIERRA */}
      
      <div className="mt-4">
        <ButtonLink href="/auth/login" variant="outline" className="w-full text-center" size="lg">
          Ya tengo cuenta
        </ButtonLink>
      </div>
    </section>
  );
}

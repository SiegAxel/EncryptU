"use client";
import { useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import Button from "@/components/layout/ui/Button";
import ButtonLink from "@/components/layout/ui/ButtonLink";

type ApiOk = { ok: true; role: "usuario" | "soporte" | "admin"; redirect: string };
type ApiErr = { ok: false; error: string };

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [msg, setMsg] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const router = useRouter();
  const searchParams = useSearchParams();
  const next = searchParams.get("next"); // viene del middleware si el user intentó entrar a una ruta protegida

  return (
    <section className="max-w-md mx-auto px-4 py-16">
      <h1 className="text-3xl font-bold text-center">Iniciar sesión</h1>

      <form
        onSubmit={async (e) => {
          e.preventDefault();
          setMsg(null);
          setLoading(true);

          const res = await fetch("/api/login", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email, password }),
          });

          const data: ApiOk | ApiErr = await res.json();
          setLoading(false);

          if (res.ok) {
            // si next es exactamente "/dashboard", reemplázalo por el redirect sugerido
            const { redirect } = data as ApiOk;
            const dest = next && next !== "/dashboard" ? next : redirect ?? "/";
            router.replace(dest);
          } else {
            setMsg((data as ApiErr)?.error ?? "No se pudo iniciar sesión");
          }
        }}
        className="mt-8 space-y-4"
      >
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
          required
        />

        <Button type="submit" className="w-full" size="lg" disabled={loading}>
          {loading ? "Ingresando..." : "Ingresar"}
        </Button>

        {msg && <p className="text-sm text-red-600">{msg}</p>}
      </form>

      <div className="mt-4">
        <ButtonLink href="/auth/registro" variant="outline" className="w-full text-center" size="lg">
          Crear cuenta
        </ButtonLink>
      </div>
    </section>
  );
}

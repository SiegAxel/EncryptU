"use client";
import { useState } from "react";
import Button from "@/components/layout/ui/Button";
import ButtonLink from "@/components/layout/ui/ButtonLink";

export default function LoginPage(){
  const [email,setEmail] = useState("");
  const [password,setPassword] = useState("");

  return (
    <section className="max-w-md mx-auto px-4 py-16">
      <h1 className="text-3xl font-bold text-center">Iniciar sesión</h1>

      <form
        onSubmit={(e)=>{ e.preventDefault(); /* submit */ }}
        className="mt-8 space-y-4"
      >
        <input className="w-full border p-2 rounded" placeholder="Email" value={email} onChange={e=>setEmail(e.target.value)} />
        <input className="w-full border p-2 rounded" type="password" placeholder="Contraseña" value={password} onChange={e=>setPassword(e.target.value)} />

        {/* Botón principal: Ingresar */}
        <Button type="submit" className="w-full" size="lg">Ingresar</Button>
      </form>

      {/* Botón secundario: Crear cuenta */}
      <div className="mt-4">
        <ButtonLink href="/auth/registro" variant="outline" className="w-full text-center" size="lg">
          Crear cuenta
        </ButtonLink>
      </div>
    </section>
  );
}


"use client";
import { useState } from "react";

export default function ResetPage(){
  const [email,setEmail] = useState("");

  function onSubmit(e: React.FormEvent){
    e.preventDefault();
    alert(`Restablecer (demo) ${email}`);
  }

  return (
    <section className="max-w-md mx-auto px-4 py-16">
      <h1 className="text-3xl font-bold text-center">Restablecer contraseña</h1>
      <form onSubmit={onSubmit} className="mt-8 space-y-4">
        <input className="w-full border p-2 rounded" placeholder="Email" value={email} onChange={e=>setEmail(e.target.value)} />
        <button className="w-full bg-brand text-white p-2 rounded">Enviar enlace</button>
      </form>
    </section>
  );
}

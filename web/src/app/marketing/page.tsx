
import Link from "next/link";

export default function HomePage() {
  return (
    <section>
      <div className="relative bg-gradient-to-b from-slate-50 to-white">
        <div className="max-w-6xl mx-auto px-4 py-16 text-center">
          <h1 className="text-4xl md:text-5xl font-extrabold tracking-tight">
            Tu gestor de contraseñas <span className="text-brand">seguro</span> y simple
          </h1>
          <p className="mt-4 text-slate-600 max-w-2xl mx-auto">
            Guarda, genera y completa credenciales fuertes. Cifrado local y control total.
          </p>
          <div className="mt-8 flex items-center justify-center gap-3">
            <Link href="/registro" className="px-6 py-3 rounded bg-brand text-white hover:opacity-90">Comenzar gratis</Link>
            <Link href="/acerca" className="px-6 py-3 rounded border hover:border-brand hover:text-brand">Ver más</Link>
          </div>
        </div>
      </div>

      <div className="max-w-6xl mx-auto px-4 py-16 grid md:grid-cols-3 gap-6">
        {[
          { title: "Security", desc: "Cifrado local + buenas prácticas." },
          { title: "Data Protection", desc: "Privacidad y control de tus datos." },
          { title: "Trusted", desc: "Diseñado para equipos y personas." },
        ].map((f, i) => (
          <div key={i} className="rounded-xl border p-6 bg-white shadow-sm">
            <div className="text-3xl">🛡️</div>
            <h3 className="mt-3 font-semibold">{f.title}</h3>
            <p className="text-slate-600 mt-1 text-sm">{f.desc}</p>
          </div>
        ))}
      </div>
    </section>
  );
}

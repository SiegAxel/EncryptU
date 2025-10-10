
export default function SoportePage(){
  const items = Array.from({length:8}).map((_,i)=>({ id:i+1, title:`Ticket #${i+1}`, preview:"Lorem ipsum dolor sit amet..." }));
  return (
    <section className="max-w-6xl mx-auto px-4 py-8 grid md:grid-cols-[280px_1fr] gap-6">
      <aside className="rounded-xl border p-3 h-[70vh] overflow-auto bg-white">
        <h2 className="font-semibold mb-3">Tickets</h2>
        <ul className="space-y-2">
          {items.map(t=>(
            <li key={t.id} className="p-2 rounded hover:bg-slate-50 border">{t.title}</li>
          ))}
        </ul>
      </aside>
      <div className="rounded-xl border p-4 bg-white">
        <div className="h-[60vh] rounded border bg-slate-50 p-4">
          <div className="text-slate-500">Selecciona un ticket para ver el chat.</div>
        </div>
        <div className="mt-3 flex gap-2">
          <input className="flex-1 border p-2 rounded" placeholder="Escribe un mensaje..." />
          <button className="px-4 rounded bg-brand text-white">Enviar</button>
        </div>
      </div>
    </section>
  );
}

"use client";

import { useMemo, useState } from "react";

type Role = "usuario" | "soporte" | "admin";
type User = { id: number; name: string; email: string; role: Role; createdAt: string };

const roles: Role[] = ["usuario", "soporte", "admin"];

export default function AdminUsersPanel({ initialUsers }: { initialUsers: User[] }) {
  const [users, setUsers] = useState<User[]>(initialUsers);
  const [activeRole, setActiveRole] = useState<Role>("usuario");
  const [q, setQ] = useState("");
  const [loadingId, setLoadingId] = useState<number | null>(null);

  const filtered = useMemo(() => {
    const subset = users.filter((u) => u.role === activeRole);
    if (!q.trim()) return subset;
    const needle = q.toLowerCase();
    return subset.filter(
      (u) =>
        u.name.toLowerCase().includes(needle) ||
        u.email.toLowerCase().includes(needle) ||
        String(u.id).includes(needle)
    );
  }, [users, activeRole, q]);

  async function patch(id: number, body: Partial<User> & { password?: string; role?: Role }) {
    setLoadingId(id);
    const res = await fetch(`/api/admin/users/${id}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    const data = await res.json();
    setLoadingId(null);
    if (!res.ok) {
      alert(data?.error ?? "No se pudo actualizar");
      return;
    }
    setUsers((arr) => arr.map((u) => (u.id === id ? { ...u, ...data.user } : u)));
  }

  async function onResetPassword(id: number) {
    const pwd = prompt("Nueva contraseña (mín. 8 caracteres):") ?? "";
    if (pwd.length < 8) return alert("Muy corta.");
    await patch(id, { password: pwd });
  }

  async function onDelete(id: number) {
    if (!confirm("¿Eliminar este usuario?")) return;
    setLoadingId(id);
    const res = await fetch(`/api/admin/users/${id}`, { method: "DELETE" });
    const data = await res.json();
    setLoadingId(null);
    if (!res.ok) return alert(data?.error ?? "No se pudo eliminar");
    setUsers((arr) => arr.filter((u) => u.id !== id));
  }

  return (
    <div className="grid grid-cols-1 gap-6 md:grid-cols-[240px_1fr]">
      {/* SIDEBAR */}
      <aside className="rounded-2xl border bg-white/80 p-4">
        <h3 className="mb-3 text-sm font-semibold">Usuarios</h3>
        <div className="space-y-2">
          {roles.map((r) => (
            <button
              key={r}
              onClick={() => setActiveRole(r)}
              className={[
                "w-full rounded-xl border px-3 py-2 text-left transition",
                activeRole === r
                  ? "border-brand/50 bg-brand/10 text-brand"
                  : "hover:bg-slate-50"
              ].join(" ")}
            >
              {r[0].toUpperCase() + r.slice(1)}
            </button>
          ))}
        </div>

        <div className="mt-6">
          <input
            className="input w-full"
            placeholder="Buscar nombre, email, #id…"
            value={q}
            onChange={(e) => setQ(e.target.value)}
          />
        </div>
      </aside>

      {/* LISTA / TABLA */}
      <div className="rounded-2xl border bg-white">
        <div className="flex items-center justify-between border-b px-4 py-3">
          <div className="text-sm">
            Rol: <span className="font-medium capitalize">{activeRole}</span>
          </div>
          <div className="text-xs text-slate-500">
            {filtered.length} resultado{filtered.length === 1 ? "" : "s"}
          </div>
        </div>

        {filtered.length === 0 ? (
          <div className="p-8 text-center text-sm text-slate-500">No hay usuarios en este rol.</div>
        ) : (
          <ul className="divide-y">
            {filtered.map((u) => (
              <li key={u.id} className="grid grid-cols-1 gap-3 p-4 md:grid-cols-[1fr_1fr_auto] md:items-center">
                {/* columna izquierda: nombre + email + creado */}
                <div>
                  <input
                    className="input mb-2"
                    defaultValue={u.name}
                    onBlur={(e) => {
                      const v = e.currentTarget.value.trim();
                      if (v && v !== u.name) patch(u.id, { name: v });
                    }}
                    disabled={loadingId === u.id}
                  />
                  <input
                    className="input"
                    defaultValue={u.email}
                    onBlur={(e) => {
                      const v = e.currentTarget.value.trim();
                      if (v && v !== u.email) patch(u.id, { email: v });
                    }}
                    disabled={loadingId === u.id}
                  />
                  <p className="mt-1 text-xs text-slate-500">
                    Creado: {new Date(u.createdAt).toLocaleDateString()}
                  </p>
                </div>

                {/* columna centro: rol + acciones rápidas */}
                <div className="flex flex-wrap items-center gap-2">
                  <select
                    className="input w-[160px]"
                    defaultValue={u.role}
                    onChange={(e) => patch(u.id, { role: e.currentTarget.value as Role })}
                    disabled={loadingId === u.id}
                  >
                    <option value="usuario">Usuario</option>
                    <option value="soporte">Soporte</option>
                    <option value="admin">Admin</option>
                  </select>

                  <button
                    className="btn-outline"
                    onClick={() => onResetPassword(u.id)}
                    disabled={loadingId === u.id}
                  >
                    Reset pass
                  </button>
                </div>

                {/* columna derecha: borrar */}
                <div className="flex justify-start md:justify-end">
                  <button
                    className="btn-primary"
                    onClick={() => onDelete(u.id)}
                    disabled={loadingId === u.id}
                  >
                    Eliminar
                  </button>
                </div>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}

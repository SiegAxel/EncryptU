"use client";
import { useMemo, useState } from "react";
import CreateUserModal from "@/components/admin/CreateUserModal";

type Role = "usuario" | "soporte" | "admin";
type User = { id: number; name: string; email: string; role: Role; createdAt?: string };

const roles: Role[] = ["usuario", "soporte", "admin"];

export default function AdminUsersPanel({ initialUsers }: { initialUsers: User[] }) {
  const [users, setUsers] = useState<User[]>(initialUsers);
  const [activeRole, setActiveRole] = useState<Role>("usuario");
  const [q, setQ] = useState("");
  const [loadingId, setLoadingId] = useState<number | null>(null);
  const [showCreateModal, setShowCreateModal] = useState(false);

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
      <aside className="admin-sidebar p-4">
        <h3 className="mb-3 text-sm font-semibold text-slate-700">Usuarios</h3>
        <div className="space-y-2">
          {roles.map((r) => (
            <button
              key={r}
              onClick={() => setActiveRole(r)}
              className={["role-btn", activeRole === r ? "role-btn--active" : ""].join(" ")}
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

        {/* Create User Button */}
        <div className="mt-4">
          <button
            onClick={() => setShowCreateModal(true)}
            className="w-full bg-green-600 text-white px-3 py-2 rounded-md text-sm font-medium hover:bg-green-700 transition-colors"
            title="Crear nuevo usuario"
          >
            + Crear Usuario
          </button>
        </div>
      </aside>

      {/* LISTA / TABLA */}
      <div className="admin-surface">
        <div className="admin-header flex items-center justify-between px-4 py-3 rounded-t-[1.1rem]">
          <div className="text-sm text-slate-800">
            Rol: <span className="font-medium capitalize text-[var(--brand-600)]">{activeRole}</span>
          </div>
          <div className="text-xs text-slate-500">
            {filtered.length} resultado{filtered.length === 1 ? "" : "s"}
          </div>
        </div>

        {filtered.length === 0 ? (
          <div className="p-8 text-center text-sm text-slate-500">
            No hay usuarios en este rol.
          </div>
        ) : (
          <ul className="divide-y divide-slate-200">
            {filtered.map((u) => (
              <li
                key={u.id}
                className="user-row grid grid-cols-1 gap-3 p-4 md:grid-cols-[1fr_1fr_auto] md:items-center"
              >
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
                    Creado: {u.createdAt ? new Date(u.createdAt).toLocaleDateString() : 'N/A'}
                  </p>
                </div>

                {/* columna centro: rol + acciones */}
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
                    className="btn-outline h-9 px-3 text-xs"
                    onClick={() => onResetPassword(u.id)}
                    disabled={loadingId === u.id}
                  >
                    Reset pass
                  </button>
                </div>

                {/* columna derecha: borrar */}
                <div className="flex justify-start md:justify-end">
                  <button
                    className="btn-primary h-9 px-3 text-xs"
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

      {/* Create User Modal */}
      <CreateUserModal
        isOpen={showCreateModal}
        onClose={() => setShowCreateModal(false)}
        onUserCreated={(newUser) => {
          setUsers((list) => [...list, newUser]);
        }}
      />
    </div>
  );
}

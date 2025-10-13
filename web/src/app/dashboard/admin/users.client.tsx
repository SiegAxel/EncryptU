"use client";
import { useState } from "react";
import Button from "@/components/layout/ui/Button";

type Role = "usuario" | "soporte" | "admin";
type User = { id: number; name: string; email: string; role: Role };

export default function AdminUsersTable({ initialUsers }: { initialUsers: User[] }) {
  const [users, setUsers] = useState<User[]>(initialUsers);
  const [loadingId, setLoadingId] = useState<number | null>(null);

  const updateRole = async (id: number, role: Role) => {
    setLoadingId(id);
    const res = await fetch(`/api/admin/users/${id}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ role }),
    });
    const data = await res.json();
    setLoadingId(null);
    if (res.ok) setUsers(arr => arr.map(u => (u.id === id ? { ...u, role } : u)));
    else alert(data?.error ?? "No se pudo actualizar el rol");
  };

  const resetPassword = async (id: number) => {
    const password = prompt("Nueva contraseña (mín. 8 caracteres):") ?? "";
    if (password.length < 8) return alert("Muy corta.");
    setLoadingId(id);
    const res = await fetch(`/api/admin/users/${id}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ password }),
    });
    const data = await res.json();
    setLoadingId(null);
    if (res.ok) alert("Contraseña actualizada");
    else alert(data?.error ?? "No se pudo actualizar la contraseña");
  };

  const removeUser = async (id: number) => {
    if (!confirm("¿Eliminar usuario?")) return;
    setLoadingId(id);
    const res = await fetch(`/api/admin/users/${id}`, { method: "DELETE" });
    const data = await res.json();
    setLoadingId(null);
    if (res.ok) setUsers(arr => arr.filter(u => u.id !== id));
    else alert(data?.error ?? "No se pudo eliminar");
  };

  if (!users.length) {
    return <p className="text-slate-500">No hay usuarios.</p>;
  }

  return (
    <div className="grid gap-4 md:grid-cols-2">
      {users.map(u => (
        <div key={u.id} className="card flex items-center justify-between p-5">
          <div>
            <div className="font-medium">{u.name}</div>
            <div className="text-sm text-slate-500">{u.email}</div>
          </div>
          <div className="flex items-center gap-2">
            <select
              className="input w-[140px]"
              value={u.role}
              onChange={e => updateRole(u.id, e.target.value as Role)}
              disabled={loadingId === u.id}
            >
              <option value="usuario">Usuario</option>
              <option value="soporte">Soporte</option>
              <option value="admin">Admin</option>
            </select>
            <Button variant="outline" onClick={() => resetPassword(u.id)} disabled={loadingId === u.id}>
              Reset pass
            </Button>
            <Button variant="primary" onClick={() => removeUser(u.id)} disabled={loadingId === u.id}>
              Eliminar
            </Button>
          </div>
        </div>
      ))}
    </div>
  );
}

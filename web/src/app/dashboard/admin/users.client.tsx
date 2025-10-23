"use client";
import { useMemo, useState } from "react";

type Role = "usuario" | "soporte" | "admin";
type User = {
  id: number;
  name: string;
  email: string;
  role: Role;
  createdAt?: string;
};

type ApiError = { error?: string };
type ApiOk = { ok: true };

function shallowUserEqual(a: User, b: User) {
  return a.name === b.name && a.email === b.email && a.role === b.role;
}

// ---------- helpers sin any ----------
function getErrorMessage(err: unknown): string {
  if (err instanceof Error) return err.message;
  try {
    return String(err);
  } catch {
    return "Error desconocido";
  }
}

async function safeJson<T>(res: Response): Promise<T | null> {
  try {
    return (await res.json()) as T;
  } catch {
    return null;
  }
}
// -------------------------------------

export default function AdminUsersPanel({ initialUsers }: { initialUsers: User[] }) {
  const [original, setOriginal] = useState<User[]>(initialUsers);
  const [draft, setDraft] = useState<User[]>(initialUsers);
  const [busyIds, setBusyIds] = useState<number[]>([]);
  const [saving, setSaving] = useState(false);

  const dirtyMap = useMemo(() => {
    const map = new Map<number, boolean>();
    for (const u of draft) {
      const o = original.find((x) => x.id === u.id);
      map.set(u.id, !!o && !shallowUserEqual(o, u));
    }
    return map;
  }, [draft, original]);

  const dirtyCount = useMemo(
    () => Array.from(dirtyMap.values()).filter(Boolean).length,
    [dirtyMap]
  );

  const setField = <K extends keyof User>(id: number, key: K, value: User[K]) => {
    setDraft((list) => list.map((u) => (u.id === id ? { ...u, [key]: value } : u)));
  };

  const resetPassword = async (id: number) => {
    const pwd = prompt("Nueva contraseña (mín. 8 caracteres):") ?? "";
    if (pwd.length < 8) {
      alert("Muy corta.");
      return;
    }
    setBusyIds((ids) => [...ids, id]);
    try {
      const res = await fetch(`/api/admin/users/${id}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ password: pwd }),
      });

      if (!res.ok) {
        const data = await safeJson<ApiError>(res);
        throw new Error(data?.error ?? "No se pudo actualizar la contraseña");
      }
      alert("Contraseña actualizada");
    } catch (e: unknown) {
      alert(getErrorMessage(e));
    } finally {
      setBusyIds((ids) => ids.filter((x) => x !== id));
    }
  };

  const removeUser = async (id: number) => {
    if (!confirm("¿Eliminar usuario?")) return;
    setBusyIds((ids) => [...ids, id]);
    try {
      const res = await fetch(`/api/admin/users/${id}`, { method: "DELETE" });
      if (!res.ok) {
        const data = await safeJson<ApiError>(res);
        throw new Error(data?.error ?? "No se pudo eliminar");
      }
      setOriginal((list) => list.filter((u) => u.id !== id));
      setDraft((list) => list.filter((u) => u.id !== id));
    } catch (e: unknown) {
      alert(getErrorMessage(e));
    } finally {
      setBusyIds((ids) => ids.filter((x) => x !== id));
    }
  };

  const saveAll = async () => {
    if (dirtyCount === 0) return;
    setSaving(true);
    try {
      const changes = draft.filter((u) => {
        const o = original.find((x) => x.id === u.id);
        return o && !shallowUserEqual(o, u);
      });

      await Promise.all(
        changes.map(async (u) => {
          const res = await fetch(`/api/admin/users/${u.id}`, {
            method: "PATCH",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ name: u.name, email: u.email, role: u.role }),
          });
          if (!res.ok) {
            const data = await safeJson<ApiError>(res);
            throw new Error(data?.error ?? "No se pudo actualizar");
          }
        })
      );

      setOriginal(draft);
    } catch (e: unknown) {
      alert(getErrorMessage(e) || "Error al actualizar");
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="flex flex-col gap-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">Usuarios</h2>
        <button
          onClick={saveAll}
          disabled={dirtyCount === 0 || saving}
          className={[
            "rounded-md px-4 py-2 text-sm font-medium transition",
            dirtyCount > 0 && !saving
              ? "bg-amber-500 text-white hover:bg-amber-600"
              : "bg-slate-300 text-slate-600 cursor-not-allowed",
          ].join(" ")}
          title={dirtyCount > 0 ? "Guardar cambios" : "Sin cambios"}
        >
          {saving ? "Guardando…" : `Actualizar${dirtyCount ? ` (${dirtyCount})` : ""}`}
        </button>
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        {draft.map((u) => {
          const isBusy = busyIds.includes(u.id);
          const isDirty = dirtyMap.get(u.id);

          return (
            <div
              key={u.id}
              className={[
                "card p-5 flex flex-col gap-3 border",
                isDirty ? "ring-1 ring-amber-300 border-amber-200" : "",
              ].join(" ")}
            >
              <div className="flex items-center gap-3">
                <input
                  className="input flex-1"
                  value={u.name}
                  onChange={(e) => setField(u.id, "name", e.target.value)}
                  placeholder="Nombre"
                />
                <select
                  className="input w-[140px]"
                  value={u.role}
                  onChange={(e) => setField(u.id, "role", e.target.value as Role)}
                >
                  <option value="usuario">Usuario</option>
                  <option value="soporte">Soporte</option>
                  <option value="admin">Admin</option>
                </select>
              </div>

              <div className="flex items-center gap-3">
                <input
                  className="input flex-1"
                  value={u.email}
                  onChange={(e) => setField(u.id, "email", e.target.value)}
                  placeholder="Correo"
                />
                <button
                  type="button"
                  onClick={() => resetPassword(u.id)}
                  disabled={isBusy}
                  className="btn-outline text-xs"
                >
                  Reset pass
                </button>
                <button
                  type="button"
                  onClick={() => removeUser(u.id)}
                  disabled={isBusy}
                  className="btn-primary text-xs"
                >
                  Eliminar
                </button>
              </div>

              {u.createdAt && (
                <div className="text-xs text-slate-500">
                  Creado: {new Date(u.createdAt).toLocaleString()}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}

import { NextResponse, type NextRequest } from "next/server";
import { cookies } from "next/headers";
import { prisma } from "@/lib/prisma";
import { verifyToken, type TokenPayload } from "@/lib/auth";
import type { User } from "@prisma/client";

export const runtime = "nodejs";

async function requireAdmin(): Promise<TokenPayload | null> {
  const token = (await cookies()).get("auth")?.value;
  if (!token) return null;
  try {
    const u = await verifyToken<TokenPayload>(token);
    return u.role === "admin" ? u : null;
  } catch {
    return null;
  }
}

type Role = "usuario" | "soporte" | "admin";
type PatchBody = { role?: Role; password?: string };

// PATCH /api/admin/users/[userID]
export async function PATCH(
  req: NextRequest,
  context: { params: Promise<{ userID: string }> } // 👈 params es Promise
) {
  const me = await requireAdmin();
  if (!me) return NextResponse.json({ ok: false, error: "Forbidden" }, { status: 403 });

  const { userID } = await context.params;         // 👈 await aquí
  const id = Number(userID);
  if (!Number.isFinite(id)) {
    return NextResponse.json({ ok: false, error: "ID inválido" }, { status: 400 });
  }

  const body = (await req.json()) as PatchBody;

  const data: Partial<Pick<User, "role" | "passwordHash">> = {};
  if (body.role) {
    if (!["usuario", "soporte", "admin"].includes(body.role))
      return NextResponse.json({ ok: false, error: "Rol inválido" }, { status: 400 });
    data.role = body.role;
  }
  if (typeof body.password === "string") {
    if (body.password.length < 8)
      return NextResponse.json({ ok: false, error: "Contraseña muy corta" }, { status: 400 });
    data.passwordHash = body.password; // (según tu decisión actual)
  }

  const user = await prisma.user.update({
    where: { id },
    data,
    select: { id: true, name: true, email: true, role: true },
  });

  return NextResponse.json({ ok: true, user });
}

// DELETE /api/admin/users/[userID]
export async function DELETE(
  _req: NextRequest,
  context: { params: Promise<{ userID: string }> } // 👈 Promise aquí también
) {
  const me = await requireAdmin();
  if (!me) return NextResponse.json({ ok: false, error: "Forbidden" }, { status: 403 });

  const { userID } = await context.params;         // 👈 await aquí
  const id = Number(userID);
  if (!Number.isFinite(id)) {
    return NextResponse.json({ ok: false, error: "ID inválido" }, { status: 400 });
  }

  await prisma.user.delete({ where: { id } });
  return NextResponse.json({ ok: true });
}

import { NextResponse, type NextRequest } from "next/server";
import { prisma } from "@/lib/prisma";
import { requireAdmin } from "@/app/api/admin/requireAdmin";

export const runtime = "nodejs";

type Role = "usuario" | "soporte" | "admin";

type PatchBody = {
  role?: Role;
  password?: string;
  name?: string;
  email?: string;
};

// PATCH /api/admin/users/[userID]
export async function PATCH(
  _req: NextRequest,
  ctx: { params: Promise<{ userID: string }> }
) {
  const me = await requireAdmin();
  if (!me) return NextResponse.json({ ok: false, error: "Forbidden" }, { status: 403 });

  const { userID } = await ctx.params; // 👈 en Next 15 debes await params
  const id = Number(userID);

  const body = (await _req.json()) as PatchBody;
  const data: Record<string, unknown> = {};

  if (body.role) {
    if (!["usuario", "soporte", "admin"].includes(body.role)) {
      return NextResponse.json({ ok: false, error: "Rol inválido" }, { status: 400 });
    }
    data.role = body.role;
  }

  if (typeof body.password === "string") {
    if (body.password.length < 8) {
      return NextResponse.json({ ok: false, error: "Contraseña muy corta" }, { status: 400 });
    }
    // ⚠️ Tú decidiste no re-hashear aquí porque llega protegida desde fuera
    data.passwordHash = body.password;
  }

  if (typeof body.name === "string" && body.name.trim().length >= 2) {
    data.name = body.name.trim();
  }

  if (typeof body.email === "string") {
    const emailRe = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/i;
    if (!emailRe.test(body.email)) {
      return NextResponse.json({ ok: false, error: "Email inválido" }, { status: 400 });
    }
    data.email = body.email.toLowerCase();
  }

  const user = await prisma.user.update({
    where: { id },
    data,
    select: { id: true, name: true, email: true, role: true, createdAt: true },
  });

  return NextResponse.json({ ok: true, user });
}

// DELETE /api/admin/users/[userID]
export async function DELETE(
  _req: NextRequest,
  ctx: { params: Promise<{ userID: string }> }
) {
  const me = await requireAdmin();
  if (!me) return NextResponse.json({ ok: false, error: "Forbidden" }, { status: 403 });

  const { userID } = await ctx.params; // 👈 await params
  const id = Number(userID);

  await prisma.user.delete({ where: { id } });
  return NextResponse.json({ ok: true });
}

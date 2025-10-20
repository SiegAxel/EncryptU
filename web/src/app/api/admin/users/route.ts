import { NextResponse } from "next/server";
import { cookies } from "next/headers";
import { prisma } from "@/lib/prisma";
import { verifyToken, type TokenPayload } from "@/lib/auth";

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

export async function GET() {
  const me = await requireAdmin();
  if (!me) return NextResponse.json({ ok: false, error: "Forbidden" }, { status: 403 });

  const users = await prisma.user.findMany({
    orderBy: { createdAt: "asc" },
    select: { id: true, name: true, email: true, role: true, createdAt: true },
  });

  return NextResponse.json({ ok: true, users });
}

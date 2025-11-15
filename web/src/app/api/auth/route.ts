import { NextResponse } from "next/server";
import { prisma } from "@/lib/prisma";
import { PrismaClientKnownRequestError } from "@prisma/client/runtime/library";
import { hashPassword } from "@/lib/password";

export const runtime = "nodejs";

type Body = { name?: string; email?: string; password?: string };
type ApiResponse = { ok: true; id: number } | { ok: false; error: string };

export async function POST(req: Request): Promise<NextResponse<ApiResponse>> {
  try {
    const { name = "", email = "", password = "" } = (await req.json()) as Body;

    const emailRe = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/i;
    if (!name.trim() || !emailRe.test(email) || password.length < 8) {
      return NextResponse.json(
        { ok: false, error: "Datos inválidos (nombre, email o contraseña)." },
        { status: 400 }
      );
    }

    const normalizedEmail = email.toLowerCase();

    const existing = await prisma.user.findUnique({
      where: { email: normalizedEmail },
    });
    if (existing) {
      return NextResponse.json(
        { ok: false, error: "El correo ya está registrado." },
        { status: 409 }
      );
    }

    // Hash the password using Argon2 before storing
    const hashedPassword = await hashPassword(password);
    
    const user = await prisma.user.create({
      data: { name: name.trim(), email: normalizedEmail, passwordHash: hashedPassword },
      select: { id: true },
    });

    return NextResponse.json({ ok: true, id: user.id }, { status: 201 });
  } catch (err: unknown) {
    const message =
      err instanceof PrismaClientKnownRequestError && err.code === "P2002"
        ? "El correo ya está registrado."
        : err instanceof Error
        ? err.message
        : String(err);

    return NextResponse.json({ ok: false, error: message }, { status: 500 });
  }
}

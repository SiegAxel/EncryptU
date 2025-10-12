import { NextResponse } from "next/server";
import { prisma } from "@/lib/prisma";
import { hashPassword } from "@/lib/auth";
import { Prisma } from "@prisma/client"; // 👈 importa tipos de Prisma

export const runtime = "nodejs";

type Body = {
  name?: string;
  email?: string;
  password?: string;
};

type ApiResponse =
  | { ok: true; id: number }
  | { ok: false; error: string };

export async function POST(req: Request): Promise<NextResponse<ApiResponse>> {
  try {
    const { name = "", email = "", password = "" } = (await req.json()) as Body;

    // Validación mínima
    const emailRe = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/i;
    if (!name.trim() || !emailRe.test(email) || password.length < 8) {
      return NextResponse.json(
        { ok: false, error: "Datos inválidos (nombre, email o contraseña)." },
        { status: 400 }
      );
    }

    // Evita duplicados (email único)
    const existing = await prisma.user.findUnique({ where: { email: email.toLowerCase() } });
    if (existing) {
      return NextResponse.json(
        { ok: false, error: "El correo ya está registrado." },
        { status: 409 }
      );
    }

    const passwordHash = await hashPassword(password);

    const user = await prisma.user.create({
      data: { name: name.trim(), email: email.toLowerCase(), passwordHash },
      select: { id: true },
    });

    return NextResponse.json({ ok: true, id: user.id }, { status: 201 });
  } catch (err: unknown) {
    // 🎯 Sin 'any': usa el tipo de error de Prisma o cae a mensaje genérico
    let message: string;
    if (err instanceof Prisma.PrismaClientKnownRequestError) {
      if (err.code === "P2002") {
        message = "El correo ya está registrado.";
      } else {
        message = `${err.code}: ${err.message}`;
      }
    } else {
      message = err instanceof Error ? err.message : String(err);
    }
    return NextResponse.json({ ok: false, error: message }, { status: 500 });
  }
}

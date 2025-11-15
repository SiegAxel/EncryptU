import { NextResponse } from "next/server";
import { prisma } from "@/lib/prisma";
import { requireAdmin } from "@/app/api/admin/requireAdmin";
import { hashPassword } from "@/lib/password";

export const runtime = "nodejs";

type Role = "usuario" | "soporte" | "admin";

type CreateUserBody = {
  name: string;
  email: string;
  password: string;
  role: Role;
};

type ApiResponse = 
  | { ok: true; user: { id: number; name: string; email: string; role: Role } }
  | { ok: false; error: string };

// POST /api/admin/users - Create new user
export async function POST(req: Request): Promise<NextResponse<ApiResponse>> {
  try {
    const me = await requireAdmin();
    if (!me) {
      return NextResponse.json(
        { ok: false, error: "Forbidden" },
        { status: 403 }
      );
    }

    const { name, email, password, role } = (await req.json()) as CreateUserBody;

    // Validation
    if (!name?.trim() || !email?.trim() || !password || !role) {
      return NextResponse.json(
        { ok: false, error: "Todos los campos son requeridos" },
        { status: 400 }
      );
    }

    const emailRe = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/i;
    if (!emailRe.test(email)) {
      return NextResponse.json(
        { ok: false, error: "Email inválido" },
        { status: 400 }
      );
    }

    if (password.length < 8) {
      return NextResponse.json(
        { ok: false, error: "La contraseña debe tener al menos 8 caracteres" },
        { status: 400 }
      );
    }

    if (!["usuario", "soporte", "admin"].includes(role)) {
      return NextResponse.json(
        { ok: false, error: "Rol inválido" },
        { status: 400 }
      );
    }

    // Check if user already exists
    const existingUser = await prisma.user.findUnique({
      where: { email: email.toLowerCase() },
    });

    if (existingUser) {
      return NextResponse.json(
        { ok: false, error: "El email ya está registrado" },
        { status: 409 }
      );
    }

    // Hash password with Argon2
    const hashedPassword = await hashPassword(password);

    // Create user
    const user = await prisma.user.create({
      data: {
        name: name.trim(),
        email: email.toLowerCase(),
        passwordHash: hashedPassword,
        role: role,
      },
      select: { id: true, name: true, email: true, role: true },
    });

    return NextResponse.json({ ok: true, user }, { status: 201 });
  } catch (err) {
    console.error("Admin user creation error:", err);
    const message = err instanceof Error ? err.message : "Error interno del servidor";
    
    return NextResponse.json(
      { ok: false, error: message },
      { status: 500 }
    );
  }
}
import { NextResponse } from "next/server";
import { prisma } from "@/lib/prisma";
import { signToken } from "@/lib/auth";
import { verifyPassword } from "@/lib/password";

export const runtime = "nodejs";

type Body = { email?: string; password?: string };
type Role = "usuario" | "soporte" | "admin";
type ApiResponse =
  | { ok: true; role: Role; redirect: string }
  | { ok: false; error: string };

export async function POST(req: Request): Promise<NextResponse<ApiResponse>> {
  try {
    const { email = "", password = "" } = (await req.json()) as Body;

    if (!email || !password) {
      return NextResponse.json<ApiResponse>(
        { ok: false, error: "Email y contraseña son requeridos." },
        { status: 400 }
      );
    }

    const user = await prisma.user.findUnique({
      where: { email: email.toLowerCase() },
      select: { id: true, name: true, email: true, passwordHash: true, role: true },
    });

    // Verify password using Argon2
    if (!user || !(await verifyPassword(user.passwordHash, password))) {
      return NextResponse.json<ApiResponse>(
        { ok: false, error: "Credenciales inválidas." },
        { status: 401 }
      );
    }

    const token = await signToken({
      sub: String(user.id),
      role: user.role as Role,
      name: user.name,
      email: user.email,
    });

    const redirectMap: Record<Role, string> = {
      usuario: "/",
      soporte: "/dashboard/soporte",
      admin: "/dashboard/admin",
    };

    const res = NextResponse.json<ApiResponse & { access_token?: string }>({
      ok: true,
      role: user.role as Role,
      redirect: redirectMap[user.role as Role] ?? "/",
      access_token: token, // Return token for desktop app compatibility
    });

    res.cookies.set("auth", token, {
      httpOnly: true,
      secure: process.env.NODE_ENV === "production",
      sameSite: "lax",
      path: "/",
      maxAge: 60 * 60 * 24 * 7,
    });

    return res;
  } catch (err: unknown) {
    const message = err instanceof Error ? err.message : String(err);
    return NextResponse.json<ApiResponse>({ ok: false, error: message }, { status: 500 });
  }
}

export async function GET() {
  return NextResponse.json({ ok: true, ping: "login" });
}

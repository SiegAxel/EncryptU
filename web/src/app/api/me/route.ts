import { NextResponse } from "next/server";
import { cookies } from "next/headers";
import { verifyToken, type TokenPayload } from "@/lib/auth";

export async function GET() {
  // 👇 primero espera el store de cookies
  const cookieStore = await cookies();
  const token = cookieStore.get("auth")?.value;

  if (!token) {
    return NextResponse.json({ ok: false }, { status: 401 });
  }

  try {
    const user = await verifyToken<TokenPayload>(token);
    return NextResponse.json({ ok: true, user });
  } catch {
    return NextResponse.json({ ok: false }, { status: 401 });
  }
}

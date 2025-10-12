// src/app/api/auth/register/route.ts
import { NextResponse } from "next/server";
import { prisma } from "@/lib/prisma";
import { hashPassword } from "@/lib/auth";

export async function POST(req: Request) {
  const { name = "", email = "", password = "" } = await req.json();

  // ¿existe?
  const existing = await prisma.user.findUnique({ where: { email } }); // <- prisma.user ✅

  if (existing) {
    return NextResponse.json({ ok: false, error: "El correo ya está registrado." }, { status: 409 });
  }

  const user = await prisma.user.create({
    data: { name, email: email.toLowerCase(), passwordHash: await hashPassword(password) },
    select: { id: true },
  });

  return NextResponse.json({ ok: true, id: user.id }, { status: 201 });
}

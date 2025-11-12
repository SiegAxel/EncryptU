import { NextResponse } from "next/server";
import { cookies } from "next/headers";
import { verifyToken, type TokenPayload } from "@/lib/auth";
import { prisma } from "@/lib/prisma";
import crypto from "crypto";


export const runtime = "nodejs";

// GET /api/userTicket?ticketId=123  -> mensajes
export async function GET(req: Request) {
  const token = (await cookies()).get("auth")?.value;
  if (!token) return NextResponse.json({ ok: false, error: "No autenticado" }, { status: 401 });

  const u = await verifyToken<TokenPayload>(token).catch(() => null);
  if (!u || u.role !== "usuario")
    return NextResponse.json({ ok: false, error: "No autorizado" }, { status: 403 });

  const { searchParams } = new URL(req.url);
  const ticketId = Number(searchParams.get("ticketId"));
  if (!ticketId) return NextResponse.json({ ok: false, error: "Falta ticketId" }, { status: 400 });

  const ticket = await prisma.contactTicket.findFirst({
    where: { id: ticketId, email: u.email },
    select: { id: true },
  });
  if (!ticket) return NextResponse.json({ ok: false, error: "Ticket no encontrado" }, { status: 404 });

  const messages = await prisma.ticketMessage.findMany({
    where: { ticketId },
    orderBy: { createdAt: "asc" },
    select: { id: true, author: true, name: true, body: true, createdAt: true },
  });

  // 👇 NUEVO: ETag + no-cache (para polling eficiente)
  const etag = '"' + crypto.createHash("sha1")
    .update(JSON.stringify(messages.map(m => m.id)))
    .digest("hex") + '"';

  const ifNoneMatch = req.headers.get("if-none-match");
  const headers = { "Cache-Control": "no-cache", "ETag": etag };

  if (ifNoneMatch === etag) {
    return new NextResponse(null, { status: 304, headers });
  }

  return NextResponse.json({ ok: true, messages }, { headers });
}
// POST /api/userTicket   body: { ticketId:number, body:string }
export async function POST(req: Request) {
  const token = (await cookies()).get("auth")?.value;
  if (!token) return NextResponse.json({ ok: false, error: "No autenticado" }, { status: 401 });

  const u = await verifyToken<TokenPayload>(token).catch(() => null);
  if (!u || u.role !== "usuario")
    return NextResponse.json({ ok: false, error: "No autorizado" }, { status: 403 });

  const { ticketId, body } = (await req.json()) as { ticketId?: number; body?: string };
  if (!ticketId) return NextResponse.json({ ok: false, error: "Falta ticketId" }, { status: 400 });
  if (!body || !body.trim()) return NextResponse.json({ ok: false, error: "Mensaje vacío" }, { status: 400 });

  const ticket = await prisma.contactTicket.findFirst({
    where: { id: ticketId, email: u.email },
    select: { id: true, status: true },
  });
  if (!ticket) return NextResponse.json({ ok: false, error: "Ticket no encontrado" }, { status: 404 });
  if (ticket.status === "closed")
    return NextResponse.json({ ok: false, error: "El ticket está cerrado" }, { status: 400 });

  // anti-spam: 20s desde el último mensaje del usuario en este ticket
  const last = await prisma.ticketMessage.findFirst({
    where: { ticketId, author: "user" },
    orderBy: { createdAt: "desc" },
    select: { createdAt: true },
  });
  if (last) {
    const diff = Date.now() - last.createdAt.getTime();
    if (diff < 20_000) {
      return NextResponse.json({ ok: false, error: "Espera unos segundos antes de enviar otro mensaje" }, { status: 429 });
    }
  }

  const msg = await prisma.ticketMessage.create({
    data: {
      ticketId,
      author: "user",
      name: u.name,
      email: u.email,
      body: body.trim(),
    },
    select: { id: true, author: true, name: true, body: true, createdAt: true },
  });

  return NextResponse.json({ ok: true, message: msg });
}

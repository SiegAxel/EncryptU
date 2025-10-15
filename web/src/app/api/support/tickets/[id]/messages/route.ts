import { NextResponse } from "next/server";
import { prisma } from "@/lib/prisma";
import { requireAgent } from "../../../requireAgent";
import nodemailer from "nodemailer";

export const runtime = "nodejs";

type RouteParams = { id: string };

export async function GET(
  _req: Request,
  ctx: { params: Promise<RouteParams> }   // 👈 params es Promise
) {
  const me = await requireAgent();
  if (!me) return NextResponse.json({ ok: false, error: "Forbidden" }, { status: 403 });

  const { id } = await ctx.params;         // 👈 await
  const ticketId = Number(id);

  const msgs = await prisma.ticketMessage.findMany({
    where: { ticketId },
    orderBy: { createdAt: "asc" },
    select: { id: true, author: true, name: true, body: true, createdAt: true },
  });

  return NextResponse.json({ ok: true, messages: msgs });
}

export async function POST(
  req: Request,
  ctx: { params: Promise<RouteParams> }     // 👈 igual aquí
) {
  const me = await requireAgent();
  if (!me) return NextResponse.json({ ok: false, error: "Forbidden" }, { status: 403 });

  const { id } = await ctx.params;          // 👈 await
  const ticketId = Number(id);

  const { body = "" } = (await req.json()) as { body?: string };
  if (!body.trim()) {
    return NextResponse.json({ ok: false, error: "Mensaje vacío" }, { status: 400 });
  }

  const ticket = await prisma.contactTicket.findUnique({
    where: { id: ticketId },
    select: { id: true, email: true, firstName: true, lastName: true },
  });
  if (!ticket) return NextResponse.json({ ok: false, error: "Ticket no existe" }, { status: 404 });

  const msg = await prisma.ticketMessage.create({
    data: {
      ticketId,
      author: "agent",
      name: me.name,
      email: me.email,
      body,
    },
    select: { id: true, body: true, createdAt: true },
  });

  const port = Number(process.env.SMTP_PORT || 465);
  const transporter = nodemailer.createTransport({
    host: process.env.SMTP_HOST!,
    port,
    secure: port === 465,
    auth: { user: process.env.SMTP_USER!, pass: process.env.SMTP_PASS! },
  });

  await transporter.sendMail({
    from: process.env.SMTP_FROM || process.env.SMTP_USER!,
    to: ticket.email,
    subject: `Respuesta a tu ticket #${ticket.id}`,
    text: `Hola ${ticket.firstName},

Hemos respondido tu ticket #${ticket.id}:

${body}

— Equipo de soporte`,
    html: `
      <p>Hola ${ticket.firstName},</p>
      <p>Hemos respondido tu ticket <strong>#${ticket.id}</strong>:</p>
      <blockquote style="border-left:4px solid #ddd;padding-left:8px;color:#333">
        ${escapeHtml(body).replace(/\n/g,"<br/>")}
      </blockquote>
      <p>— Equipo de soporte</p>
    `,
  });

  return NextResponse.json({ ok: true, message: msg });
}

function escapeHtml(s: string) {
  return s.replace(/[&<>"']/g, (c) => ({ "&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;" }[c] as string));
}

import { NextResponse } from "next/server";
import { prisma } from "@/lib/prisma";
import { requireAgent } from "../../../requireAgent";
import nodemailer from "nodemailer";

export const runtime = "nodejs";

type RouteParams = { id: string };

export async function POST(
  _req: Request,
  ctx: { params: Promise<RouteParams> }   // 👈 params es Promise
) {
  const me = await requireAgent();
  if (!me) return NextResponse.json({ ok: false, error: "Forbidden" }, { status: 403 });

  const { id } = await ctx.params;        // 👈 await aquí
  const ticketId = Number(id);

  const ticket = await prisma.contactTicket.findUnique({
    where: { id: ticketId },
    select: { id: true, email: true, firstName: true, lastName: true, status: true },
  });
  if (!ticket) return NextResponse.json({ ok: false, error: "Ticket no encontrado" }, { status: 404 });
  if (ticket.status === "closed") {
    return NextResponse.json({ ok: false, error: "El ticket ya está cerrado" }, { status: 400 });
  }

  await prisma.contactTicket.update({ where: { id: ticketId }, data: { status: "closed" } });

  const port = Number(process.env.SMTP_PORT || 465);
  const transporter = nodemailer.createTransport({
    host: process.env.SMTP_HOST!,
    port,
    secure: port === 465,
    auth: { user: process.env.SMTP_USER!, pass: process.env.SMTP_PASS! },
  });

  const from = process.env.SMTP_FROM || process.env.SMTP_USER!;
  const asunto = `Ticket #${ticket.id} cerrado - Gracias por contactarte con EncryptU`;
  const html = `
    <p>Hola ${ticket.firstName},</p>
    <p>Tu ticket <strong>#${ticket.id}</strong> ha sido cerrado.</p>
    <p>Gracias por contactarte con <strong>EncryptU</strong>. ¡Esperamos que hayas quedado satisfecho con nuestra solución!</p>
    <p>Ante cualquier duda, no dudes en contactarnos nuevamente.</p>
    <p>— Equipo de soporte EncryptU</p>
  `;

  await transporter.sendMail({
    from: `"EncryptU Soporte" <${from}>`,
    to: ticket.email,
    subject: asunto,
    html,
  });

  return NextResponse.json({ ok: true, message: "Ticket cerrado y correo enviado" });
}

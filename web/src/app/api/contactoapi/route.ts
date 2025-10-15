import { NextResponse } from "next/server";
import nodemailer, { type Transporter } from "nodemailer";
import { prisma } from "@/lib/prisma";

export const runtime = "nodejs"; // Nodemailer requiere Node.js (no Edge)

type Body = {
  firstName?: string;
  lastName?: string;
  email?: string;
  reason?: string;
  phone?: string;
  description?: string;
};

type ApiResponse =
  | { ok: true; id: number }
  | { ok: false; error: string };

export async function POST(req: Request): Promise<NextResponse<ApiResponse>> {
  try {
    const { firstName, lastName, email, reason, phone, description } = (await req.json()) as Body;

    // Validación mínima (existencia de campos)
    if (!firstName || !lastName || !email || !reason || !phone || !description) {
      return NextResponse.json({ ok: false, error: "Faltan campos" }, { status: 400 });
    }

    // 1) Guardar en BD (Neon)
    const ticket = await prisma.contactTicket.create({
      data: { firstName, lastName, email, reason, phone, description },
    });

    // 2) Enviar correo (Gmail SSL 465)
    const port = Number(process.env.SMTP_PORT || 465);
    const transporter: Transporter = nodemailer.createTransport({
      host: process.env.SMTP_HOST!,
      port,
      secure: port === 465, // 465=SSL, 587=STARTTLS
      auth: {
        user: process.env.SMTP_USER!,
        pass: process.env.SMTP_PASS!, // App Password SIN espacios
      },
    });

    const from = process.env.SMTP_FROM || process.env.SMTP_USER!;
    const to = process.env.CONTACT_RECIPIENT || "liam251215@gmail.com";
    const subject = `Ticket generado por ${firstName} ${lastName}`;

    const text = `
Nuevo ticket #${ticket.id}

Nombre: ${firstName} ${lastName}
Correo: ${email}
Motivo: ${reason}
Teléfono: ${phone}

Descripción:
${description}

Creado: ${ticket.createdAt.toISOString()}
`.trim();

    const html = `
      <h2>Nuevo ticket #${ticket.id}</h2>
      <table style="border-collapse:collapse">
        <tr><td><strong>Nombre:</strong></td><td>${escapeHtml(firstName)} ${escapeHtml(lastName)}</td></tr>
        <tr><td><strong>Correo:</strong></td><td>${escapeHtml(email)}</td></tr>
        <tr><td><strong>Motivo:</strong></td><td>${escapeHtml(reason)}</td></tr>
        <tr><td><strong>Teléfono:</strong></td><td>${escapeHtml(phone)}</td></tr>
      </table>
      <p><strong>Descripción:</strong></p>
      <p>${escapeHtml(description).replace(/\n/g, "<br/>")}</p>
      <p><small>Creado: ${ticket.createdAt.toISOString()}</small></p>
    `;

    await transporter.sendMail({ from, to, subject, text, html });

    return NextResponse.json({ ok: true, id: ticket.id });
  } catch (err: unknown) {
    // sin `any`: estrechamos el tipo
    const message = err instanceof Error ? err.message : String(err);
    console.error(err);
    return NextResponse.json({ ok: false, error: message }, { status: 500 });
  }
}

// (opcional) GET de prueba para verificar que la ruta existe
export async function GET() {
  return NextResponse.json({ ok: true, ping: "contactoapi" });
}

function escapeHtml(s: string) {
  return s.replace(/[&<>"']/g, (c) =>
    ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c as "&" | "<" | ">" | '"' | "'"])
  );
}

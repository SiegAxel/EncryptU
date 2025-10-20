// src/app/api/contactoapi/route.ts
import { NextResponse } from "next/server";
import nodemailer from "nodemailer";
import { prisma } from "@/lib/prisma";

export const runtime = "nodejs";

type Incoming = {
  firstName?: string;
  lastName?: string;
  email?: string;
  reason?: string;      // "soporte" | "consulta"
  phone?: string;       // 9 dígitos CL
  description?: string; // texto
  apellido?: string;
  motivo?: string;
  telefono?: string;
  descripcion?: string;
};

type Normalized = {
  firstName?: string;
  lastName?: string;
  email: string;
  reason?: string;
  phone?: string;
  description: string;
};

// ──────────────────────────────── utilidades ────────────────────────────────
function requireEnv(name: string) {
  const v = process.env[name];
  if (!v) throw new Error(`Falta variable de entorno ${name}`);
  return v;
}

function toErrorMessage(err: unknown): string {
  if (err instanceof Error) return err.message;
  if (typeof err === "string") return err;
  try { return JSON.stringify(err); } catch { return "Error del servidor"; }
}

function normalize(input: Incoming): Normalized {
  return {
    firstName: input.firstName,
    lastName: input.lastName ?? input.apellido,
    email: input.email ?? "",
    reason: input.reason ?? input.motivo,
    phone: (input.phone ?? input.telefono)?.replace(/\D/g, ""),
    description: input.description ?? input.descripcion ?? "",
  };
}

// ──────────────────────────────── handler ────────────────────────────────
export async function POST(req: Request) {
  try {
    const raw = (await req.json()) as Incoming;
    const body = normalize(raw);

    // Validaciones mínimas
    const emailRe = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/i;
    if (!emailRe.test(body.email)) {
      return NextResponse.json({ ok: false, error: "Correo inválido" }, { status: 400 });
    }
    if (!body.description.trim()) {
      return NextResponse.json({ ok: false, error: "La descripción es obligatoria" }, { status: 400 });
    }
    if (body.phone && !/^\d{9}$/.test(body.phone)) {
      return NextResponse.json({ ok: false, error: "El teléfono debe tener 9 dígitos" }, { status: 400 });
    }
    if (body.reason && !["soporte", "consulta"].includes(body.reason)) {
      return NextResponse.json({ ok: false, error: "Motivo no válido" }, { status: 400 });
    }

    // ── Crear Ticket + Mensaje ──
    const ticket = await prisma.$transaction(async (tx) => {
      const t = await tx.contactTicket.create({
        data: {
          firstName: body.firstName ?? "-",
          lastName: body.lastName ?? "-",
          email: body.email,
          reason: body.reason ?? "consulta",
          phone: body.phone ?? "-",
          description: body.description,
          status: "open",
        },
        select: { id: true, firstName: true, lastName: true, email: true, reason: true },
      });

      await tx.ticketMessage.create({
        data: {
          ticketId: t.id,
          author: "user",
          name: [body.firstName, body.lastName].filter(Boolean).join(" ") || "Usuario",
          email: body.email,
          body: body.description,
        },
      });

      return t;
    });

    // ── Enviar correo ──
    const host = requireEnv("SMTP_HOST");
    const port = Number(requireEnv("SMTP_PORT"));
    const user = requireEnv("SMTP_USER");
    const pass = requireEnv("SMTP_PASS");
    const from = process.env.SMTP_FROM || user;

    const transporter = nodemailer.createTransport({
      host, port, secure: port === 465, auth: { user, pass },
    });

    const asunto = `Nuevo ticket #${ticket.id} - ${ticket.reason}`;
    const html = `
      <h2>Nuevo contacto recibido</h2>
      <p><b>Ticket:</b> #${ticket.id}</p>
      <p><b>Nombre:</b> ${ticket.firstName} ${ticket.lastName}</p>
      <p><b>Email:</b> ${ticket.email}</p>
      <p><b>Motivo:</b> ${ticket.reason}</p>
      <p><b>Descripción:</b><br/>${body.description.replace(/\n/g, "<br/>")}</p>
    `;

    const safe = (s?: string) =>
      (s ?? "").toString().replace(/[\r\n"<>\(\)]/g, " ").trim().slice(0, 120);
    const fullName = [safe(body.firstName), safe(body.lastName)].filter(Boolean).join(" ") || "Contacto";

    const info = await transporter.sendMail({
      from: `"EncryptU Contacto" <${from}>`,
      to: from,
      replyTo: `"${fullName}" <${safe(body.email)}>`,
      subject: asunto,
      html,
    });

    const { messageId } = info as { messageId?: string };

    // ── Respuesta ──
    return NextResponse.json({
      ok: true,
      id: ticket.id,
      messageId: String(messageId ?? ""),
    });
  } catch (err: unknown) {
    const message = toErrorMessage(err);
    return NextResponse.json({ ok: false, error: message }, { status: 500 });
  }
}

// src/app/api/contactoapi/route.ts
import { NextResponse } from "next/server";
import nodemailer from "nodemailer";

export const runtime = "nodejs";

type Incoming = {
  firstName?: string;
  lastName?: string;
  email?: string;
  reason?: string;
  phone?: string;
  description?: string;
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

function requireEnv(name: string) {
  const v = process.env[name];
  if (!v) throw new Error(`Falta variable de entorno ${name}`);
  return v;
}

function toErrorMessage(err: unknown): string {
  if (err instanceof Error) return err.message;
  if (typeof err === "string") return err;
  try {
    return JSON.stringify(err);
  } catch {
    return "Error del servidor";
  }
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

export async function POST(req: Request) {
  try {
    const raw = (await req.json()) as Incoming;
    const body = normalize(raw);

    // ── Validaciones ──
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

    // ── SMTP Config ──
    const host = requireEnv("SMTP_HOST");
    const port = Number(requireEnv("SMTP_PORT"));
    const user = requireEnv("SMTP_USER");
    const pass = requireEnv("SMTP_PASS");
    const from = process.env.SMTP_FROM || user;

    const transporter = nodemailer.createTransport({
      host,
      port,
      secure: port === 465,
      auth: { user, pass },
    });

    const asunto = `Contacto: ${body.reason ?? "General"}`;
    const html = `
      <h2>Nuevo contacto</h2>
      <p><b>Nombre:</b> ${body.firstName || "-"}</p>
      <p><b>Apellido:</b> ${body.lastName || "-"}</p>
      <p><b>Email:</b> ${body.email}</p>
      <p><b>Motivo:</b> ${body.reason || "-"}</p>
      <p><b>Teléfono:</b> ${body.phone || "-"}</p>
      <p><b>Descripción:</b><br/>${body.description.replace(/\n/g, "<br/>")}</p>
    `;

    // Evita inyección de cabeceras en replyTo
    const safe = (s?: string) =>
      (s ?? "").toString().replace(/[\r\n"<>\(\)]/g, " ").trim().slice(0, 120);
    const fullName = [safe(body.firstName), safe(body.lastName)].filter(Boolean).join(" ") || "Contacto";

    const id = Date.now();

    // Correo principal (a tu buzón)
    const info = await transporter.sendMail({
      from: `"EncryptU Contacto" <${from}>`, // remitente del dominio (no spoofea)
      to: from,                              // llega a tu propio correo
      replyTo: `"${fullName}" <${safe(body.email)}>`, // clave: destinatario para responder
      subject: asunto,
      html,
    });

    const { messageId } = info as { messageId?: string };

    return NextResponse.json({
      ok: true,
      id,
      messageId: String(messageId ?? ""),
    });
  } catch (err: unknown) {
    const message = toErrorMessage(err);
    return NextResponse.json({ ok: false, error: message }, { status: 500 });
  }
}

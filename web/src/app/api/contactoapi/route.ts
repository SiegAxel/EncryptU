import { NextResponse } from "next/server";
import nodemailer from "nodemailer";

export const runtime = "nodejs";

type ContactInput = {
  apellido?: string;
  email?: string;
  motivo?: string;
  telefono?: string;
  descripcion?: string;
};

function requireEnv(name: string) {
  const v = process.env[name];
  if (!v) throw new Error(`Falta variable de entorno ${name}`);
  return v;
}

// Utilidad para extraer el mensaje sin usar `any`
function toErrorMessage(err: unknown): string {
  if (err instanceof Error) return err.message;
  if (typeof err === "string") return err;
  try {
    return JSON.stringify(err);
  } catch {
    return "Error del servidor";
  }
}

export async function POST(req: Request) {
  try {
    const body = (await req.json()) as ContactInput;

    const emailRe = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/i;
    if (!emailRe.test(body.email || "") || !(body.descripcion || "").trim()) {
      return NextResponse.json({ ok: false, error: "Datos inválidos" }, { status: 400 });
    }

    const host = requireEnv("SMTP_HOST");
    const port = Number(requireEnv("SMTP_PORT")); // 465 o 587
    const user = requireEnv("SMTP_USER");
    const pass = requireEnv("SMTP_PASS");
    const from = process.env.SMTP_FROM || user;

    const transporter = nodemailer.createTransport({
      host,
      port,
      secure: port === 465,
      auth: { user, pass },
    });

    const asunto = `Contacto: ${body.motivo || "General"}`;
    const html = `
      <h2>Nuevo contacto</h2>
      <p><b>Apellido:</b> ${body.apellido || "-"}</p>
      <p><b>Email:</b> ${body.email}</p>
      <p><b>Motivo:</b> ${body.motivo || "-"}</p>
      <p><b>Teléfono:</b> ${body.telefono || "-"}</p>
      <p><b>Descripción:</b><br/>${(body.descripcion || "").replace(/\n/g, "<br/>")}</p>
    `;

    const info = await transporter.sendMail({
      from,
      to: from,
      subject: asunto,
      html,
    });

    // `info` es `nodemailer.SentMessageInfo`; `messageId` suele ser string
    return NextResponse.json({ ok: true, messageId: String((info as any).messageId ?? "") });
  } catch (err: unknown) {
    const message = toErrorMessage(err);
    return NextResponse.json({ ok: false, error: message }, { status: 500 });
  }
}

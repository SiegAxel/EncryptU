"use client";
import { useState, type ChangeEvent, type FormEvent } from "react";
import Container from "@/components/layout/ui/Container";
import Section from "@/components/layout/ui/Section";
import Card from "@/components/layout/ui/Card";
import Input from "@/components/layout/ui/Input";
import Button from "@/components/layout/ui/Button";
import FAQAccordion from "@/components/layout/FAQAccordion";

type Form = {
  firstName: string;
  lastName: string;
  email: string;
  reason: "soporte" | "consulta" | "";
  phone: string;       // solo 9 dígitos
  description: string; // máx 500 palabras
};

type ApiResponse = { ok: boolean; id?: number; error?: string };

// ───────── helpers de validación ─────────
const nameRe = /^[A-Za-zÁÉÍÓÚÜÑáéíóúüñ\s'-]{2,}$/;
const emailRe = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/i;
const phoneRe = /^\d{9}$/;

function countWords(s: string) {
  return (s.trim().match(/\S+/g) || []).length;
}

function validate(form: Form) {
  const errors: Partial<Record<keyof Form, string>> = {};

  if (!form.firstName.trim() || !nameRe.test(form.firstName.trim())) {
    errors.firstName = "Nombre inválido. Usa solo letras y espacios (mín. 2).";
  }
  if (!form.lastName.trim() || !nameRe.test(form.lastName.trim())) {
    errors.lastName = "Apellido inválido. Usa solo letras y espacios (mín. 2).";
  }
  if (!emailRe.test(form.email)) {
    errors.email = "Correo no válido.";
  }
  if (!phoneRe.test(form.phone)) {
    errors.phone = "El teléfono debe tener exactamente 9 dígitos (Chile).";
  }
  if (form.reason !== "soporte" && form.reason !== "consulta") {
    errors.reason = "Selecciona un motivo válido.";
  }
  if (countWords(form.description) === 0) {
    errors.description = "La descripción es obligatoria.";
  } else if (countWords(form.description) > 500) {
    errors.description = "Máximo 500 palabras.";
  }
  return errors;
}

// Datos de FAQ
const faqItems = [
  {
    question: "¿Cómo descargo e instalo EncryptU?",
    answer: "Puedes descargar el instalador desde nuestra página de instalación. El instalador es compatible con Windows 10 y 11, y la instalación toma menos de 2 minutos."
  },
  {
    question: "¿Es seguro usar EncryptU?",
    answer: "Sí, EncryptU utiliza cifrado AES-256 de grado militar y Argon2 para el hashing de contraseñas. Tu información se almacena localmente con cifrado de extremo a extremo."
  },
  {
    question: "¿Puedo importar mis contraseñas desde otros gestores?",
    answer: "En un futuro. EncryptU tiene planeado incorporar el importar automáticamente contraseñas desde navegadores populares como Chrome, Firefox, Edge y Safari, así como desde otros gestores de contraseñas en un futuro."
  },
  {
    question: "¿Qué planes de suscripción ofrece EncryptU?",
    answer: "Ofrecemos tres planes: Básico (gratuito), Estándar ($6/mes) para equipos pequeños, y Premium ($10/mes) para empresas. Visita nuestra página de planes para más detalles."
  },
  {
    question: "¿Cómo funciona la sincronización entre dispositivos?",
    answer: "La sincronización se realiza a través de nuestros servidores seguros usando cifrado de extremo a extremo. Solo tú tienes acceso a tus datos desencriptados."
  },
  {
    question: "¿Qué hago si olvido mi contraseña maestra?",
    answer: "Por seguridad, la contraseña maestra no se puede recuperar. Sin embargo, si aun tienes tu sesion activa, puedes enviar un ticket y recuperar el acceso."
  },
  {
    question: "¿Ofrecen soporte técnico?",
    answer: "Sí, nuestro equipo de soporte está disponible para ayudarte con instalación, configuración y resolución de problemas. Puedes contactarnos a través de este formulario."
  }
];

// ───────── componente ─────────
export default function ContactPage() {
  const [form, setForm] = useState<Form>({
    firstName: "",
    lastName: "",
    email: "",
    reason: "",
    phone: "",
    description: "",
  });

  const [errors, setErrors] = useState<Partial<Record<keyof Form, string>>>({});
  const [touched, setTouched] = useState<Partial<Record<keyof Form, boolean>>>({});
  const [sending, setSending] = useState(false);
  const [msg, setMsg] = useState<string | null>(null);

  // actualiza y revalida por campo
  const setField =
    (k: keyof Form) =>
    (v: string) => {
      setForm((f) => {
        const next = { ...f, [k]: v };
        if (touched[k]) {
          setErrors(validate(next));
        }
        return next;
      });
    };

  // handlers
  const onInput =
    (k: keyof Form) =>
    (e: ChangeEvent<HTMLInputElement>) => {
      let v = e.target.value;
      // solo números para phone y recortar a 9
      if (k === "phone") {
        v = v.replace(/\D/g, "").slice(0, 9);
      }
      setField(k)(v);
    };

  const onTextArea =
    (k: keyof Form) =>
    (e: ChangeEvent<HTMLTextAreaElement>) => {
      const v = e.target.value;
      setField(k)(v);
    };

  const onBlur =
    (k: keyof Form) =>
    () => {
      setTouched((t) => ({ ...t, [k]: true }));
      setErrors(validate(form));
    };

  const submit = async (e: FormEvent) => {
    e.preventDefault();
    setTouched({
      firstName: true,
      lastName: true,
      email: true,
      reason: true,
      phone: true,
      description: true,
    });

    const errs = validate(form);
    setErrors(errs);
    if (Object.keys(errs).length > 0) return;

    setSending(true);
    setMsg(null);

    const res = await fetch("/api/contactoapi", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(form),
    });

    const data: ApiResponse = await res.json();
    if (res.ok) {
      setMsg(`¡Enviado! Ticket #${data.id}`);
      setForm({
        firstName: "",
        lastName: "",
        email: "",
        reason: "",
        phone: "",
        description: "",
      });
      setTouched({});
      setErrors({});
    } else {
      setMsg(data?.error ?? "Revisa los datos");
    }
    setSending(false);
  };

  const descWords = countWords(form.description);
  const descTooLong = descWords > 500;

  return (
    <Section>
      <Container>
        {/* Sección principal de contacto */}
        <div className="grid gap-6 md:grid-cols-2 mb-12">
          <Card>
            <h1 className="mb-3 text-xl font-semibold">Contáctanos</h1>
            <form className="space-y-3" onSubmit={submit} noValidate>
              <div>
                <Input
                  label="Nombre"
                  value={form.firstName}
                  onChange={onInput("firstName")}
                  onBlur={onBlur("firstName")}
                />
                {touched.firstName && errors.firstName && (
                  <p className="mt-1 text-xs text-red-600">{errors.firstName}</p>
                )}
              </div>

              <div>
                <Input
                  label="Apellido"
                  value={form.lastName}
                  onChange={onInput("lastName")}
                  onBlur={onBlur("lastName")}
                />
                {touched.lastName && errors.lastName && (
                  <p className="mt-1 text-xs text-red-600">{errors.lastName}</p>
                )}
              </div>

              <div>
                <Input
                  label="Correo electrónico"
                  type="email"
                  value={form.email}
                  onChange={onInput("email")}
                  onBlur={onBlur("email")}
                />
                {touched.email && errors.email && (
                  <p className="mt-1 text-xs text-red-600">{errors.email}</p>
                )}
              </div>

              <div>
                <label className="block space-y-1">
                  <span className="text-sm text-slate-600">Motivo</span>
                  <select
                    className="input"
                    value={form.reason}
                    onChange={(e) =>
                      setField("reason")(e.target.value as Form["reason"])
                    }
                    onBlur={onBlur("reason")}
                  >
                    <option value="">Selecciona…</option>
                    <option value="soporte">Soporte</option>
                    <option value="consulta">Consulta</option>
                  </select>
                </label>
                {touched.reason && errors.reason && (
                  <p className="mt-1 text-xs text-red-600">{errors.reason}</p>
                )}
              </div>

              <div>
                <Input
                  label="Número de teléfono (9 dígitos)"
                  inputMode="numeric"
                  pattern="\d{9}"
                  maxLength={9}
                  value={form.phone}
                  onChange={onInput("phone")}
                  onBlur={onBlur("phone")}
                />
                {touched.phone && errors.phone && (
                  <p className="mt-1 text-xs text-red-600">{errors.phone}</p>
                )}
              </div>

              <div>
                <label className="block space-y-1">
                  <span className="text-sm text-slate-600">Descripción</span>
                  <textarea
                    className={`input min-h-[120px] ${descTooLong ? "ring-2 ring-red-400" : ""}`}
                    value={form.description}
                    onChange={onTextArea("description")}
                    onBlur={onBlur("description")}
                  />
                </label>
                <div className="mt-1 flex justify-between text-xs">
                  {touched.description && errors.description ? (
                    <p className="text-red-600">{errors.description}</p>
                  ) : (
                    <span />
                  )}
                  <span className={descTooLong ? "text-red-600" : "text-slate-500"}>
                    {descWords}/500 palabras
                  </span>
                </div>
              </div>

              <Button className="w-full" type="submit" disabled={sending}>
                {sending ? "Enviando..." : "Enviar formulario"}
              </Button>

              {msg && <p className="text-sm text-slate-700">{msg}</p>}
            </form>
          </Card>
          <img src="/negrito.png" className="mt-60 ml-35"/>
        </div>

        {/* Sección de FAQ */}
        <div className="mb-12">
          <Card>
            <div className="text-center mb-8">
              <h2 className="text-2xl font-bold text-gray-900 mb-2">
                Preguntas Frecuentes
              </h2>
              <p className="text-gray-600">
                Encuentra respuestas rápidas a las consultas más comunes sobre EncryptU
              </p>
            </div>
            <FAQAccordion items={faqItems} />
          </Card>
        </div>

        {/* Sección del logo de EncryptU */}
        <div className="text-center">
          <Card className="inline-block">
            <div className="flex flex-col items-center space-y-4">
              <img
                src="/negrito.png"
                alt="EncryptU Logo"
                className="h-16 w-auto"
              />
              <div>
                <p className="text-sm text-gray-600">
                  Gestión de contraseñas segura
                </p>
              </div>
            </div>
          </Card>
        </div>
      </Container>
    </Section>
  );
}

// web/src/components/layout/Navbar.tsx
"use client";
import Link from "next/link";
import Image from "next/image";
import { useEffect, useState } from "react";
import { usePathname, useRouter } from "next/navigation";
import Container from "@/components/layout/ui/Container";
import SocialBar from "./SocialBar";
import { cn } from "@/lib/cn";

const nav = [
  { href: "/", label: "Inicio" },
  { href: "/marketing/acerca", label: "Nosotros" },
  { href: "/marketing/planes", label: "Planes" },
  { href: "/marketing/contacto", label: "Contacto" },
  { href: "/marketing/ticket", label: "Tickets" }
];

type Me =
  | { ok: true; user: { name: string; role: "usuario" | "soporte" | "admin" } }
  | { ok: false };

export default function Navbar() {
  const pathname = usePathname();
  const router = useRouter();
  const [me, setMe] = useState<Me>({ ok: false });

  async function loadMe() {
    try {
      const res = await fetch("/api/me", { cache: "no-store", credentials: "include" });
      const data = (await res.json()) as Me;
      setMe(data);
    } catch {
      setMe({ ok: false });
    }
  }

  useEffect(() => {
    loadMe();
  }, [pathname]); // ← se re-ejecuta al cambiar de ruta

  const logout = async () => {
    await fetch("/api/logout", { method: "POST", credentials: "include" });
    setMe({ ok: false });
    router.push("/");
    router.refresh();
  };

  return (
    <header className="sticky top-0 z-40 w-full border-b bg-white/80 backdrop-blur">
      <Container>
        <div className="flex h-16 items-center justify-between gap-4">
          <Link href="/" className="flex items-center gap-2">
            <Image src="/negrito.png" alt="EncryptU" width={200} height={200} />
          </Link>

          <nav className="hidden items-center gap-6 md:flex">
            {/* enlaces públicos */}
            <Link href="/" className={cn("text-sm hover:text-brand", pathname === "/" && "text-brand font-medium")}>
              Inicio
            </Link>
            <Link href="/marketing/acerca" className={cn("text-sm hover:text-brand", pathname === "/marketing/acerca" && "text-brand font-medium")}>
              Nosotros
            </Link>
            <Link href="/marketing/planes" className={cn("text-sm hover:text-brand", pathname === "/marketing/planes" && "text-brand font-medium")}>
              Planes
            </Link>
            <Link href="/marketing/contacto" className={cn("text-sm hover:text-brand", pathname === "/marketing/contacto" && "text-brand font-medium")}>
              Contacto
            </Link>

            {/* SOLO usuarios: Tickets */}
            {me.ok && me.user.role === "usuario" && (
              <Link
                href="/marketing/ticket"
                className={cn("text-sm hover:text-brand", pathname === "/marketing/ticket" && "text-brand font-medium")}
              >
                Tickets
              </Link>
            )}
          </nav>



          <div className="flex items-center gap-2">
            {me.ok ? (
              <>
                <span className="text-sm">¡Bienvenido {me.user.name}!</span>
                {me.user.role === "admin" && (
                  <Link href="/dashboard/admin" className="btn-outline text-sm">Admin</Link>
                )}
                {me.user.role === "soporte" && (
                  <Link href="/dashboard/soporte" className="btn-outline text-sm">Soporte</Link>
                )}
                <button onClick={logout} className="btn-primary text-sm">Salir</button>
              </>
            ) : (
              <>
                <Link href="/auth/login" className="btn-outline text-sm">Ingresar</Link>
                <Link href="/auth/registro" className="btn-primary text-sm">Crear cuenta</Link>
              </>
            )}
          </div>
        </div>
      </Container>
    </header>
  );
}

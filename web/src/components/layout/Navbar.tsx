"use client";
import Link from "next/link";
import Image from "next/image";
import { usePathname } from "next/navigation";
import Container from "@/components/layout/ui/Container";
import SocialBar from "./SocialBar";
import { cn } from "@/lib/cn";
import ButtonLink from "@/components/layout/ui/ButtonLink";

const nav = [
  { href: "/", label: "Inicio" },
  { href: "/marketing/acerca", label: "Nosotros" },
  { href: "/marketing/planes", label: "Planes" },
  { href: "/marketing/contacto", label: "Contacto" },
];

export default function Navbar() {
  const pathname = usePathname();
  return (
    <header className="sticky top-0 z-40 w-full border-b bg-white/80 backdrop-blur">
      <Container>
        <div className="flex h-16 items-center justify-between gap-4">
          <Link href="/" className="flex items-center gap-2">
            <Image src="/logo.svg" alt="EncryptU" width={32} height={32} />
            <span className="text-xl font-semibold">
              Encrypt<span className="text-brand">U</span>
            </span>
          </Link>

          <nav className="hidden items-center gap-6 md:flex">
            {nav.map((item) => (
              <Link
                key={item.href}
                href={item.href}
                className={cn(
                  "text-sm hover:text-brand",
                  pathname === item.href && "text-brand font-medium"
                )}
              >
                {item.label}
              </Link>
            ))}
          </nav>

          <div className="hidden md:block">
            <SocialBar />
          </div>


          <div className="flex items-center gap-2">
            <ButtonLink href="/auth/login" variant="outline" size="md">
              Ingresar
            </ButtonLink>
            <ButtonLink href="/auth/registro" variant="primary" size="md">
              Crear cuenta
            </ButtonLink>
          </div>

        </div>

      </Container>
    </header>
  );
}

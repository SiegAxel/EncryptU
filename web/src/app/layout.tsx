// src/app/layout.tsx
import "./globals.css";
import Navbar from "@/components/layout/Navbar";
import Footer from "@/components/layout/Footer";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "EncryptU",
  description: "Gestor de contraseñas seguras",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="es" suppressHydrationWarning>
      {/* min-h-dvh + flex-col para “empujar” el footer abajo */}
      <body className="min-h-dvh flex flex-col bg-white text-slate-800 dark:bg-slate-950 dark:text-slate-200">
        <Navbar />
        {/* main ocupa el espacio restante */}
        <main className="flex-1">
          {children}
        </main>
        <Footer />
      </body>
    </html>
  );
}

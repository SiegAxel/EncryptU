"use client";

import Link from "next/link";

export default function Footer() {
  const year = new Date().getFullYear();

  return (
    <footer className="border-t bg-white text-slate-700 dark:bg-slate-950 dark:text-slate-200">
      <div className="mx-auto max-w-6xl px-4 py-10">
        <div className="grid gap-8 md:grid-cols-3">
          {/* Columna izquierda: redes */}
          <div>
            <p className="text-lg font-medium mb-4">
              Síguenos en nuestras redes sociales
            </p>
            <div className="flex items-center gap-6">
              <a
                href="https://facebook.com"
                aria-label="Facebook"
                target="_blank"
                rel="noopener noreferrer"
                className="transition-opacity hover:opacity-80"
              >
                {/* Facebook */}
                <svg width="28" height="28" viewBox="0 0 24 24" fill="currentColor" className="text-[#1877F2]">
                  <path d="M22 12.06C22 6.51 17.52 2 12 2S2 6.51 2 12.06c0 5.02 3.66 9.18 8.44 9.94v-7.03H7.9v-2.91h2.54V9.41c0-2.5 1.49-3.89 3.77-3.89 1.09 0 2.23.2 2.23.2v2.45h-1.26c-1.24 0-1.63.77-1.63 1.56v1.86h2.78l-.44 2.91h-2.34V22c4.78-.76 8.44-4.92 8.44-9.94Z" />
                </svg>
              </a>

              <a
                href="https://linkedin.com"
                aria-label="LinkedIn"
                target="_blank"
                rel="noopener noreferrer"
                className="transition-opacity hover:opacity-80"
              >
                {/* LinkedIn */}
                <svg width="28" height="28" viewBox="0 0 24 24" fill="currentColor" className="text-[#0A66C2]">
                  <path d="M4.98 3.5C4.98 4.6 4.1 5.5 3 5.5S1 4.6 1 3.5 1.9 1.5 3 1.5s1.98.9 1.98 2Zm.02 4H1V22h4V7.5ZM13 7.3c-2.14 0-3.58 1.17-4.19 2.27h-.06V7.5H5v14.5h3.9v-7.2c0-1.9.36-3.75 2.72-3.75 2.32 0 2.35 2.16 2.35 3.86V22H18V14.5c0-4.04-.86-7.2-5-7.2Z"/>
                </svg>
              </a>

              <a
                href="https://instagram.com"
                aria-label="Instagram"
                target="_blank"
                rel="noopener noreferrer"
                className="transition-opacity hover:opacity-80"
              >
                {/* Instagram */}
                <svg width="28" height="28" viewBox="0 0 24 24" fill="currentColor" className="text-[#E1306C]">
                  <path d="M7 2h10a5 5 0 0 1 5 5v10a5 5 0 0 1-5 5H7a5 5 0 0 1-5-5V7a5 5 0 0 1 5-5Zm0 2a3 3 0 0 0-3 3v10a3 3 0 0 0 3 3h10a3 3 0 0 0 3-3V7a3 3 0 0 0-3-3H7Zm5 3.5A5.5 5.5 0 1 1 6.5 13 5.51 5.51 0 0 1 12 7.5Zm0 2A3.5 3.5 0 1 0 15.5 13 3.5 3.5 0 0 0 12 9.5Zm5.25-3a1.25 1.25 0 1 1-1.25 1.25A1.25 1.25 0 0 1 17.25 6.5Z"/>
                </svg>
              </a>

              <a
                href="https://github.com"
                aria-label="GitHub"
                target="_blank"
                rel="noopener noreferrer"
                className="transition-opacity hover:opacity-80"
              >
                {/* GitHub (circ badge) */}
                <svg width="28" height="28" viewBox="0 0 24 24" fill="currentColor" className="text-slate-900 dark:text-white">
                  <path d="M12 2a10 10 0 0 0-3.16 19.49c.5.09.68-.22.68-.48 0-.23-.01-.84-.01-1.64-2.78.6-3.37-1.19-3.37-1.19-.45-1.16-1.11-1.47-1.11-1.47-.9-.62.07-.6.07-.6 1 .07 1.53 1.03 1.53 1.03.89 1.52 2.33 1.08 2.9.83.09-.65.35-1.08.63-1.33-2.22-.25-4.56-1.11-4.56-4.95 0-1.09.39-1.99 1.03-2.69-.1-.25-.45-1.27.1-2.64 0 0 .84-.27 2.75 1.03a9.5 9.5 0 0 1 5 0c1.91-1.3 2.75-1.03 2.75-1.03.55 1.37.2 2.39.1 2.64.64.7 1.03 1.6 1.03 2.69 0 3.85-2.34 4.7-4.57 4.95.36.31.68.92.68 1.86 0 1.34-.01 2.42-.01 2.75 0 .26.18.58.69.48A10 10 0 0 0 12 2Z"/>
                </svg>
              </a>
            </div>
          </div>

          {/* Columna centro: copyright */}
          <div className="flex items-end md:items-center justify-center">
            <p className="text-sm text-slate-500 dark:text-slate-400">
              © {year} EncryptU — Syntec
            </p>
          </div>

          {/* Columna derecha: enlaces */}
          <div className="flex flex-col items-end gap-2 text-right">
            <Link href="/marketing/Contáctanos" className="hover:text-slate-900 dark:hover:text-white">
              Hablemos
            </Link>
            <Link href="/marketing/Contáctanos" className="hover:text-slate-900 dark:hover:text-white">
              Contáctanos
            </Link>
            <a href="tel:+562224117480" className="hover:text-slate-900 dark:hover:text-white">
              56(2)224117480
            </a>
            <Link href="/privacidad" className="text-rose-600 hover:underline">
              Política de Privacidad
            </Link>
          </div>
        </div>
      </div>
    </footer>
  );
}

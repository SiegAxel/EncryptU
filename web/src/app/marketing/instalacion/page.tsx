// src/app/marketing/instalacion/page.tsx
import Link from "next/link";
import Section from "@/components/layout/ui/Section";
import Container from "@/components/layout/ui/Container";
import Card from "@/components/layout/ui/Card";
import ButtonLink from "@/components/layout/ui/ButtonLink";
import { FaFacebook, FaLinkedin, FaInstagram, FaGithub } from "react-icons/fa";
import DownloadButton from "@/components/layout/DowloadButton";

export default function InstalacionPage() {
  return (
    <Section>
      <Container>
        {/* Encabezado */}
        <header className="mb-6">
          <h1 className="text-2xl md:text-3xl font-bold">Instalación</h1>
        </header>

        {/* Contenido principal */}
        <div className="grid gap-6 lg:grid-cols-3">
          {/* Columna principal */}
          <div className="lg:col-span-2 space-y-6">
            <Card>
              <div className="space-y-4">
                <h2 className="text-lg font-semibold">⚙️ Pasos de instalación</h2>

                <ol className="list-decimal pl-5 space-y-3 text-sm md:text-base">
                  <li>
                    <span className="font-semibold">Descarga el programa</span>
                    <ul className="list-disc pl-5 mt-2 space-y-1">
                      <li>Ve a la página del proyecto en <Link className="text-brand underline" href="https://github.com/SiegAxel/EncryptU/blob/main/docs/user-guide.md" target="_blank">GitHub</Link>.</li>
                      <li>En <em>Releases</em> encontrarás el instalador para tu sistema operativo.</li>
                    </ul>
                  </li>

                  <li>
                    <span className="font-semibold">Sistema Windows</span>
                    <ul className="list-disc pl-5 mt-2 space-y-1">
                      <li>Descarga el archivo <code>.exe</code>.</li>
                      <li>Ejecuta el instalador y acepta los permisos correspondientes.</li>
                    </ul>
                  </li>

                  <li>
                    <span className="font-semibold">Sistema Linux</span>
                    <ul className="list-disc pl-5 mt-2 space-y-1">
                      <li>Descarga el paquete correspondiente a tu distro.</li>
                      <li>Usa el gestor de paquetes o ejecuta el instalador (según corresponda).</li>
                    </ul>
                  </li>

                  <li>
                    <span className="font-semibold">Primer inicio</span>
                    <ul className="list-disc pl-5 mt-2 space-y-1">
                      <li>Abre la aplicación y completa el asistente inicial (tema y seguridad).</li>
                      <li>Activa el cifrado local y define una contraseña maestra.</li>
                    </ul>
                  </li>

                  <li>
                    <span className="font-semibold">Actualizaciones</span>
                    <ul className="list-disc pl-5 mt-2 space-y-1">
                      <li>El sistema avisará cuando haya nuevas versiones disponibles.</li>
                      <li>Podrás actualizar desde el propio programa en “Ajustes &raquo; Actualizar”.</li>
                    </ul>
                  </li>
                </ol>

                {/* CTA de descarga */}
                <div className="pt-2" >
                  <DownloadButton
                    imageUrl="/team/venezolano.png"
                    fileName="venezolano-descargado.png"
                    className="bg-rose-400 hover:bg-rose-600 text-white font-bold py-2 px-6 rounded-lg transition-colors duration-300"
                  >
                    Descargar Imagen
                  </DownloadButton>
                </div>
              </div>
            </Card>

            {/* Callout de descarga completa */}
            <Card>
              <div className="flex items-start gap-3">
                <div className="mt-0.5 h-3 w-3 rounded-full bg-emerald-500" />
                <div className="space-y-1">
                  <h3 className="font-semibold">✅ Descarga completada</h3>
                  <p className="text-sm text-slate-600">
                    Abre la carpeta de descargas y ejecuta el instalador. Disfruta de EncryptU y
                    cuida tus contraseñas con buenas prácticas de seguridad.
                  </p>
                </div>
              </div>
            </Card>

            {/* Ayuda / Soporte */}
            <Card>
              <div className="space-y-3">
                <h3 className="font-semibold">¿Necesitas ayuda?</h3>
                <p className="text-sm text-slate-600">
                  Nuestro equipo de soporte cuenta con experiencia técnica y está disponible para ayudarte
                  con la instalación o configuración. También contamos con guías y preguntas frecuentes.
                </p>
                <div className="flex flex-wrap gap-2">
                  <ButtonLink href="/marketing/contacto" variant="outline">Contactar</ButtonLink>
                </div>
              </div>
            </Card>
          </div>

          {/* Columna lateral: info breve / políticas */}
          <aside className="space-y-6">
            <Card>
              <div className="space-y-2">
                <h4 className="font-semibold">Información</h4>
                <ul className="text-sm text-slate-600 space-y-1">
                  <li><Link href="/marketing/politicas" className="underline">Políticas de Privacidad</Link></li>
                  <li><Link href="/marketing/planes" className="underline">Planes y precios</Link></li>
                  <li><Link href="/marketing/acerca" className="underline">Acerca de nosotros</Link></li>
                </ul>
              </div>
            </Card>

            {/* Redes sociales */}
            <Card>
              <div className="space-y-3">
                <h4 className="font-semibold">Síguenos</h4>
                <div className="flex items-center gap-4 text-xl">
                  <Link href="https://facebook.com" aria-label="Facebook" target="_blank"><FaFacebook /></Link>
                  <Link href="https://linkedin.com" aria-label="LinkedIn" target="_blank"><FaLinkedin /></Link>
                  <Link href="https://instagram.com" aria-label="Instagram" target="_blank"><FaInstagram /></Link>
                  <Link href="https://github.com/SiegAxel/EncryptU" aria-label="GitHub" target="_blank"><FaGithub /></Link>
                </div>
              </div>
            </Card>
          </aside>
        </div>
      </Container>
    </Section>
  );
}

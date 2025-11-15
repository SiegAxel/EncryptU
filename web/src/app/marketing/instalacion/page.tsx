"use client";

import Link from "next/link";
import Section from "@/components/layout/ui/Section";
import Container from "@/components/layout/ui/Container";
import Card from "@/components/layout/ui/Card";
import ButtonLink from "@/components/layout/ui/ButtonLink";
import InstallDownloadButton from "@/components/layout/InstallDownloadButton";
import { FaDownload, FaShieldAlt, FaCog, FaCheckCircle, FaExclamationTriangle, FaGithub, FaFacebook, FaLinkedin, FaInstagram } from "react-icons/fa";

export default function InstalacionPage() {
  return (
    <Section>
      <Container>
        {/* Hero Section */}
        <div className="text-center mb-12">
          <div className="flex justify-center mb-6">
            <div className="w-20 h-20 bg-gradient-to-br from-red-500 to-red-600 rounded-2xl flex items-center justify-center">
              <FaDownload className="w-10 h-10 text-white" />
            </div>
          </div>
          <h1 className="text-4xl md:text-5xl font-bold text-gray-900 mb-4">
            Descargar EncryptU
          </h1>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            La aplicación completa de gestión de contraseñas segura para Windows. 
            Protege tus datos con la mejor tecnología de cifrado.
          </p>
        </div>

        {/* Main Download Section */}
        <div className="grid gap-8 lg:grid-cols-2 mb-12">
          {/* Download Button */}
          <div className="flex justify-center lg:justify-end">
            <InstallDownloadButton 
              installerUrl="/downloads/EncryptU-Setup-v1.0.0.exe"
              fileName="EncryptU-Setup-v1.0.0.exe"
              size="45.2 MB"
              version="v1.0.0"
            />
          </div>

          {/* Features */}
          <div className="space-y-6">
            <Card>
              <div className="flex items-start gap-4">
                <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center flex-shrink-0">
                  <FaShieldAlt className="w-6 h-6 text-green-600" />
                </div>
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">
                    Seguridad de Nivel Empresarial
                  </h3>
                  <p className="text-gray-600">
                    Cifrado AES-256, Argon2 para contraseñas, y sincronización segura entre dispositivos.
                  </p>
                </div>
              </div>
            </Card>

            <Card>
              <div className="flex items-start gap-4">
                <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center flex-shrink-0">
                  <FaCog className="w-6 h-6 text-blue-600" />
                </div>
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">
                    Fácil de Usar
                  </h3>
                  <p className="text-gray-600">
                    Interfaz intuitiva, importación automática de navegadores, y configuración en minutos.
                  </p>
                </div>
              </div>
            </Card>

            <Card>
              <div className="flex items-start gap-4">
                <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center flex-shrink-0">
                  <FaDownload className="w-6 h-6 text-purple-600" />
                </div>
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">
                    Descarga Directa
                  </h3>
                  <p className="text-gray-600">
                    Instalador verificado, libre de malware, y compatible con Windows 10 y 11.
                  </p>
                </div>
              </div>
            </Card>
          </div>
        </div>

        {/* Installation Steps */}
        <div className="grid gap-8 lg:grid-cols-3 mb-12">
          <div className="lg:col-span-2">
            <Card>
              <div className="space-y-6">
                <h2 className="text-2xl font-bold text-gray-900 mb-4">
                   Proceso de Instalación
                </h2>

                <div className="space-y-6">
                  <div className="flex gap-4">
                    <div className="w-8 h-8 bg-red-600 text-white rounded-full flex items-center justify-center font-bold text-sm flex-shrink-0">
                      1
                    </div>
                    <div>
                      <h3 className="font-semibold text-gray-900 mb-2">Descargar</h3>
                      <p className="text-gray-600 text-sm">
                        Haz clic en el botón de descarga para obtener el instalador más reciente de EncryptU.
                      </p>
                    </div>
                  </div>

                  <div className="flex gap-4">
                    <div className="w-8 h-8 bg-red-600 text-white rounded-full flex items-center justify-center font-bold text-sm flex-shrink-0">
                      2
                    </div>
                    <div>
                      <h3 className="font-semibold text-gray-900 mb-2">Ejecutar</h3>
                      <p className="text-gray-600 text-sm">
                        Localiza el archivo descargado (EncryptU-Setup-v1.0.0.exe) y ejecútalo como administrador.
                      </p>
                    </div>
                  </div>

                  <div className="flex gap-4">
                    <div className="w-8 h-8 bg-red-600 text-white rounded-full flex items-center justify-center font-bold text-sm flex-shrink-0">
                      3
                    </div>
                    <div>
                      <h3 className="font-semibold text-gray-900 mb-2">Instalar</h3>
                      <p className="text-gray-600 text-sm">
                        Sigue las instrucciones del instalador. La instalación toma menos de 2 minutos.
                      </p>
                    </div>
                  </div>

                  <div className="flex gap-4">
                    <div className="w-8 h-8 bg-red-600 text-white rounded-full flex items-center justify-center font-bold text-sm flex-shrink-0">
                      4
                    </div>
                    <div>
                      <h3 className="font-semibold text-gray-900 mb-2">Configurar</h3>
                      <p className="text-gray-600 text-sm">
                        Crea tu cuenta maestra y comienza a gestionar tus contraseñas de forma segura.
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </Card>
          </div>

          {/* System Requirements */}
          <aside className="space-y-6">
            <Card>
              <div className="space-y-4">
                <h3 className="text-lg font-semibold text-gray-900">
                   Requisitos del Sistema
                </h3>
                <div className="space-y-3 text-sm">
                  <div className="flex items-center gap-2">
                    <FaCheckCircle className="w-4 h-4 text-green-600" />
                    <span className="text-gray-700">Windows 10 o superior</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <FaCheckCircle className="w-4 h-4 text-green-600" />
                    <span className="text-gray-700">64 MB RAM disponible</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <FaCheckCircle className="w-4 h-4 text-green-600" />
                    <span className="text-gray-700">100 MB espacio libre</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <FaCheckCircle className="w-4 h-4 text-green-600" />
                    <span className="text-gray-700">Conexión a internet</span>
                  </div>
                </div>
              </div>
            </Card>

            <Card>
              <div className="space-y-4">
                <h3 className="text-lg font-semibold text-gray-900">
                   Seguridad
                </h3>
                <div className="space-y-3 text-sm">
                  <div className="flex items-start gap-2">
                    <FaShieldAlt className="w-4 h-4 text-green-600 mt-0.5" />
                    <span className="text-gray-700">Código fuente abierto</span>
                  </div>
                  <div className="flex items-start gap-2">
                    <FaShieldAlt className="w-4 h-4 text-green-600 mt-0.5" />
                    <span className="text-gray-700">Sin telemetría</span>
                  </div>
                  <div className="flex items-start gap-2">
                    <FaShieldAlt className="w-4 h-4 text-green-600 mt-0.5" />
                    <span className="text-gray-700">Cifrado local</span>
                  </div>
                </div>
              </div>
            </Card>
          </aside>
        </div>

        {/* Important Information */}
        <div className="grid gap-8 lg:grid-cols-2 mb-12">
          <Card>
            <div className="flex items-start gap-3">
              <FaExclamationTriangle className="w-5 h-5 text-amber-600 mt-1 flex-shrink-0" />
              <div className="space-y-2">
                <h3 className="font-semibold text-amber-800">Información Importante</h3>
                <div className="text-sm text-amber-700 space-y-1">
                  <p>• El instalador puede generar una advertencia del antivirus (falso positivo)</p>
                  <p>• Se recomienda descargar únicamente desde este sitio oficial</p>
                  <p>• La primera ejecución puede tomar más tiempo debido a la inicialización</p>
                </div>
              </div>
            </div>
          </Card>

          <Card>
            <div className="flex items-start gap-3">
              <FaCheckCircle className="w-5 h-5 text-green-600 mt-1 flex-shrink-0" />
              <div className="space-y-2">
                <h3 className="font-semibold text-green-800">¿Qué Incluye?</h3>
                <div className="text-sm text-green-700 space-y-1">
                  <p>• Aplicación principal con interfaz moderna</p>
                  <p>• Generador de contraseñas seguras</p>
                  <p>• Importador automático de navegadores</p>
                  <p>• Documentación y guías de usuario</p>
                </div>
              </div>
            </div>
          </Card>
        </div>

        {/* Support Section */}
        <div className="grid gap-6 lg:grid-cols-3">
          <Card>
            <div className="text-center space-y-4">
              <h3 className="text-lg font-semibold text-gray-900">¿Necesitas Ayuda?</h3>
              <p className="text-sm text-gray-600">
                Nuestro equipo de soporte está disponible para ayudarte con la instalación y configuración.
              </p>
              <div className="space-y-2">
                <ButtonLink href="/marketing/contacto" variant="outline" className="w-full">
                  Contactar Soporte
                </ButtonLink>
                <ButtonLink href="/marketing/contacto" variant="ghost" className="w-full text-sm">
                  Preguntas Frecuentes
                </ButtonLink>
              </div>
            </div>
          </Card>

          <Card>
            <div className="text-center space-y-4">
              <h3 className="text-lg font-semibold text-gray-900">Recursos</h3>
              <div className="space-y-2">
                <Link href="/marketing/planes" className="block text-sm text-red-600 hover:text-red-700 underline">
                  Ver Planes y Precios
                </Link>
                <Link href="/marketing/acerca" className="block text-sm text-red-600 hover:text-red-700 underline">
                  Acerca de EncryptU
                </Link>
                <Link href="https://github.com/SiegAxel/EncryptU" target="_blank" className="block text-sm text-red-600 hover:text-red-700 underline">
                  Código Fuente (GitHub)
                </Link>
              </div>
            </div>
          </Card>

          <Card>
            <div className="text-center space-y-4">
              <h3 className="text-lg font-semibold text-gray-900">Síguenos</h3>
              <div className="flex justify-center gap-4 text-xl">
                <Link href="https://facebook.com" target="_blank" className="text-gray-600 hover:text-red-600 transition-colors">
                  <FaFacebook />
                </Link>
                <Link href="https://linkedin.com" target="_blank" className="text-gray-600 hover:text-red-600 transition-colors">
                  <FaLinkedin />
                </Link>
                <Link href="https://instagram.com" target="_blank" className="text-gray-600 hover:text-red-600 transition-colors">
                  <FaInstagram />
                </Link>
                <Link href="https://github.com/SiegAxel/EncryptU" target="_blank" className="text-gray-600 hover:text-red-600 transition-colors">
                  <FaGithub />
                </Link>
              </div>
              <p className="text-xs text-gray-500">
                Mantente al día con las últimas actualizaciones y noticias de seguridad.
              </p>
            </div>
          </Card>
        </div>
      </Container>
    </Section>
  );
}

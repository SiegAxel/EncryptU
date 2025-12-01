"use client";

import Link from "next/link";
import Section from "@/components/layout/ui/Section";
import Container from "@/components/layout/ui/Container";
import Card from "@/components/layout/ui/Card";
import ButtonLink from "@/components/layout/ui/ButtonLink";
import InstallDownloadButton from "@/components/layout/InstallDownloadButton";
import { useLatestRelease } from "@/hooks/useLatestRelease";
import { FaDownload, FaShieldAlt, FaCog, FaCheckCircle, FaExclamationTriangle, FaGithub, FaFacebook, FaLinkedin, FaInstagram, FaSpinner } from "react-icons/fa";

export default function InstalacionPage() {
  const { data: latestRelease, loading, error } = useLatestRelease();

  if (loading) {
    return (
      <Section>
        <Container>
          <div className="flex justify-center items-center min-h-[400px]">
            <div className="text-center">
              <FaSpinner className="w-8 h-8 animate-spin text-red-600 mx-auto mb-4" />
              <p className="text-gray-600">Cargando información de la última versión...</p>
            </div>
          </div>
        </Container>
      </Section>
    );
  }

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
  };

  const formatDate = (dateString: string): string => {
    return new Date(dateString).toLocaleDateString('es-ES', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

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
          {latestRelease && (
            <div className="mt-4 flex justify-center gap-4 text-sm text-gray-500">
              <span>Versión: <strong className="text-red-600">{latestRelease.version}</strong></span>
              <span>•</span>
              <span>Publicado: {formatDate(latestRelease.published_at)}</span>
              {latestRelease.download_count > 0 && (
                <>
                  <span>•</span>
                  <span>{latestRelease.download_count.toLocaleString()} descargas</span>
                </>
              )}
            </div>
          )}
          {error && (
            <div className="mt-4 p-3 bg-amber-100 border border-amber-300 rounded-lg text-amber-700 text-sm">
              ⚠️ {error} - Usando versión de respaldo
            </div>
          )}
        </div>

        {/* Sección principal de descarga */}
        <div className="grid gap-8 lg:grid-cols-2 mb-12">
          {/* Download Button */}
          <div className="flex justify-center lg:justify-end">
            <InstallDownloadButton
              installerUrl={latestRelease?.download_url || "#"}
              fileName={latestRelease?.file_name || "EncryptU-Setup.exe"}
              size={latestRelease?.file_size ? (
                typeof latestRelease.file_size === 'string' && latestRelease.file_size.includes('MB')
                  ? latestRelease.file_size
                  : formatFileSize(
                      typeof latestRelease.file_size === 'string'
                        ? parseInt(latestRelease.file_size) || 40960000
                        : latestRelease.file_size || 40960000
                    )
              ) : "39 MB"}
              version={latestRelease?.version || "v1.0.0"}
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
                        Localiza el archivo descargado ({latestRelease?.file_name || "EncryptU-Setup.exe"}) y ejecútalo como administrador.
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
                  <p>• <strong>Verificación de integridad:</strong> Hash SHA256 disponible en GitHub</p>
                  <p>• <a href={latestRelease?.html_url || "https://github.com/SiegAxel/EncryptU/releases"} target="_blank" className="underline hover:no-underline">Ver en GitHub</a> para el hash más reciente</p>
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
                {latestRelease?.html_url && (
                  <Link href={latestRelease.html_url} target="_blank" className="block text-sm text-red-600 hover:text-red-700 underline">
                    Ver Última Release
                  </Link>
                )}
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

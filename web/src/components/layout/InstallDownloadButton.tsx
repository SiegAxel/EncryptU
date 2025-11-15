"use client";

import { useState } from "react";
import { FaDownload, FaCheckCircle, FaExclamationTriangle, FaGithub, FaCode } from "react-icons/fa";

interface InstallDownloadButtonProps {
  installerUrl?: string;
  fileName?: string;
  size?: string;
  version?: string;
  className?: string;
}

export default function InstallDownloadButton({
  installerUrl = "/api/download-installer",
  fileName = "EncryptU-Setup-v1.0.0.exe",
  size = "45.2 MB",
  version = "v1.0.0",
  className = ""
}: InstallDownloadButtonProps) {
  const [downloading, setDownloading] = useState(false);
  const [downloaded, setDownloaded] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showAlternatives, setShowAlternatives] = useState(false);

  const handleDownload = async () => {
    setDownloading(true);
    setError(null);
    
    try {
      // Hacer fetch directo al endpoint API
      const response = await fetch(installerUrl);
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ message: "Error desconocido" }));
        throw new Error(errorData.message || `HTTP error! status: ${response.status}`);
      }
      
      // Crear blob del archivo
      const blob = await response.blob();
      
      // Crear URL del blob
      const blobUrl = window.URL.createObjectURL(blob);
      
      // Crear enlace de descarga
      const link = document.createElement('a');
      link.href = blobUrl;
      link.download = fileName;
      document.body.appendChild(link);
      link.click();
      
      // Limpiar
      document.body.removeChild(link);
      window.URL.revokeObjectURL(blobUrl);
      
      setDownloaded(true);
      setDownloading(false);
      
      // Reset después de 3 segundos
      setTimeout(() => setDownloaded(false), 3000);
    } catch (error) {
      console.error("Error downloading installer:", error);
      setError(error instanceof Error ? error.message : "Error desconocido");
      setShowAlternatives(true);
      setDownloading(false);
    }
  };

  return (
    <div className={`bg-white rounded-xl border border-gray-200 p-6 shadow-lg ${className}`}>
      <div className="text-center space-y-4">
        {/* Icono y título */}
        <div className="flex justify-center">
          <div className="w-16 h-16 bg-gradient-to-br from-red-500 to-red-600 rounded-xl flex items-center justify-center">
            <FaDownload className="w-8 h-8 text-white" />
          </div>
        </div>
        
        <div>
          <h3 className="text-xl font-bold text-gray-900 mb-2">
            Descargar EncryptU Desktop
          </h3>
          <p className="text-gray-600 text-sm">
            La aplicación completa de gestión de contraseñas para Windows
          </p>
        </div>

        {/* Información del archivo */}
        <div className="bg-gray-50 rounded-lg p-4 space-y-2">
          <div className="flex justify-between text-sm">
            <span className="text-gray-600">Versión:</span>
            <span className="font-medium text-gray-900">{version}</span>
          </div>
          <div className="flex justify-between text-sm">
            <span className="text-gray-600">Tamaño:</span>
            <span className="font-medium text-gray-900">{size}</span>
          </div>
          <div className="flex justify-between text-sm">
            <span className="text-gray-600">Sistema:</span>
            <span className="font-medium text-gray-900">Windows 10/11</span>
          </div>
        </div>

        {/* Error Display */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-left">
            <div className="flex items-start gap-2">
              <FaExclamationTriangle className="w-5 h-5 text-red-600 mt-0.5 flex-shrink-0" />
              <div>
                <h4 className="font-medium text-red-800 mb-2">Instalador No Disponible</h4>
                <p className="text-red-700 text-sm mb-3">{error}</p>
                <p className="text-red-600 text-xs">
                  El instalador estará disponible próximamente. Usa una de las alternativas mientras tanto.
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Botón de descarga */}
        <button
          onClick={handleDownload}
          disabled={downloading || downloaded}
          className={`w-full py-3 px-6 rounded-lg font-semibold text-white transition-all duration-300 ${
            downloaded
              ? "bg-green-600 hover:bg-green-700"
              : downloading
              ? "bg-gray-400 cursor-not-allowed"
              : error
              ? "bg-gray-500 hover:bg-gray-600"
              : "bg-gradient-to-r from-red-600 to-red-700 hover:from-red-700 hover:to-red-800 transform hover:scale-105 shadow-lg"
          }`}
        >
          <div className="flex items-center justify-center gap-2">
            {downloaded ? (
              <>
                <FaCheckCircle className="w-5 h-5" />
                ¡Descarga Iniciada!
              </>
            ) : downloading ? (
              <>
                <div className="animate-spin rounded-full h-5 w-5 border-2 border-white border-t-transparent" />
                Descargando...
              </>
            ) : error ? (
              <>
                <FaExclamationTriangle className="w-5 h-5" />
                No Disponible
              </>
            ) : (
              <>
                <FaDownload className="w-5 h-5" />
                Descargar Instalador
              </>
            )}
          </div>
        </button>

        {/* Alternativas de instalación */}
        {showAlternatives && (
          <div className="space-y-3">
            <h4 className="font-medium text-gray-900">Alternativas de Instalación:</h4>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              <button
                onClick={() => window.open('https://github.com/tu-usuario/encryptu', '_blank')}
                className="flex items-center gap-2 p-3 bg-gray-50 hover:bg-gray-100 rounded-lg border border-gray-200 transition-colors"
              >
                <FaGithub className="w-5 h-5 text-gray-600" />
                <div className="text-left">
                  <div className="font-medium text-sm text-gray-900">GitHub</div>
                  <div className="text-xs text-gray-600">Código fuente</div>
                </div>
              </button>
              
              <button
                onClick={() => {
                  // Aquí se podría abrir un diálogo con instrucciones
                  alert('Para ejecutar desde código fuente:\n\n1. Clona el repositorio\n2. Instala Python 3.8+\n3. Ejecuta: pip install -r requirements.txt\n4. Ejecuta: python desktop/__main__.py');
                }}
                className="flex items-center gap-2 p-3 bg-gray-50 hover:bg-gray-100 rounded-lg border border-gray-200 transition-colors"
              >
                <FaCode className="w-5 h-5 text-gray-600" />
                <div className="text-left">
                  <div className="font-medium text-sm text-gray-900">Ejecutar desde código</div>
                  <div className="text-xs text-gray-600">Para desarrolladores</div>
                </div>
              </button>
            </div>
          </div>
        )}

        {/* Nota de seguridad */}
        <div className="flex items-start gap-2 text-xs text-gray-500 bg-yellow-50 p-3 rounded-lg border border-yellow-200">
          <FaExclamationTriangle className="w-4 h-4 text-yellow-600 mt-0.5 flex-shrink-0" />
          <div>
            <p className="font-medium text-yellow-800">Importante:</p>
            <p>Este instalador es seguro y ha sido verificado. Se recomienda descargarlo solo desde este sitio oficial.</p>
          </div>
        </div>
      </div>
    </div>
  );
}
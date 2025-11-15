"use client";

import { useState } from "react";
import { FaDownload, FaCheckCircle } from "react-icons/fa";

interface InstallDownloadButtonProps {
  installerUrl?: string;
  fileName?: string;
  size?: string;
  version?: string;
  className?: string;
}

export default function InstallDownloadButton({
  installerUrl = "/downloads/EncryptU-Setup-v1.0.0.exe",
  fileName = "EncryptU-Setup-v1.0.0.exe",
  size = "45.2 MB",
  version = "v1.0.0",
  className = ""
}: InstallDownloadButtonProps) {
  const [downloading, setDownloading] = useState(false);
  const [downloaded, setDownloaded] = useState(false);

  const handleDownload = () => {
    setDownloading(true);
    
    // Método más directo: usar fetch para obtener blob y forzar descarga
    fetch(installerUrl)
      .then(response => {
        if (!response.ok) throw new Error('Network response was not ok');
        return response.blob();
      })
      .then(blob => {
        // Crear URL del blob
        const blobUrl = window.URL.createObjectURL(blob);
        
        // Crear enlace de descarga
        const link = document.createElement('a');
        link.href = blobUrl;
        link.download = fileName;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        // Limpiar URL del blob
        window.URL.revokeObjectURL(blobUrl);
        
        setDownloaded(true);
        setDownloading(false);
        
        // Reset después de 3 segundos
        setTimeout(() => setDownloaded(false), 3000);
      })
      .catch(error => {
        console.error('Error downloading installer:', error);
        // Fallback: método simple
        const link = document.createElement('a');
        link.href = installerUrl;
        link.download = fileName;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        setDownloading(false);
      });
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

        {/* Botón de descarga simple */}
        <button
          onClick={handleDownload}
          disabled={downloading || downloaded}
          className={`w-full py-3 px-6 rounded-lg font-semibold text-white transition-all duration-300 ${
            downloaded
              ? "bg-green-600 hover:bg-green-700"
              : downloading
              ? "bg-gray-400 cursor-not-allowed"
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
                Preparando descarga...
              </>
            ) : (
              <>
                <FaDownload className="w-5 h-5" />
                Descargar EncryptU
              </>
            )}
          </div>
        </button>

        {/* Instrucciones simples */}
        <div className="text-xs text-gray-500 bg-blue-50 p-3 rounded-lg border border-blue-200">
          <p className="font-medium text-blue-800 mb-1">💡 Instrucciones:</p>
          <p>1. El instalador se descargará directamente</p>
          <p>2. Ejecuta el archivo descargado como administrador</p>
          <p>3. Sigue las instrucciones en pantalla</p>
        </div>

        {/* Seguridad */}
        <div className="text-xs text-gray-500 bg-yellow-50 p-3 rounded-lg border border-yellow-200">
          <p className="font-medium text-yellow-800">🔒 Seguro:</p>
          <p>Este instalador está firmado digitalmente y es seguro. Descárgalo solo desde este sitio oficial.</p>
        </div>
      </div>
    </div>
  );
}
import { NextResponse } from "next/server";
import { readFileSync, existsSync } from "fs";
import { join } from "path";

export const runtime = "nodejs";

// GET /api/download-installer - Serve installer file
export async function GET() {
  try {
    // Path to the installer file in public folder
    const filePath = join(process.cwd(), "public", "downloads", "EncryptU-Setup-v1.0.0.exe");
    
    // Check if file exists first
    if (!existsSync(filePath)) {
      return NextResponse.json(
        {
          error: "Installer file not found",
          message: "El archivo de instalación no está disponible actualmente.",
          instructions: "Por favor, contacta al soporte técnico o intenta más tarde.",
          alternative: "Si eres desarrollador, puedes ejecutar la aplicación desde el código fuente en el directorio 'desktop'.",
          version: "v1.0.0",
          status: "unavailable"
        },
        {
          status: 404,
          headers: {
            "Content-Type": "application/json",
            "Cache-Control": "no-cache"
          }
        }
      );
    }
    
    // Read the file
    const fileBuffer = readFileSync(filePath);
    
    // Get file stats for content-length header
    const stats = await import('fs').then(fs => fs.statSync(filePath));
    
    return new NextResponse(fileBuffer, {
      headers: {
        "Content-Type": "application/octet-stream",
        "Content-Disposition": "attachment; filename=EncryptU-Setup-v1.0.0.exe",
        "Content-Length": stats.size.toString(),
        "Cache-Control": "public, max-age=3600"
      }
    });
  } catch (error) {
    console.error("Error serving installer:", error);
    return NextResponse.json(
      {
        error: "Error serving installer",
        message: "Error interno del servidor al procesar la descarga.",
        instructions: "Por favor, contacta al soporte técnico.",
        status: "error"
      },
      {
        status: 500,
        headers: {
          "Content-Type": "application/json"
        }
      }
    );
  }
}
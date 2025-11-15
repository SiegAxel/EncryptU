import { NextResponse } from "next/server";
import { readFileSync } from "fs";
import { join } from "path";

export const runtime = "nodejs";

// GET /api/download-installer - Serve installer file
export async function GET() {
  try {
    // Path to the installer file in public folder
    const filePath = join(process.cwd(), "public", "downloads", "EncryptU-Setup-v1.0.0.exe");
    
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
      { error: "Installer file not found" },
      { status: 404 }
    );
  }
}
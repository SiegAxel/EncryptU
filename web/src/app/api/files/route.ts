import { NextResponse } from "next/server";
import { prisma } from "@/lib/prisma";
import { verifyToken, type TokenPayload } from "@/lib/auth";
import { cookies } from "next/headers";

export const runtime = "nodejs";

// GET /api/files - List user's files
export async function GET(req: Request) {
  try {
    const cookieStore = await cookies();
    const token = cookieStore.get("auth")?.value;

    if (!token) {
      return NextResponse.json(
        { ok: false, error: "No token provided" },
        { status: 401 }
      );
    }

    // Verify JWT token
    let tokenPayload: TokenPayload;
    try {
      tokenPayload = await verifyToken<TokenPayload>(token);
    } catch {
      return NextResponse.json(
        { ok: false, error: "Invalid token" },
        { status: 401 }
      );
    }

    // Find user by email from token
    const user = await prisma.user.findUnique({
      where: { email: tokenPayload.email.toLowerCase() }
    });

    if (!user) {
      return NextResponse.json(
        { ok: false, error: "User not found" },
        { status: 404 }
      );
    }

    // Get user's files
    const files = await prisma.file.findMany({
      where: { ownerId: user.id },
      orderBy: { createdAt: 'desc' }
    });

    // Transform files to match desktop expectations
    const transformedFiles = files.map(file => {
      const filename = file.filename as string;
      const [site, username] = filename.split(' | ');
      
      return {
        id: file.id,
        site: site || filename,
        username: username || 'Usuario',
        createdAt: file.createdAt.toISOString(),
        filename: file.filename
      };
    });

    return NextResponse.json(transformedFiles);

  } catch (error) {
    console.error("Get files error:", error);
    return NextResponse.json(
      { ok: false, error: "Internal server error" },
      { status: 500 }
    );
  }
}
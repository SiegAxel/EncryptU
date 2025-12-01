import { NextResponse } from "next/server";
import { prisma } from "@/lib/prisma";
import { verifyToken, type TokenPayload } from "@/lib/auth";
import { cookies } from "next/headers";

export const runtime = "nodejs";

// GET /api/files/[id] - Download a specific file
export async function GET(req: Request, { params }: { params: Promise<{ id: string }> }) {
  try {
    const resolvedParams = await params;
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

    const fileId = parseInt(resolvedParams.id);
    if (isNaN(fileId)) {
      return NextResponse.json(
        { ok: false, error: "Invalid file ID" },
        { status: 400 }
      );
    }

    // Get the file
    const file = await prisma.file.findFirst({
      where: {
        id: fileId,
        ownerId: user.id
      }
    });

    if (!file) {
      return NextResponse.json(
        { ok: false, error: "File not found" },
        { status: 404 }
      );
    }

    // Devolver el contenido del archivo
    return new Response(file.content, {
      status: 200,
      headers: {
        'Content-Type': 'application/octet-stream',
        'Content-Disposition': `attachment; filename="${file.filename}"`
      }
    });

  } catch (error) {
    console.error("Download error:", error);
    return NextResponse.json(
      { ok: false, error: "Internal server error" },
      { status: 500 }
    );
  }
}

// DELETE /api/files/[id] - Delete a specific file
export async function DELETE(req: Request, { params }: { params: Promise<{ id: string }> }) {
  try {
    const resolvedParams = await params;
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

    const fileId = parseInt(resolvedParams.id);
    if (isNaN(fileId)) {
      return NextResponse.json(
        { ok: false, error: "Invalid file ID" },
        { status: 400 }
      );
    }

    // Delete the file
    const deletedFile = await prisma.file.deleteMany({
      where: {
        id: fileId,
        ownerId: user.id
      }
    });

    if (deletedFile.count === 0) {
      return NextResponse.json(
        { ok: false, error: "File not found" },
        { status: 404 }
      );
    }

    return NextResponse.json({ ok: true });

  } catch (error) {
    console.error("Delete error:", error);
    return NextResponse.json(
      { ok: false, error: "Internal server error" },
      { status: 500 }
    );
  }
}
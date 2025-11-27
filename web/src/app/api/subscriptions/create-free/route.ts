import { NextResponse } from "next/server";
import { prisma } from "@/lib/prisma";
import { assignFreePlanToUser } from "@/lib/subscription";

export const runtime = "nodejs";

type Body = { userId: number };
type ApiResponse = 
  | { ok: true; message: string }
  | { ok: false; error: string };

// POST /api/subscriptions/create-free - Create free subscription for existing user
export async function POST(req: Request): Promise<NextResponse<ApiResponse>> {
  try {
    const { userId } = (await req.json()) as Body;

    if (!userId || typeof userId !== "number") {
      return NextResponse.json(
        { ok: false, error: "userId es requerido" },
        { status: 400 }
      );
    }

    // Verify user exists
    const user = await prisma.user.findUnique({
      where: { id: userId },
      select: { id: true, name: true, email: true }
    });

    if (!user) {
      return NextResponse.json(
        { ok: false, error: "Usuario no encontrado" },
        { status: 404 }
      );
    }

    // Check if user already has an active subscription
    const existingSubscription = await prisma.userSubscription.findFirst({
      where: {
        userId: userId,
        status: "active"
      },
      select: { id: true, plan: { select: { name: true } } }
    });

    if (existingSubscription) {
      return NextResponse.json(
        { ok: true, message: `Usuario ya tiene plan ${existingSubscription.plan.name} activo` },
        { status: 200 }
      );
    }

    // Assign free plan
    await assignFreePlanToUser(userId);

    return NextResponse.json(
      { ok: true, message: "Plan gratuito asignado exitosamente" },
      { status: 200 }
    );

  } catch (error) {
    console.error("Error creating free subscription:", error);
    const message = error instanceof Error ? error.message : "Error interno del servidor";

    return NextResponse.json(
      { ok: false, error: message },
      { status: 500 }
    );
  }
}
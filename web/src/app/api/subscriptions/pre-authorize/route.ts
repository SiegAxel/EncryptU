import { NextResponse } from "next/server";
import { prisma } from "@/lib/prisma";
import { verifyToken, type TokenPayload } from "@/lib/auth";
import { cookies } from "next/headers";

export const runtime = "nodejs";

// Pre-authorize subscription - creates pending record before PayPal
export async function POST(req: Request) {
  try {
    const token = (await cookies()).get("auth")?.value;

    if (!token) {
      return NextResponse.json(
        { ok: false, error: "Usuario no autenticado" },
        { status: 401 }
      );
    }

    // Verify JWT token
    let tokenPayload: TokenPayload;
    try {
      tokenPayload = await verifyToken<TokenPayload>(token);
    } catch {
      return NextResponse.json(
        { ok: false, error: "Token inválido" },
        { status: 401 }
      );
    }

    const body = await req.json();
    const { planId } = body;

    if (!planId) {
      return NextResponse.json(
        { ok: false, error: "Plan ID es requerido" },
        { status: 400 }
      );
    }

    // Find user by email from token
    const user = await prisma.user.findUnique({
      where: { email: tokenPayload.email.toLowerCase() }
    });

    if (!user) {
      return NextResponse.json(
        { ok: false, error: "Usuario no encontrado" },
        { status: 404 }
      );
    }

    // Get subscription plan
    const plan = await prisma.subscriptionPlan.findUnique({
      where: { id: planId }
    });

    if (!plan || !plan.isActive) {
      return NextResponse.json(
        { ok: false, error: "Plan inválido" },
        { status: 400 }
      );
    }

    // Check if user already has an active subscription
    const existingSubscription = await prisma.userSubscription.findFirst({
      where: { 
        userId: user.id,
        status: "active"
      }
    });

    if (existingSubscription) {
      return NextResponse.json(
        { ok: false, error: "Ya tienes una suscripción activa" },
        { status: 400 }
      );
    }

    // Clean up any existing pending subscriptions for this plan
    await prisma.userSubscription.deleteMany({
      where: {
        userId: user.id,
        planId: plan.id,
        status: "pending_payment"
      }
    });

    // Create pending subscription record
    const pendingSubscription = await prisma.userSubscription.create({
      data: {
        userId: user.id,
        planId: plan.id,
        status: "pending_payment",
        startDate: new Date(),
        currency: "USD",
        metadata: {
          session_created_at: new Date().toISOString(),
          paypal_plan_id: plan.paypalPlanId,
          user_email: user.email
        }
      }
    });

    console.log(` Pre-authorized subscription ${pendingSubscription.id} for user ${user.email}`);

    return NextResponse.json({
      ok: true,
      subscriptionId: pendingSubscription.id,
      planName: plan.name,
      planPrice: plan.price.toString()
    });

  } catch (error) {
    console.error("Pre-authorize error:", error);
    return NextResponse.json(
      { ok: false, error: "Error interno del servidor" },
      { status: 500 }
    );
  }
}
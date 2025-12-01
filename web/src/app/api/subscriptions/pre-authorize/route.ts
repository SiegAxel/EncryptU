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

    // Find the user's existing subscription (they can only have one due to unique constraint)
    const existingSubscription = await prisma.userSubscription.findFirst({
      where: { userId: user.id }
    });

    let pendingSubscription;
    if (existingSubscription) {
      // Update existing subscription to new plan (upgrade/downgrade)
      pendingSubscription = await prisma.userSubscription.update({
        where: { id: existingSubscription.id },
        data: {
          planId: plan.id,
          status: "pending_payment", // Will be activated by PayPal webhook
          updatedAt: new Date(),
          metadata: {
            session_created_at: new Date().toISOString(),
            paypal_plan_id: plan.paypalPlanId,
            user_email: user.email,
            previous_plan: existingSubscription.planId
          }
        }
      });
      console.log(`🔄 Updated existing subscription ${existingSubscription.id} to plan ${plan.name}`);
    } else {
      // Crear la primera suscripción si no existe
      pendingSubscription = await prisma.userSubscription.create({
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
      console.log(`✅ Created new subscription for user ${user.email}`);
    }

    console.log(`✅ Pre-authorized subscription ${pendingSubscription.id} for user ${user.email}`);

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
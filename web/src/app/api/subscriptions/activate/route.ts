import { NextResponse } from "next/server";
import { prisma } from "@/lib/prisma";
import { verifyToken, type TokenPayload } from "@/lib/auth";
import { cookies } from "next/headers";

export const runtime = "nodejs";

// Activate subscription directly (for fake payments that don't send webhooks)
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
    const { paypalSubscriptionId, planId } = body;

    if (!paypalSubscriptionId || !planId) {
      return NextResponse.json(
        { ok: false, error: "PayPal subscription ID and plan ID are required" },
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

    // Find subscription plan
    const plan = await prisma.subscriptionPlan.findUnique({
      where: { id: planId }
    });

    if (!plan || !plan.isActive) {
      return NextResponse.json(
        { ok: false, error: "Plan inválido" },
        { status: 400 }
      );
    }

    console.log(`🚀 Activating subscription for user ${user.email} with PayPal ID ${paypalSubscriptionId}`);

    // Find existing subscription or create new one
    const existingSubscription = await prisma.userSubscription.findFirst({
      where: { userId: user.id },
      include: { plan: true }
    });

    const now = new Date();
    const nextBillingDate = new Date(now);
    nextBillingDate.setMonth(nextBillingDate.getMonth() + 1);

    if (existingSubscription) {
      // Update existing subscription
      const updatedSubscription = await prisma.userSubscription.update({
        where: { id: existingSubscription.id },
        data: {
          planId: plan.id,
          status: "active",
          paypalSubscriptionId: paypalSubscriptionId,
          startDate: now,
          nextBillingDate: nextBillingDate,
          updatedAt: now,
          metadata: {
            ...(existingSubscription.metadata as Record<string, unknown> || {}),
            client_activation: true,
            activated_at: now.toISOString(),
            paypal_plan_id: plan.paypalPlanId,
            plan_changed_from: existingSubscription.plan.name
          }
        }
      });
      console.log(`✅ Updated existing subscription ${updatedSubscription.id} to active`);
      
      return NextResponse.json({
        ok: true,
        message: "Suscripción activada exitosamente",
        subscriptionId: updatedSubscription.id,
        planName: plan.name,
        startDate: updatedSubscription.startDate,
        nextBillingDate: updatedSubscription.nextBillingDate
      });
    } else {
      // Create new subscription
      const newSubscription = await prisma.userSubscription.create({
        data: {
          userId: user.id,
          planId: plan.id,
          status: "active",
          paypalSubscriptionId: paypalSubscriptionId,
          startDate: now,
          nextBillingDate: nextBillingDate,
          currency: "USD",
          metadata: {
            client_activation: true,
            activated_at: now.toISOString(),
            paypal_plan_id: plan.paypalPlanId
          }
        }
      });
      console.log(`✅ Created new active subscription ${newSubscription.id}`);
      
      return NextResponse.json({
        ok: true,
        message: "Suscripción activada exitosamente",
        subscriptionId: newSubscription.id,
        planName: plan.name,
        startDate: newSubscription.startDate,
        nextBillingDate: newSubscription.nextBillingDate
      });
    }


  } catch (error) {
    console.error("Activation error:", error);
    return NextResponse.json(
      { ok: false, error: "Error interno del servidor" },
      { status: 500 }
    );
  }
}

// Check current subscription status
export async function GET(req: Request) {
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

    // Get current subscription
    const subscription = await prisma.userSubscription.findFirst({
      where: { userId: user.id },
      include: { plan: true }
    });

    return NextResponse.json({
      ok: true,
      subscription: subscription ? {
        id: subscription.id,
        status: subscription.status,
        planName: subscription.plan.name,
        planPrice: subscription.plan.price,
        startDate: subscription.startDate,
        nextBillingDate: subscription.nextBillingDate,
        paypalSubscriptionId: subscription.paypalSubscriptionId
      } : null
    });

  } catch (error) {
    console.error("Check subscription error:", error);
    return NextResponse.json(
      { ok: false, error: "Error interno del servidor" },
      { status: 500 }
    );
  }
}
import { NextResponse } from "next/server";
import { prisma } from "@/lib/prisma";
import { verifyToken, type TokenPayload } from "@/lib/auth";
// eslint-disable-next-line @typescript-eslint/no-unused-vars
import { requireAdmin } from "@/app/api/admin/requireAdmin";

export const runtime = "nodejs";

// GET /api/subscriptions - Get current user's subscription
export async function GET(req: Request) {
  try {
    const authHeader = req.headers.get("authorization");
    const token = authHeader?.replace("Bearer ", "");

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

    const subscription = await prisma.userSubscription.findFirst({
      where: { userId: user.id },
      include: {
        plan: true,
        user: {
          select: { id: true, name: true, email: true }
        }
      }
    });

    if (!subscription) {
      return NextResponse.json(
        { ok: false, error: "No subscription found" },
        { status: 404 }
      );
    }

    return NextResponse.json({
      ok: true,
      subscription: {
        id: subscription.id,
        status: subscription.status,
        plan: {
          id: subscription.plan.id,
          name: subscription.plan.name,
          price: subscription.plan.price.toString(),
          features: subscription.plan.features
        },
        nextBillingDate: subscription.nextBillingDate,
        amountPaid: subscription.amountPaid,
        currency: subscription.currency,
        isActive: subscription.status === "active"
      }
    });

  } catch (error) {
    console.error("Get subscription error:", error);
    return NextResponse.json(
      { ok: false, error: "Internal server error" },
      { status: 500 }
    );
  }
}

// PATCH /api/subscriptions - Upgrade/downgrade subscription
export async function PATCH(req: Request) {
  try {
    const authHeader = req.headers.get("authorization");
    const token = authHeader?.replace("Bearer ", "");

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

    const body = await req.json();
    const { planId } = body;

    if (!planId) {
      return NextResponse.json(
        { ok: false, error: "Plan ID is required" },
        { status: 400 }
      );
    }

    // Get target plan
    const targetPlan = await prisma.subscriptionPlan.findUnique({
      where: { id: planId }
    });

    if (!targetPlan || !targetPlan.isActive) {
      return NextResponse.json(
        { ok: false, error: "Invalid subscription plan" },
        { status: 400 }
      );
    }

    // Get current subscription
    const currentSubscription = await prisma.userSubscription.findFirst({
      where: { userId: user.id },
      include: { plan: true }
    });

    if (!currentSubscription) {
      return NextResponse.json(
        { ok: false, error: "No current subscription found" },
        { status: 404 }
      );
    }

    // Check if downgrading (only allowed if current plan is more expensive)
    if (targetPlan.price < currentSubscription.plan.price && currentSubscription.status === "active") {
      // For downgrades, we need to handle partial refund or end of billing cycle
      return NextResponse.json(
        { ok: false, error: "Downgrades only allowed at end of billing cycle" },
        { status: 400 }
      );
    }

    // For upgrades, activate immediately
    if (targetPlan.price > currentSubscription.plan.price) {
      await prisma.userSubscription.update({
        where: { id: currentSubscription.id },
        data: {
          planId: targetPlan.id,
          nextBillingDate: new Date(), // Immediate effect
          updatedAt: new Date()
        }
      });
    }

    const updatedSubscription = await prisma.userSubscription.findUnique({
      where: { id: currentSubscription.id },
      include: { plan: true }
    });

    return NextResponse.json({
      ok: true,
      subscription: updatedSubscription,
      message: "Subscription updated successfully"
    });

  } catch (error) {
    console.error("Update subscription error:", error);
    return NextResponse.json(
      { ok: false, error: "Internal server error" },
      { status: 500 }
    );
  }
}
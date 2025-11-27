import { NextResponse } from "next/server";
import { prisma } from "@/lib/prisma";

export const runtime = "nodejs";

// Debug endpoint to manually activate stuck subscriptions
export async function GET(req: Request) {
  const { searchParams } = new URL(req.url);
  const userEmail = searchParams.get("email");
  
  if (!userEmail) {
    return NextResponse.json(
      { ok: false, error: "Email parameter required" },
      { status: 400 }
    );
  }
  
  try {
    console.log(`🔧 Manual activation requested for: ${userEmail}`);
    
    // Find user
    const user = await prisma.user.findUnique({
      where: { email: userEmail.toLowerCase() }
    });
    
    if (!user) {
      return NextResponse.json(
        { ok: false, error: "User not found" },
        { status: 404 }
      );
    }
    
    // Find pending subscription
    const subscription = await prisma.userSubscription.findFirst({
      where: {
        userId: user.id,
        status: { in: ["pending_payment", "pending"] }
      },
      orderBy: {
        createdAt: 'desc'
      },
      include: { plan: true }
    });
    
    if (!subscription) {
      return NextResponse.json(
        { ok: false, error: "No pending subscription found" },
        { status: 404 }
      );
    }
    
    // Calculate next billing date
    const now = new Date();
    const nextBillingDate = new Date(now);
    nextBillingDate.setMonth(nextBillingDate.getMonth() + 1);
    
    // Activate subscription
    await prisma.userSubscription.update({
      where: { id: subscription.id },
      data: {
        status: "active",
        startDate: now,
        nextBillingDate: nextBillingDate,
        updatedAt: now,
        metadata: {
          ...(subscription.metadata as Record<string, unknown> || {}),
          manual_activation: true,
          activated_by_debug: true,
          activated_at: now.toISOString()
        }
      }
    });
    
    console.log(`✅ Manually activated subscription ${subscription.id} for ${user.email}`);
    
    return NextResponse.json({
      ok: true,
      message: `Subscription ${subscription.id} activated successfully`,
      subscriptionId: subscription.id,
      planName: subscription.plan.name,
      activationTime: now.toISOString()
    });
    
  } catch (error) {
    console.error("Manual activation error:", error);
    return NextResponse.json(
      { ok: false, error: "Internal server error" },
      { status: 500 }
    );
  }
}

// Debug endpoint to list pending subscriptions and test PayPal events locally
export async function POST(req: Request) {
  try {
    const body = await req.json();
    const { action } = body;
    
    if (action === "list_pending") {
      const pendingSubscriptions = await prisma.userSubscription.findMany({
        where: {
          status: { in: ["pending_payment", "pending"] }
        },
        include: {
          user: true,
          plan: true
        },
        orderBy: {
          createdAt: 'desc'
        }
      });
      
      return NextResponse.json({
        ok: true,
        pendingSubscriptions: pendingSubscriptions.map(sub => ({
          id: sub.id,
          userEmail: sub.user.email,
          planName: sub.plan.name,
          status: sub.status,
          createdAt: sub.createdAt,
          metadata: sub.metadata
        }))
      });
    }
    
    // Default action: Log PayPal webhook debug info
    console.log("=== PAYPAL WEBHOOK DEBUG ===");
    console.log("Raw request body:", JSON.stringify(body, null, 2));
    
    // Check subscription plans in database
    const plans = await prisma.subscriptionPlan.findMany();
    console.log("Available plans in database:", plans.map(p => ({
      id: p.id,
      name: p.name,
      paypalPlanId: p.paypalPlanId,
      price: p.price
    })));
    
    // Check users
    const users = await prisma.user.findMany({
      select: { id: true, email: true, name: true }
    });
    console.log("Users in database:", users);
    
    // Check existing subscriptions
    const subscriptions = await prisma.userSubscription.findMany({
      include: {
        user: { select: { email: true, name: true }},
        plan: { select: { name: true, paypalPlanId: true }}
      }
    });
    console.log("Existing subscriptions:", subscriptions);
    
    return NextResponse.json({
      ok: true,
      message: "Debug info logged to console",
      plans: plans.length,
      users: users.length,
      subscriptions: subscriptions.length
    });
    
  } catch (error) {
    console.error("Debug endpoint error:", error);
    return NextResponse.json(
      { ok: false, error: error instanceof Error ? error.message : 'Unknown error' },
      { status: 500 }
    );
  }
}
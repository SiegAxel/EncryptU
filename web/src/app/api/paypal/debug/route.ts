import { NextResponse } from "next/server";
import { prisma } from "@/lib/prisma";

export const runtime = "nodejs";

// Debug endpoint to test PayPal webhook events locally
export async function POST(req: Request) {
  try {
    const body = await req.json();
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
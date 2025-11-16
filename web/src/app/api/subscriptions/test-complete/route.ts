import { NextResponse } from "next/server";
import { prisma } from "@/lib/prisma";

export const runtime = "nodejs";

// Test endpoint to manually complete all missing fields
export async function POST(req: Request) {
  try {
    const body = await req.json();
    const { subscriptionId } = body;
    
    if (!subscriptionId) {
      return NextResponse.json(
        { ok: false, error: "Subscription ID is required" },
        { status: 400 }
      );
    }
    
    console.log(` Testing complete subscription data for ID: ${subscriptionId}`);
    
    const now = new Date();
    
    // Update subscription with all missing fields
    const updatedSubscription = await prisma.userSubscription.update({
      where: { id: subscriptionId },
      data: {
        paypalCustomerId: "TEST-CUSTOMER-" + subscriptionId,
        lastPaymentDate: now,
        amountPaid: 19.99,
        updatedAt: now,
        metadata: {
          test_completion: true,
          completed_at: now.toISOString()
        }
      }
    });
    
    console.log(` Subscription ${subscriptionId} updated with complete data`);
    
    return NextResponse.json({
      ok: true,
      message: "Subscription updated with complete data",
      subscription: {
        id: updatedSubscription.id,
        status: updatedSubscription.status,
        paypalCustomerId: updatedSubscription.paypalCustomerId,
        lastPaymentDate: updatedSubscription.lastPaymentDate,
        amountPaid: updatedSubscription.amountPaid,
        updatedAt: updatedSubscription.updatedAt
      }
    });
    
  } catch (error) {
    console.error("Test completion error:", error);
    return NextResponse.json(
      { ok: false, error: error instanceof Error ? error.message : 'Unknown error' },
      { status: 500 }
    );
  }
}
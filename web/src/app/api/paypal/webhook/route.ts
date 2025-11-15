import { NextResponse } from "next/server";
import { prisma } from "@/lib/prisma";

export const runtime = "nodejs";

interface PayPalWebhookEvent {
  event_type: string;
  resource: {
    id: string;
    status: string;
    subscriber: {
      email_address: string;
      payer_id: string;
    };
    plan_id: string;
    start_time: string;
    update_time: string;
    amount: {
      value: string;
      currency_code: string;
    };
  };
}

export async function POST(req: Request) {
  try {
    const event = await req.json() as PayPalWebhookEvent;
    
    switch (event.event_type) {
      case "BILLING.SUBSCRIPTION.CREATED":
        await handleSubscriptionCreated(event.resource);
        break;
      
      case "BILLING.SUBSCRIPTION.ACTIVATED":
        await handleSubscriptionActivated(event.resource);
        break;
      
      case "BILLING.SUBSCRIPTION.CANCELLED":
        await handleSubscriptionCancelled(event.resource);
        break;
      
      case "BILLING.SUBSCRIPTION.SUSPENDED":
        await handleSubscriptionSuspended(event.resource);
        break;
      
      case "BILLING.SUBSCRIPTION.EXPIRED":
        await handleSubscriptionExpired(event.resource);
        break;
      
      case "PAYMENT.SALE.COMPLETED":
        await handlePaymentCompleted(event.resource);
        break;
      
      default:
        console.log(`Unhandled PayPal event: ${event.event_type}`);
    }

    return NextResponse.json({ ok: true });
  } catch (error) {
    console.error("PayPal webhook error:", error);
    return NextResponse.json(
      { error: "Webhook processing failed" },
      { status: 500 }
    );
  }
}

async function handleSubscriptionCreated(resource: any) {
  // Find user by PayPal customer email
  const user = await prisma.user.findUnique({
    where: { email: resource.subscriber.email_address.toLowerCase() }
  });

  if (!user) {
    console.error("User not found for email:", resource.subscriber.email_address);
    return;
  }

  // Find subscription plan by PayPal plan ID
  const plan = await prisma.subscriptionPlan.findUnique({
    where: { paypalPlanId: resource.plan_id }
  });

  if (!plan) {
    console.error("Plan not found for PayPal plan ID:", resource.plan_id);
    return;
  }

  // Create user subscription
  await prisma.userSubscription.create({
    data: {
      userId: user.id,
      planId: plan.id,
      paypalSubscriptionId: resource.id,
      paypalCustomerId: resource.subscriber.payer_id,
      status: "pending",
      startDate: new Date(resource.start_time),
      metadata: { paypal_plan_id: resource.plan_id }
    }
  });
}

async function handleSubscriptionActivated(resource: any) {
  await prisma.userSubscription.updateMany({
    where: { paypalSubscriptionId: resource.id },
    data: {
      status: "active",
      nextBillingDate: new Date(resource.billing_info.next_billing_time),
      updatedAt: new Date()
    }
  });
}

async function handleSubscriptionCancelled(resource: any) {
  await prisma.userSubscription.updateMany({
    where: { paypalSubscriptionId: resource.id },
    data: {
      status: "cancelled",
      endDate: new Date(),
      updatedAt: new Date()
    }
  });
}

async function handleSubscriptionSuspended(resource: any) {
  await prisma.userSubscription.updateMany({
    where: { paypalSubscriptionId: resource.id },
    data: {
      status: "suspended",
      updatedAt: new Date()
    }
  });
}

async function handleSubscriptionExpired(resource: any) {
  await prisma.userSubscription.updateMany({
    where: { paypalSubscriptionId: resource.id },
    data: {
      status: "expired",
      endDate: new Date(),
      updatedAt: new Date()
    }
  });
}

async function handlePaymentCompleted(resource: any) {
  await prisma.userSubscription.updateMany({
    where: { paypalSubscriptionId: resource.billing_agreement_id },
    data: {
      lastPaymentDate: new Date(resource.create_time),
      amountPaid: parseFloat(resource.amount.total),
      nextBillingDate: new Date(resource.next_payment_date),
      updatedAt: new Date()
    }
  });
}
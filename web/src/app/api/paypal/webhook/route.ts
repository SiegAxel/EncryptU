import { NextResponse } from "next/server";
import { prisma } from "@/lib/prisma";

export const runtime = "nodejs";

interface PayPalWebhookEvent {
  event_type: string;
  resource: Record<string, any>;
  id: string;
  create_time: string;
}

interface PayPalSubscriptionResource {
  id: string;
  status: string;
  status_change_note?: string;
  subscriber: {
    email_address: string;
    payer_id: string;
  };
  plan_id: string;
  start_time: string;
  update_time: string;
  billing_info?: {
    next_billing_time: string;
  };
  amount?: {
    value: string;
    currency_code: string;
  };
}

interface PayPalPaymentSaleResource {
  id: string;
  billing_agreement_id: string;
  amount: {
    total: string;
    currency: string;
  };
  create_time: string;
  next_payment_date?: string;
  parent_payment?: string;
}

export async function POST(req: Request) {
  try {
    const event = await req.json() as PayPalWebhookEvent;
    console.log(`Received PayPal webhook event: ${event.event_type}`, { eventId: event.id, createTime: event.create_time });
    
    switch (event.event_type) {
      case "BILLING.SUBSCRIPTION.CREATED":
        if ('subscriber' in event.resource) {
          await handleSubscriptionCreated(event.resource as PayPalSubscriptionResource);
        }
        break;
      
      case "BILLING.SUBSCRIPTION.ACTIVATED":
        if ('subscriber' in event.resource) {
          await handleSubscriptionActivated(event.resource as PayPalSubscriptionResource);
        }
        break;
      
      case "BILLING.SUBSCRIPTION.CANCELLED":
        if ('subscriber' in event.resource) {
          await handleSubscriptionCancelled(event.resource as PayPalSubscriptionResource);
        }
        break;
      
      case "BILLING.SUBSCRIPTION.SUSPENDED":
        if ('subscriber' in event.resource) {
          await handleSubscriptionSuspended(event.resource as PayPalSubscriptionResource);
        }
        break;
      
      case "BILLING.SUBSCRIPTION.EXPIRED":
        if ('subscriber' in event.resource) {
          await handleSubscriptionExpired(event.resource as PayPalSubscriptionResource);
        }
        break;
      
      case "PAYMENT.SALE.COMPLETED":
        if ('billing_agreement_id' in event.resource) {
          await handlePaymentCompleted(event.resource as PayPalPaymentSaleResource);
        }
        break;
      
      case "BILLING.SUBSCRIPTION.PAYMENT.FAILED":
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        console.log("Payment failed for subscription:", event.resource?.id);
        break;
      
      default:
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        console.log(`Unhandled PayPal event: ${event.event_type}`, event.resource);
    }

    return NextResponse.json({ ok: true });
  } catch (error) {
    console.error("PayPal webhook error:", error);
    return NextResponse.json(
      { error: "Webhook processing failed", message: error instanceof Error ? error.message : 'Unknown error' },
      { status: 500 }
    );
  }
}

async function handleSubscriptionCreated(resource: PayPalSubscriptionResource) {
  console.log(`Creating subscription for PayPal subscription ${resource.id}`);
  
  try {
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

    // Check if subscription already exists (idempotency)
    const existingSubscription = await prisma.userSubscription.findFirst({
      where: { paypalSubscriptionId: resource.id }
    });

    if (existingSubscription) {
      console.log(`Subscription ${resource.id} already exists, skipping creation`);
      return;
    }

    // Create user subscription
    const subscription = await prisma.userSubscription.create({
      data: {
        userId: user.id,
        planId: plan.id,
        paypalSubscriptionId: resource.id,
        paypalCustomerId: resource.subscriber.payer_id,
        status: "pending",
        startDate: new Date(resource.start_time),
        metadata: {
          paypal_plan_id: resource.plan_id,
          subscriber_email: resource.subscriber.email_address
        },
        currency: resource.amount?.currency_code || "USD"
      }
    });
    
    console.log(`Created subscription ${subscription.id} for user ${user.id} (${user.email})`);
  } catch (error) {
    console.error(`Failed to create subscription for resource ${resource.id}:`, error);
  }
}

async function handleSubscriptionActivated(resource: PayPalSubscriptionResource) {
  console.log(`Activating subscription ${resource.id} for plan ${resource.plan_id}`);
  
  try {
    // Get the subscription to calculate proper billing cycle
    const subscription = await prisma.userSubscription.findFirst({
      where: { paypalSubscriptionId: resource.id },
      include: { plan: true }
    });
    
    if (!subscription) {
      console.error(`Subscription ${resource.id} not found in database`);
      return;
    }
    
    // Calculate next billing date for immediate monthly access
    const now = new Date();
    let nextBillingDate: Date;
    
    // If PayPal provides next billing time, use it; otherwise calculate from start date
    if (resource.billing_info?.next_billing_time) {
      nextBillingDate = new Date(resource.billing_info.next_billing_time);
    } else {
      // Calculate next billing date based on subscription start date
      const startDate = subscription.startDate;
      
      // If start date is in the past, calculate next billing from now
      if (startDate <= now) {
        // For immediate activation, start billing cycle from now
        nextBillingDate = new Date(now);
        nextBillingDate.setMonth(nextBillingDate.getMonth() + 1);
      } else {
        // If future start date, use it as next billing
        nextBillingDate = startDate;
      }
    }
    
    // Update subscription with immediate activation and proper billing cycle
    await prisma.userSubscription.updateMany({
      where: { paypalSubscriptionId: resource.id },
      data: {
        status: "active",
        startDate: now, // Immediate access from activation time
        nextBillingDate: nextBillingDate,
        updatedAt: now
      }
    });
    
    console.log(`Successfully activated subscription ${resource.id} with immediate access. Next billing: ${nextBillingDate.toISOString()}`);
  } catch (error) {
    console.error(`Failed to activate subscription ${resource.id}:`, error);
  }
}

async function handleSubscriptionCancelled(resource: PayPalSubscriptionResource) {
  await prisma.userSubscription.updateMany({
    where: { paypalSubscriptionId: resource.id },
    data: {
      status: "cancelled",
      endDate: new Date(),
      updatedAt: new Date()
    }
  });
}

async function handleSubscriptionSuspended(resource: PayPalSubscriptionResource) {
  await prisma.userSubscription.updateMany({
    where: { paypalSubscriptionId: resource.id },
    data: {
      status: "suspended",
      updatedAt: new Date()
    }
  });
}

async function handleSubscriptionExpired(resource: PayPalSubscriptionResource) {
  await prisma.userSubscription.updateMany({
    where: { paypalSubscriptionId: resource.id },
    data: {
      status: "expired",
      endDate: new Date(),
      updatedAt: new Date()
    }
  });
}

async function handlePaymentCompleted(resource: PayPalPaymentSaleResource) {
  console.log(`Processing payment completed for sale: ${resource.id}`);
  
  try {
    // For subscription payments, the billing_agreement_id contains the subscription ID
    const subscriptionId = resource.billing_agreement_id || resource.parent_payment;
    
    if (!subscriptionId) {
      console.error("No subscription ID found in payment resource:", resource);
      return;
    }
    
    const result = await prisma.userSubscription.updateMany({
      where: { paypalSubscriptionId: subscriptionId },
      data: {
        lastPaymentDate: new Date(resource.create_time),
        amountPaid: parseFloat(resource.amount.total),
        currency: resource.amount.currency || "USD",
        nextBillingDate: resource.next_payment_date
          ? new Date(resource.next_payment_date)
          : undefined,
        updatedAt: new Date()
      }
    });
    
    console.log(`Updated ${result.count} subscription(s) for payment ${resource.id}`);
    
    if (result.count === 0) {
      console.warn(`No subscription found for PayPal subscription ID: ${subscriptionId}`);
    }
  } catch (error) {
    console.error(`Failed to process payment completed for resource ${resource.id}:`, error);
  }
}
import { NextResponse } from "next/server";
import { prisma } from "@/lib/prisma";

export const runtime = "nodejs";

interface PayPalWebhookEvent {
  event_type: string;
  resource: PayPalSubscriptionResource | PayPalPaymentSaleResource | Record<string, unknown>;
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
        if ('subscriber' in event.resource) {
          await handleSubscriptionPaymentFailed(event.resource as PayPalSubscriptionResource);
        }
        break;
      
      default:
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
  console.log(` Handling subscription created: ${resource.id}`);
  console.log(` PayPal email: ${resource.subscriber.email_address}`);
  
  try {
    // Find subscription plan
    const plan = await prisma.subscriptionPlan.findUnique({
      where: { paypalPlanId: resource.plan_id }
    });

    if (!plan) {
      console.error("Plan not found for PayPal plan ID:", resource.plan_id);
      return;
    }

    console.log(` Plan: ${plan.name} (${plan.price})`);

    // Look for recent pending subscriptions for this plan (user started the process)
    const now = new Date();
    const tenMinutesAgo = new Date(now.getTime() - 10 * 60 * 1000); // 10 minutes ago
    
    const recentSubscription = await prisma.userSubscription.findFirst({
      where: {
        planId: plan.id,
        status: "pending_payment",
        createdAt: {
          gte: tenMinutesAgo
        }
      },
      orderBy: {
        createdAt: 'desc' // Most recent first
      },
      include: {
        user: true
      }
    });

    if (recentSubscription) {
      console.log(` Found matching pending subscription: ${recentSubscription.id}`);
      console.log(` User: ${recentSubscription.user.email}`);
      
      // Update the pending subscription with PayPal details
      const updatedSubscription = await prisma.userSubscription.update({
        where: { id: recentSubscription.id },
        data: {
          paypalSubscriptionId: resource.id,
          paypalCustomerId: resource.subscriber.payer_id,
          status: "pending",
          metadata: {
            ...(recentSubscription.metadata as Record<string, unknown> || {}),
            paypal_subscription_created: true,
            subscriber_email: resource.subscriber.email_address,
            paypal_payer_id: resource.subscriber.payer_id,
            updated_at: new Date().toISOString()
          }
        }
      });

      console.log(` Updated subscription ${updatedSubscription.id} with PayPal ID ${resource.id}`);
    } else {
      // No matching pending subscription found
      console.log(" No matching pending subscription found");
      console.log(" This could mean:");
      console.log("   - User wasn't logged in when they clicked PayPal");
      console.log("   - User already has active subscription");
      console.log("   - Subscription was already processed");
    }
    
  } catch (error) {
    console.error(` Failed to handle subscription creation ${resource.id}:`, error);
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

async function handleSubscriptionPaymentFailed(resource: PayPalSubscriptionResource) {
  console.log(`Payment failed for subscription ${resource.id} - reverting to previous plan`);
  
  try {
    // Find the subscription that failed
    const subscription = await prisma.userSubscription.findFirst({
      where: { paypalSubscriptionId: resource.id },
      include: { plan: true }
    });
    
    if (!subscription) {
      console.error(`Subscription ${resource.id} not found for payment failure`);
      return;
    }
    
    // Get the previous plan from metadata
    const metadata = subscription.metadata as Record<string, unknown> || {};
    const previousPlanId = metadata.previous_plan;
    
    if (previousPlanId) {
      // Revert to previous plan
      const previousPlan = await prisma.subscriptionPlan.findUnique({
        where: { id: previousPlanId as number }
      });
      
      if (previousPlan) {
        await prisma.userSubscription.update({
          where: { id: subscription.id },
          data: {
            planId: previousPlanId as number,
            status: "active", // Revert to active status
            endDate: null, // Clear end date
            updatedAt: new Date(),
            metadata: {
              ...metadata,
              payment_failed: true,
              reverted_to_plan: previousPlan.name,
              failed_at: new Date().toISOString()
            }
          }
        });
        
        console.log(`✅ Reverted subscription ${subscription.id} to previous plan: ${previousPlan.name}`);
      } else {
        console.error(`Previous plan ${previousPlanId} not found`);
      }
    } else {
      console.log(`No previous plan found in metadata for subscription ${subscription.id}, keeping current plan`);
      // If no previous plan, just mark as active again (shouldn't happen with proper flow)
      await prisma.userSubscription.update({
        where: { id: subscription.id },
        data: {
          status: "active",
          updatedAt: new Date(),
          metadata: {
            ...metadata,
            payment_failed: true,
            failed_at: new Date().toISOString()
          }
        }
      });
    }
  } catch (error) {
    console.error(`Failed to handle payment failure for subscription ${resource.id}:`, error);
  }
}
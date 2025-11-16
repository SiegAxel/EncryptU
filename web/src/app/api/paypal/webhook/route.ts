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
    // Enhanced logging for debugging
    const headers = Object.fromEntries(req.headers.entries());
    console.log('📨 PayPal Webhook Headers:', {
      'user-agent': headers['user-agent'],
      'content-type': headers['content-type'],
      'paypal-transmission-sig': headers['paypal-transmission-sig'] ? 'present' : 'missing',
      'paypal-transmission-time': headers['paypal-transmission-time'] || 'missing',
      'paypal-cert-url': headers['paypal-cert-url'] || 'missing',
      'paypal-auth-algo': headers['paypal-auth-algo'] || 'missing'
    });

    const event = await req.json() as PayPalWebhookEvent;
    console.log(`🔔 Received PayPal webhook event: ${event.event_type}`, {
      eventId: event.id,
      createTime: event.create_time,
      resourceType: typeof event.resource
    });

    // Verify webhook authenticity (PayPal recommends this for production)
    const transmissionSig = headers['paypal-transmission-sig'];
    const transmissionTime = headers['paypal-transmission-time'];
    const certUrl = headers['paypal-cert-url'];
    const authAlgo = headers['paypal-auth-algo'];

    if (transmissionSig && transmissionTime && certUrl && authAlgo) {
      console.log('✅ Webhook appears to be from PayPal (has verification headers)');
      // In production, you should verify this signature with PayPal's webhook verification API
    } else {
      console.log('⚠️  Webhook verification headers missing - this should be fixed for production');
    }
    
    let handled = false;
    
    switch (event.event_type) {
      case "BILLING.SUBSCRIPTION.CREATED":
        console.log(' Handling BILLING.SUBSCRIPTION.CREATED');
        if ('subscriber' in event.resource) {
          await handleSubscriptionCreated(event.resource as PayPalSubscriptionResource);
          handled = true;
        }
        break;
      
      case "BILLING.SUBSCRIPTION.ACTIVATED":
        console.log(' Handling BILLING.SUBSCRIPTION.ACTIVATED');
        if ('subscriber' in event.resource) {
          await handleSubscriptionActivated(event.resource as PayPalSubscriptionResource);
          handled = true;
        }
        break;
      
      case "BILLING.SUBSCRIPTION.CANCELLED":
        console.log(' Handling BILLING.SUBSCRIPTION.CANCELLED');
        if ('subscriber' in event.resource) {
          await handleSubscriptionCancelled(event.resource as PayPalSubscriptionResource);
          handled = true;
        }
        break;
      
      case "BILLING.SUBSCRIPTION.SUSPENDED":
        console.log('⏸  Handling BILLING.SUBSCRIPTION.SUSPENDED');
        if ('subscriber' in event.resource) {
          await handleSubscriptionSuspended(event.resource as PayPalSubscriptionResource);
          handled = true;
        }
        break;
      
      case "BILLING.SUBSCRIPTION.EXPIRED":
        console.log('⏰ Handling BILLING.SUBSCRIPTION.EXPIRED');
        if ('subscriber' in event.resource) {
          await handleSubscriptionExpired(event.resource as PayPalSubscriptionResource);
          handled = true;
        }
        break;
      
      case "PAYMENT.SALE.COMPLETED":
        console.log('💳 Handling PAYMENT.SALE.COMPLETED');
        if ('billing_agreement_id' in event.resource) {
          await handlePaymentCompleted(event.resource as PayPalPaymentSaleResource);
          handled = true;
        }
        break;
      
      case "BILLING.SUBSCRIPTION.PAYMENT.FAILED":
        console.log('❌ Handling BILLING.SUBSCRIPTION.PAYMENT.FAILED');
        if ('subscriber' in event.resource) {
          await handleSubscriptionPaymentFailed(event.resource as PayPalSubscriptionResource);
          handled = true;
        }
        break;
      
      default:
        console.log(`❓ Unhandled PayPal event: ${event.event_type}`);
        console.log('📋 Full event data:', JSON.stringify(event, null, 2));
    }

    console.log(`🎯 Webhook processing ${handled ? 'completed successfully' : 'no action taken'}`);
    
    // Always return 200 OK to prevent PayPal from retrying
    return NextResponse.json({
      ok: true,
      message: handled ? 'Event processed' : 'Event ignored',
      eventType: event.event_type
    });
    
  } catch (error) {
    console.error('💥 PayPal webhook error:', error);
    console.error('📊 Error details:', {
      name: error instanceof Error ? error.name : 'Unknown',
      message: error instanceof Error ? error.message : String(error),
      stack: error instanceof Error ? error.stack : undefined
    });
    
    // Return 200 anyway to prevent retries, but log the error
    return NextResponse.json({
      ok: false,
      error: "Webhook processing failed",
      message: error instanceof Error ? error.message : 'Unknown error',
      timestamp: new Date().toISOString()
    });
  }
}

async function handleSubscriptionCreated(resource: PayPalSubscriptionResource) {
  console.log(`🔔 Handling subscription created: ${resource.id}`);
  console.log(`📧 PayPal email: ${resource.subscriber.email_address}`);
  
  try {
    // Find subscription plan
    const plan = await prisma.subscriptionPlan.findUnique({
      where: { paypalPlanId: resource.plan_id }
    });

    if (!plan) {
      console.error(`❌ Plan not found for PayPal plan ID: ${resource.plan_id}`);
      return;
    }

    console.log(`📋 Plan: ${plan.name} (${plan.price})`);

    // Enhanced search strategy - try multiple approaches
    let subscription = null;
    
    // Strategy 1: Look for pending subscription by plan and recent timeframe
    const now = new Date();
    const oneHourAgo = new Date(now.getTime() - 60 * 60 * 1000); // 1 hour instead of 10 minutes
    
    console.log(`🔍 Searching for pending subscription (plan ${plan.id}, last hour)`);
    
    subscription = await prisma.userSubscription.findFirst({
      where: {
        planId: plan.id,
        status: "pending_payment",
        createdAt: {
          gte: oneHourAgo
        }
      },
      orderBy: {
        createdAt: 'desc' // Most recent first
      },
      include: {
        user: true
      }
    });

    // Strategy 2: If not found, search by any pending subscription for this user
    if (!subscription && resource.subscriber?.email_address) {
      console.log(`🔍 Trying alternate search by user email`);
      
      const user = await prisma.user.findUnique({
        where: { email: resource.subscriber.email_address.toLowerCase() }
      });
      
      if (user) {
        subscription = await prisma.userSubscription.findFirst({
          where: {
            userId: user.id,
            status: "pending_payment"
          },
          orderBy: {
            createdAt: 'desc'
          },
          include: {
            user: true
          }
        });
      }
    }

    // Strategy 3: If still not found, look for any active subscription and update it
    if (!subscription && resource.subscriber?.email_address) {
      console.log(`🔍 Final attempt: searching for active subscription to upgrade`);
      
      const user = await prisma.user.findUnique({
        where: { email: resource.subscriber.email_address.toLowerCase() }
      });
      
      if (user) {
        subscription = await prisma.userSubscription.findFirst({
          where: {
            userId: user.id,
            status: "active"
          },
          include: {
            user: true,
            plan: true
          }
        });
        
        if (subscription) {
          console.log(`📝 Found active subscription ${subscription.id} (${subscription.plan.name}) - will upgrade to ${plan.name}`);
        }
      }
    }

    if (subscription) {
      console.log(`✅ Found matching subscription: ${subscription.id}`);
      console.log(`👤 User: ${subscription.user.email}`);
      
      // Update the subscription with PayPal details
      const updatedSubscription = await prisma.userSubscription.update({
        where: { id: subscription.id },
        data: {
          paypalSubscriptionId: resource.id,
          paypalCustomerId: resource.subscriber.payer_id,
          status: "pending", // Will be activated by the ACTIVATED event
          metadata: {
            ...(subscription.metadata as Record<string, unknown> || {}),
            paypal_subscription_created: true,
            subscriber_email: resource.subscriber.email_address,
            paypal_payer_id: resource.subscriber.payer_id,
            updated_at: new Date().toISOString()
          }
        }
      });

      console.log(`🔄 Updated subscription ${updatedSubscription.id} with PayPal ID ${resource.id}`);
    } else {
      console.log(`⚠️  No matching subscription found`);
      console.log(`   Possible reasons:`);
      console.log(`   - User wasn't logged in during pre-authorize`);
      console.log(`   - Subscription already processed`);
      console.log(`   - Timing issue (pre-authorize too long ago)`);
      console.log(`   - Database cleanup removed the record`);
      
      // Create a new subscription record if we have user info
      if (resource.subscriber?.email_address) {
        const user = await prisma.user.findUnique({
          where: { email: resource.subscriber.email_address.toLowerCase() }
        });
        
        if (user) {
          console.log(`➕ Creating new subscription record for user ${user.email}`);
          
          const newSubscription = await prisma.userSubscription.create({
            data: {
              userId: user.id,
              planId: plan.id,
              status: "pending",
              startDate: new Date(),
              paypalSubscriptionId: resource.id,
              paypalCustomerId: resource.subscriber.payer_id,
              currency: "USD",
              metadata: {
                paypal_subscription_created: true,
                subscriber_email: resource.subscriber.email_address,
                paypal_payer_id: resource.subscriber.payer_id,
                created_via_webhook: true,
                created_at: new Date().toISOString()
              }
            }
          });
          
          console.log(`✅ Created new subscription ${newSubscription.id}`);
        } else {
          console.log(`❌ User not found in database: ${resource.subscriber.email_address}`);
        }
      }
    }
    
  } catch (error) {
    console.error(`❌ Failed to handle subscription creation ${resource.id}:`, error);
  }
}

async function handleSubscriptionActivated(resource: PayPalSubscriptionResource) {
  console.log(`Activating subscription ${resource.id} for plan ${resource.plan_id}`);
  
  try {
    let subscription = null;
    
    // Strategy 1: Try to find by PayPal subscription ID first
    subscription = await prisma.userSubscription.findFirst({
      where: { paypalSubscriptionId: resource.id },
      include: { plan: true }
    });
    
    // Strategy 2: If not found, search by user email and plan ID (more robust for fake payments)
    if (!subscription && resource.subscriber?.email_address) {
      console.log(`🔍 Strategy 2: Finding subscription by user email ${resource.subscriber.email_address}`);
      
      // Find the plan
      const plan = await prisma.subscriptionPlan.findUnique({
        where: { paypalPlanId: resource.plan_id }
      });
      
      if (plan) {
        // Find user by email
        const user = await prisma.user.findUnique({
          where: { email: resource.subscriber.email_address.toLowerCase() }
        });
        
        if (user) {
          // Look for pending subscription for this user and plan
          subscription = await prisma.userSubscription.findFirst({
            where: {
              userId: user.id,
              planId: plan.id,
              status: { in: ["pending_payment", "pending"] }
            },
            orderBy: {
              createdAt: 'desc'
            },
            include: { plan: true }
          });
        }
      }
    }
    
    // Strategy 3: If still not found, look for any pending subscription for this user
    if (!subscription && resource.subscriber?.email_address) {
      console.log(`🔍 Strategy 3: Finding any pending subscription for user`);
      
      const user = await prisma.user.findUnique({
        where: { email: resource.subscriber.email_address.toLowerCase() }
      });
      
      if (user) {
        subscription = await prisma.userSubscription.findFirst({
          where: {
            userId: user.id,
            status: { in: ["pending_payment", "pending"] }
          },
          orderBy: {
            createdAt: 'desc'
          },
          include: { plan: true }
        });
      }
    }
    
    if (!subscription) {
      console.error(`❌ No matching subscription found for activation ${resource.id} (${resource.subscriber?.email_address})`);
      return;
    }
    
    console.log(`✅ Found subscription to activate: ${subscription.id} (status: ${subscription.status})`);
    
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
    
    // Update subscription with PayPal details and activation
    await prisma.userSubscription.update({
      where: { id: subscription.id },
      data: {
        paypalSubscriptionId: resource.id,
        paypalCustomerId: resource.subscriber.payer_id,
        status: "active",
        startDate: now, // Immediate access from activation time
        nextBillingDate: nextBillingDate,
        updatedAt: now,
        metadata: {
          ...(subscription.metadata as Record<string, unknown> || {}),
          activated_at: now.toISOString(),
          paypal_plan_id: resource.plan_id,
          activation_webhook_received: true
        }
      }
    });
    
    console.log(`🎉 Successfully activated subscription ${subscription.id} (PayPal ID: ${resource.id}) with immediate access. Next billing: ${nextBillingDate.toISOString()}`);
  } catch (error) {
    console.error(`❌ Failed to activate subscription ${resource.id}:`, error);
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
    
    // First, try to find and activate the subscription
    const subscription = await prisma.userSubscription.findFirst({
      where: { paypalSubscriptionId: subscriptionId },
      include: { user: true }
    });
    
    if (subscription) {
      console.log(`✅ Found subscription ${subscription.id} for payment ${resource.id}`);
      
      // Update payment details AND activate the subscription
      const updatedSubscription = await prisma.userSubscription.update({
        where: { id: subscription.id },
        data: {
          status: "active", // Activate subscription immediately on payment
          lastPaymentDate: new Date(resource.create_time),
          amountPaid: parseFloat(resource.amount.total),
          currency: resource.amount.currency || "USD",
          startDate: new Date(), // Set start date to payment time for immediate access
          nextBillingDate: resource.next_payment_date
            ? new Date(resource.next_payment_date)
            : new Date(Date.now() + 30 * 24 * 60 * 60 * 1000), // Default to 30 days from now
          updatedAt: new Date(),
          metadata: {
            ...(subscription.metadata as Record<string, unknown> || {}),
            payment_completed: true,
            payment_completed_at: new Date().toISOString(),
            paypal_sale_id: resource.id,
            activated_via_payment: true
          }
        }
      });
      
      console.log(`🎉 Activated subscription ${subscription.id} via payment ${resource.id}`);
    } else {
      console.warn(`⚠️ No subscription found for PayPal subscription ID: ${subscriptionId}`);
      
      // Fallback: Try to find pending subscription by user email or plan
      // This handles cases where the subscription ID wasn't saved yet
      console.log(`🔍 Attempting to find subscription by other criteria...`);
      
      // You could add additional search logic here if needed
      // For example, by searching for recent pending subscriptions
      const recentSubscriptions = await prisma.userSubscription.findMany({
        where: {
          status: { in: ["pending_payment", "pending"] },
          createdAt: {
            gte: new Date(Date.now() - 60 * 60 * 1000) // Last hour
          }
        },
        orderBy: {
          createdAt: 'desc'
        }
      });
      
      if (recentSubscriptions.length > 0) {
        console.log(`🔍 Found ${recentSubscriptions.length} recent pending subscription(s)`);
        // You might want to add logic here to match the correct subscription
        // For now, we'll just log it for debugging
      }
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
import { NextResponse } from "next/server";
import { prisma } from "@/lib/prisma";
import { verifyToken, type TokenPayload } from "@/lib/auth";
import { cookies } from "next/headers";

export const runtime = "nodejs";

// Check current user's subscription status
export async function GET(req: Request) {
  try {
    const cookieStore = await cookies();
    const token = cookieStore.get("auth")?.value;
    
    console.log("🔐 Auth check - Token found:", !!token);
    console.log("🔐 Auth check - Token length:", token?.length || 0);

    if (!token) {
      console.log("❌ No auth token found in cookies");
      return NextResponse.json(
        { ok: false, error: "Usuario no autenticado" },
        { status: 401 }
      );
    }

    // Verify JWT token
    let tokenPayload: TokenPayload;
    try {
      tokenPayload = await verifyToken<TokenPayload>(token);
      console.log("✅ Token verified for user:", tokenPayload.email);
    } catch (error) {
      console.log("❌ Token verification failed:", error);
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

    // Check current subscription (excluding free plan)
    const currentSubscription = await prisma.userSubscription.findFirst({
      where: { 
        userId: user.id,
        status: "active",
        NOT: {
          plan: {
            name: "Básico" // Exclude free plan
          }
        }
      },
      include: {
        plan: true
      }
    });

    // Get all available plans
    const availablePlans = await prisma.subscriptionPlan.findMany({
      where: { isActive: true },
      orderBy: { price: "asc" }
    });

    return NextResponse.json({
      ok: true,
      hasActiveSubscription: !!currentSubscription,
      currentSubscription: currentSubscription ? {
        id: currentSubscription.id,
        planName: currentSubscription.plan.name,
        planPrice: currentSubscription.plan.price.toString(),
        status: currentSubscription.status,
        nextBillingDate: currentSubscription.nextBillingDate
      } : null,
      availablePlans: availablePlans.map(plan => ({
        id: plan.id,
        name: plan.name,
        price: plan.price.toString(),
        paypalPlanId: plan.paypalPlanId,
        isFree: plan.price.toString() === "0.00"
      }))
    });

  } catch (error) {
    console.error("Check current subscription error:", error);
    return NextResponse.json(
      { ok: false, error: "Error interno del servidor" },
      { status: 500 }
    );
  }
}
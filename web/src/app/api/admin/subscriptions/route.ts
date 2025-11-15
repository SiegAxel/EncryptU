import { NextResponse } from "next/server";
import { prisma } from "@/lib/prisma";
import { requireAdmin } from "@/app/api/admin/requireAdmin";

export const runtime = "nodejs";

// GET /api/admin/subscriptions - Get all subscriptions with user info
export async function GET(req: Request) {
  try {
    const me = await requireAdmin();
    if (!me) {
      return NextResponse.json(
        { ok: false, error: "Forbidden" },
        { status: 403 }
      );
    }

    const { searchParams } = new URL(req.url);
    const page = parseInt(searchParams.get("page") || "1");
    const limit = parseInt(searchParams.get("limit") || "10");
    const status = searchParams.get("status");
    const search = searchParams.get("search");

    const skip = (page - 1) * limit;

    // Build where clause - eslint disabled for dynamic query building
    const where: any = {}; // eslint-disable-line @typescript-eslint/no-explicit-any
    
    if (status && status !== "all") {
      where.status = status;
    }

    if (search) {
      where.OR = [
        { user: { name: { contains: search, mode: "insensitive" } } },
        { user: { email: { contains: search, mode: "insensitive" } } },
        { plan: { name: { contains: search, mode: "insensitive" } } }
      ];
    }

    const [subscriptions, total] = await Promise.all([
      prisma.userSubscription.findMany({
        where,
        include: {
          user: {
            select: { id: true, name: true, email: true }
          },
          plan: true
        },
        skip,
        take: limit,
        orderBy: { createdAt: "desc" }
      }),
      prisma.userSubscription.count({ where })
    ]);

    const totalPages = Math.ceil(total / limit);

    return NextResponse.json({
      ok: true,
      subscriptions: subscriptions.map((sub: any) => ({ // eslint-disable-line @typescript-eslint/no-explicit-any
        id: sub.id,
        status: sub.status,
        startDate: sub.startDate,
        endDate: sub.endDate,
        nextBillingDate: sub.nextBillingDate,
        amountPaid: sub.amountPaid.toString(),
        currency: sub.currency,
        paypalSubscriptionId: sub.paypalSubscriptionId,
        user: sub.user,
        plan: sub.plan
      })),
      pagination: {
        page,
        limit,
        total,
        totalPages,
        hasNext: page < totalPages,
        hasPrev: page > 1
      }
    });

  } catch (error) {
    console.error("Admin subscriptions error:", error);
    return NextResponse.json(
      { ok: false, error: "Internal server error" },
      { status: 500 }
    );
  }
}
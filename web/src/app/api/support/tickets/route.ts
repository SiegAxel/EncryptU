import { NextResponse } from "next/server";
import { prisma } from "@/lib/prisma";
import { requireAgent } from "../requireAgent";

export const runtime = "nodejs";

export async function GET() {
  const me = await requireAgent();
  if (!me) return NextResponse.json({ ok: false, error: "Forbidden" }, { status: 403 });

  const tickets = await prisma.contactTicket.findMany({
    orderBy: { createdAt: "desc" },
    select: {
      id: true, firstName: true, lastName: true, email: true,
      reason: true, status: true, createdAt: true,
      assignedTo: { select: { id: true, name: true } },
      _count: { select: { messages: true } },
    },
  });

  return NextResponse.json({ ok: true, tickets });
}

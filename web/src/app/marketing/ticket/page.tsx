import { cookies } from "next/headers";
import { redirect } from "next/navigation";
import { verifyToken, type TokenPayload } from "@/lib/auth";
import { prisma } from "@/lib/prisma";
import TicketsPageClient from "./page-client";

export const revalidate = 0;
export const dynamic = "force-dynamic";
export default async function UserTicketsPage() {
  const token = (await cookies()).get("auth")?.value;
  if (!token) redirect("/auth/login?next=/marketing/ticket");

  const u = await verifyToken<TokenPayload>(token).catch(() => null);
  if (!u) redirect("/auth/login?next=/marketing/ticket");
  if (u.role !== "usuario") redirect("/");

  const raw = await prisma.contactTicket.findMany({
    where: { email: u.email },
    orderBy: { createdAt: "desc" },
    select: {
      id: true,
      reason: true,
      status: true,
      createdAt: true,
      _count: { select: { messages: true } },
    },
  });

  // 🔧 serializa Date -> string
  const tickets = raw.map(t => ({
    ...t,
    createdAt: t.createdAt.toISOString(),
  }));

  return <TicketsPageClient tickets={tickets} />;
}

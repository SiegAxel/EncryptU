// src/app/marketing/ticket/layout.tsx
import { cookies } from "next/headers";
import { redirect } from "next/navigation";
import { verifyToken, type TokenPayload } from "@/lib/auth";

export default async function TicketLayout({ children }: { children: React.ReactNode }) {
  const token = (await cookies()).get("auth")?.value;
  if (!token) redirect("/auth/login?next=/marketing/ticket");

  const u = await verifyToken<TokenPayload>(token).catch(() => null);
  if (!u) redirect("/auth/login?next=/marketing/ticket");
  if (u.role !== "usuario") redirect("/");

  return <>{children}</>;
}

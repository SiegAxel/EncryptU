import { cookies } from "next/headers";
import { redirect } from "next/navigation";
import { verifyToken, type TokenPayload } from "@/lib/auth";

export default async function DashboardLayout({ children }: { children: React.ReactNode }) {
  const token = (await cookies()).get("auth")?.value;
  if (!token) redirect("/auth/login?next=/dashboard");
  try { await verifyToken<TokenPayload>(token); } catch { redirect("/auth/login?next=/dashboard"); }
  return <>{children}</>;
}

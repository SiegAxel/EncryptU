import { cookies } from "next/headers";
import { redirect } from "next/navigation";
import { verifyToken, type TokenPayload } from "@/lib/auth";

export default async function AdminLayout({ children }: { children: React.ReactNode }) {
  const token = (await cookies()).get("auth")?.value;
  if (!token) redirect("/auth/login?next=/dashboard/admin");
  const u = await verifyToken<TokenPayload>(token).catch(() => null);
  if (!u || u.role !== "admin") redirect("/");
  return <>{children}</>;
}

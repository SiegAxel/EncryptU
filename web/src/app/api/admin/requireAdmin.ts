import { cookies } from "next/headers";
import { verifyToken, type TokenPayload } from "@/lib/auth";

export async function requireAdmin(): Promise<TokenPayload | null> {
  const token = (await cookies()).get("auth")?.value;
  if (!token) return null;

  try {
    const u = await verifyToken<TokenPayload>(token);
    return u.role === "admin" ? u : null;
  } catch {
    return null;
  }
}

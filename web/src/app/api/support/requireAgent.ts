import { cookies } from "next/headers";
import { verifyToken, type TokenPayload } from "@/lib/auth";

export type Agent = TokenPayload & { role: "soporte" | "admin" };

export async function requireAgent(): Promise<Agent | null> {
    const token = (await cookies()).get("auth")?.value;
    if (!token) return null;
    try {
        const u = await verifyToken<TokenPayload>(token);
        if (u.role === "soporte" || u.role === "admin") return u as Agent;
        return null;
    } catch {
        return null;
    }
}

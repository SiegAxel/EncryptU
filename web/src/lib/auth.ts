import { SignJWT, jwtVerify, type JWTPayload } from "jose";

const rawSecret =
  process.env.AUTH_SECRET ?? process.env.JWT_SECRET ?? process.env.NEXTAUTH_SECRET;

if (!rawSecret && process.env.NODE_ENV === "production") {
  throw new Error("Se requiere la variable de entorno AUTH_SECRET en producción.");
}

const secretKey = new TextEncoder().encode(rawSecret ?? "development-secret");

export type Role = "usuario" | "soporte" | "admin";

export type TokenPayload = JWTPayload & {
  sub: string;
  role: Role;
  name: string;
  email: string;
};

export type SignOptions = {
  /** Tiempo hasta que expira el token, por defecto 7 días. */
  expiresIn?: string | number;
};

export async function signToken<T extends JWTPayload>(
  payload: T,
  options: SignOptions = {}
): Promise<string> {
  const { expiresIn = "7d" } = options;

  return await new SignJWT(payload)
    .setProtectedHeader({ alg: "HS256", typ: "JWT" })
    .setIssuedAt()
    .setExpirationTime(expiresIn)
    .sign(secretKey);
}

export async function verifyToken<T extends JWTPayload>(token: string): Promise<T> {
  const { payload } = await jwtVerify(token, secretKey);
  return payload as T;
}

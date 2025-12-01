/**
 * @jest-environment node
 */

import type { TokenPayload, Role } from "@/lib/auth";

// 👇 Mock virtual de "jose" (no depende de archivos externos ni moduleNameMapper)
jest.mock(
  "jose",
  () => {
    type JWTPayload = {
      sub?: string;
    } & Record<string, unknown>;

    class SignJWT {
      private payload: JWTPayload;

      constructor(payload: JWTPayload) {
        this.payload = payload;
      }

      setProtectedHeader(_header: Record<string, unknown>): this {
        return this;
      }

      setIssuedAt(): this {
        return this;
      }

      setExpirationTime(_exp: string | number): this {
        return this;
      }

      async sign(_key: Uint8Array): Promise<string> {
        const payloadB64 = Buffer.from(
          JSON.stringify(this.payload),
          "utf8"
        ).toString("base64url");

        // token mock: header.mock.payload.mock
        return `mock.${payloadB64}.mock`;
      }
    }

    async function jwtVerify(
      token: string,
      _key: Uint8Array
    ): Promise<{ payload: JWTPayload }> {
      const parts = token.split(".");
      if (parts.length !== 3) {
        throw new Error("Invalid token format");
      }

      const payloadB64 = parts[1];
      const json = Buffer.from(payloadB64, "base64url").toString("utf8");
      const payload = JSON.parse(json) as JWTPayload;

      return { payload };
    }

    return { SignJWT, jwtVerify };
  },
  { virtual: true }
);

// 👈 IMPORTAMOS auth DESPUÉS de mockear "jose"
import { signToken, verifyToken } from "@/lib/auth";

describe("Auth JWT helpers", () => {
  const basePayload: TokenPayload = {
    sub: "10",
    role: "admin" as Role,
    name: "Liam Test",
    email: "liam.test@example.com",
  };

  test("signToken y verifyToken preservan el payload", async () => {
    const token = await signToken<TokenPayload>(basePayload);

    expect(typeof token).toBe("string");
    expect(token.split(".").length).toBe(3); // formato JWT

    const decoded = await verifyToken<TokenPayload>(token);

    expect(decoded.sub).toBe("10");
    expect(decoded.role).toBe("admin");
    expect(decoded.name).toBe("Liam Test");
    expect(decoded.email).toBe("liam.test@example.com");
  });
});

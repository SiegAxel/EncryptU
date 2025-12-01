// test/__mocks__/jose.ts

// Tipo mínimo para que TypeScript no se queje
export type JWTPayload = {
  sub?: string;
} & Record<string, unknown>;

// Implementación súper simple y suficiente para los tests
export class SignJWT {
  private payload: JWTPayload;

  // No necesitamos usar header/iat/exp de verdad para los tests unitarios
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
    // Token fake: header.mock.payloadBase64.mock
    const payloadB64 = Buffer.from(
      JSON.stringify(this.payload),
      "utf8"
    ).toString("base64url");

    return `mock.${payloadB64}.mock`;
  }
}

export async function jwtVerify(
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

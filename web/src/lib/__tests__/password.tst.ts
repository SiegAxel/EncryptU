/**
 * @jest-environment node
 */

import { hashPassword, verifyPassword, isValidHash } from "@/lib/password";

describe("PasswordHasher (Argon2)", () => {
  const plainPassword = "EncryptU2025*";

  test("hashPassword genera un hash Argon2 válido", async () => {
    const hash = await hashPassword(plainPassword);

    // no debe ser texto plano
    expect(hash).not.toBe(plainPassword);
    // debe parecer hash de argon2
    expect(typeof hash).toBe("string");
    expect(hash.length).toBeGreaterThan(10);
    expect(isValidHash(hash)).toBe(true);
  });

  test("verifyPassword acepta la contraseña correcta", async () => {
    const hash = await hashPassword(plainPassword);

    const result = await verifyPassword(hash, plainPassword);

    expect(result).toBe(true);
  });

  test("verifyPassword rechaza una contraseña incorrecta", async () => {
    const hash = await hashPassword(plainPassword);

    const result = await verifyPassword(hash, "OtraCosa123!");

    expect(result).toBe(false);
  });

  test("isValidHash devuelve false para cadenas que no son Argon2", () => {
    expect(isValidHash("no-es-un-hash")).toBe(false);
    expect(isValidHash("")).toBe(false);
  });
});

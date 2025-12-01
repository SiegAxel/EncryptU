/**
 * @jest-environment node
 */

import { cn } from "@/lib/cn";

describe("cn (clsx + tailwind-merge)", () => {
  test("combina clases simples en una sola cadena", () => {
    const result = cn("bg-red-500", "text-white", "p-4");

    expect(result).toBe("bg-red-500 text-white p-4");
  });

  test("omite valores falsy (undefined, null, false)", () => {
    const result = cn("bg-red-500", undefined, null, false && "p-4", "text-white");

    expect(result).toBe("bg-red-500 text-white");
  });

  test("tailwind-merge elimina clases conflictivas duplicadas", () => {
    const result = cn("p-2", "p-4", "text-sm", "text-lg");

    // tailwind-merge deja normalmente la última clase de cada grupo
    expect(result).toBe("p-4 text-lg");
  });
});

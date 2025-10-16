import { PrismaClient } from "@prisma/client";

// Reutiliza la instancia en desarrollo para evitar múltiples conexiones.
declare global {
  var prismaGlobal: PrismaClient | undefined;
}

export const prisma = globalThis.prismaGlobal ?? new PrismaClient();

if (process.env.NODE_ENV !== "production") {
  globalThis.prismaGlobal = prisma;
}

export default prisma;

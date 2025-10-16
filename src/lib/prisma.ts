import { PrismaClient } from "@prisma/client";

/**
 * Prisma client instance shared across the application.
 *
 * In development we reuse the same instance to avoid creating too many
 * database connections when Next.js hot-reloads the server layer.
 */
declare global {
  // eslint-disable-next-line no-var
  var __prismaClient: PrismaClient | undefined;
}

const prismaGlobal = globalThis as typeof globalThis & {
  __prismaClient?: PrismaClient;
};

export const prisma = prismaGlobal.__prismaClient ?? new PrismaClient();

if (process.env.NODE_ENV !== "production") {
  prismaGlobal.__prismaClient = prisma;
}

export default prisma;

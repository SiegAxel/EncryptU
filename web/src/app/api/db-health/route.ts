import { NextResponse } from "next/server";
import { prisma } from "@/lib/prisma";

type DbVersionRow = { version: string };
type DbNameRow = { current_database: string };

export async function GET() {
  try {
    // Chequeos útiles: versión y base actual
    const version = await prisma.$queryRaw<DbVersionRow[]>`SELECT version()`;
    const db = await prisma.$queryRaw<DbNameRow[]>`SELECT current_database()`;

    return NextResponse.json({
      ok: true,
      version: version?.[0]?.version ?? null,
      database: db?.[0]?.current_database ?? null,
    });
  } catch (err: unknown) {
    const message = err instanceof Error ? err.message : String(err);
    return NextResponse.json({ ok: false, error: message }, { status: 500 });
  }
}

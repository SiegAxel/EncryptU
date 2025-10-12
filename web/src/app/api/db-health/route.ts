import { NextResponse } from "next/server";
import { prisma } from "@/lib/prisma";

export async function GET() {
  try {
    // Chequeos útiles: versión y base actual
    const version = await prisma.$queryRaw<Array<{ version: string }>>`SELECT version()`;
    const db = await prisma.$queryRaw<Array<{ current_database: string }>>`SELECT current_database()`;

    return NextResponse.json({
      ok: true,
      version: version?.[0]?.version ?? null,
      database: db?.[0]?.current_database ?? null,
    });
  } catch (err: any) {
    return NextResponse.json({ ok: false, error: err?.message ?? String(err) }, { status: 500 });
  }
}

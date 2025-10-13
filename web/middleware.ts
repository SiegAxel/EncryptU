// web/middleware.ts
import { NextResponse, type NextRequest } from "next/server";
import { verifyToken, type TokenPayload } from "./src/lib/auth";

function needs(path: string, prefix: string) {
  return path === prefix || path.startsWith(prefix + "/");
}

const roleHome = (role: "usuario" | "soporte" | "admin") =>
  role === "admin" ? "/dashboard/admin"
  : role === "soporte" ? "/dashboard/soporte"
  : "/";

export async function middleware(req: NextRequest) {
  const { pathname, search } = req.nextUrl;

  // Solo protegemos /dashboard/*
  if (!needs(pathname, "/dashboard")) return NextResponse.next();

  const token = req.cookies.get("auth")?.value;

  // Si piden exactamente /dashboard, redirige al “home” del rol
  if (pathname === "/dashboard") {
    if (!token) {
      const url = req.nextUrl.clone();
      url.pathname = "/auth/login";
      url.search = `?next=${encodeURIComponent(pathname + search)}`;
      return NextResponse.redirect(url);
    }
    try {
      const payload = await verifyToken<TokenPayload>(token);
      const dest = roleHome(payload.role);
      return NextResponse.redirect(new URL(dest, req.url));
    } catch {
      const url = req.nextUrl.clone();
      url.pathname = "/auth/login";
      url.search = `?next=${encodeURIComponent(pathname + search)}`;
      return NextResponse.redirect(url);
    }
  }

  // Para subrutas específicas:
  if (!token) {
    const url = req.nextUrl.clone();
    url.pathname = "/auth/login";
    url.search = `?next=${encodeURIComponent(pathname + search)}`;
    return NextResponse.redirect(url);
  }

  try {
    const payload = await verifyToken<TokenPayload>(token);

    if (needs(pathname, "/dashboard/admin") && payload.role !== "admin") {
      return NextResponse.redirect(new URL("/", req.url));
    }
    if (needs(pathname, "/dashboard/soporte") && !["admin", "soporte"].includes(payload.role)) {
      return NextResponse.redirect(new URL("/", req.url));
    }

    return NextResponse.next();
  } catch {
    const url = req.nextUrl.clone();
    url.pathname = "/auth/login";
    url.search = `?next=${encodeURIComponent(pathname + search)}`;
    return NextResponse.redirect(url);
  }
}

export const config = {
  matcher: ["/dashboard/:path*"],
};

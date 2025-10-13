import { NextResponse, type NextRequest } from "next/server";
import { verifyToken, type TokenPayload } from "./src/lib/auth";

function needs(path: string, prefix: string) {
  return path === prefix || path.startsWith(prefix + "/");
}

export async function middleware(req: NextRequest) {
  const { pathname, search } = req.nextUrl;

  // Solo protegemos dashboard
  if (!needs(pathname, "/dashboard")) return NextResponse.next();

  const token = req.cookies.get("auth")?.value;
  if (!token) {
    const url = req.nextUrl.clone();
    url.pathname = "/auth/login";
    url.search = `?next=${encodeURIComponent(pathname + search)}`;
    return NextResponse.redirect(url);
  }

  try {
    const u = await verifyToken<TokenPayload>(token);

    // /dashboard raíz → envía a su sección o a /
    if (pathname === "/dashboard") {
      if (u.role === "admin") {
        return NextResponse.redirect(new URL("/dashboard/admin", req.url));
      }
      if (u.role === "soporte") {
        return NextResponse.redirect(new URL("/dashboard/soporte", req.url));
      }
      return NextResponse.redirect(new URL("/", req.url)); // usuario
    }

    // Acceso estricto por rol a subrutas
    if (needs(pathname, "/dashboard/admin") && u.role !== "admin") {
      return NextResponse.redirect(new URL("/", req.url));
    }
    if (needs(pathname, "/dashboard/soporte") && u.role !== "soporte") {
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

// ⚠️ incluye /dashboard "pelado" y subrutas
export const config = {
  matcher: ["/dashboard", "/dashboard/:path*"],
};

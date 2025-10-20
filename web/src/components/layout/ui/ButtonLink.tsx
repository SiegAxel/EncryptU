import Link, { LinkProps } from "next/link";
import { cn } from "@/lib/cn";

// IMPORTA estos desde tu Button.tsx para no duplicar estilos
// (si Button.tsx y ButtonLink.tsx están en la misma carpeta, puedes hacer import { base, variants, sizes } from "./Button"
// pero como los definiste dentro del archivo, replicamos acá)
type Variant = "primary" | "outline" | "ghost" | "inverted";
type Size = "sm" | "md" | "lg";

type Props = LinkProps & {
  children: React.ReactNode;
  className?: string;
  variant?: Variant;
  size?: Size;
};

const base =
  "inline-flex items-center justify-center rounded-md font-medium transition-colors " +
  "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 " +
  "disabled:opacity-50 disabled:pointer-events-none";

const variants: Record<Variant, string> = {
  primary:  "bg-brand text-white hover:opacity-90 focus-visible:ring-brand",
  outline:  "border border-brand text-brand hover:bg-brand hover:text-white focus-visible:ring-brand",
  ghost:    "text-slate-700 hover:bg-slate-100 focus-visible:ring-slate-400",
  inverted: "bg-white text-slate-900 hover:bg-slate-100 focus-visible:ring-white",
};

const sizes: Record<Size, string> = {
  sm: "h-9 px-3 text-sm",
  md: "h-10 px-4 text-sm",
  lg: "h-11 px-5 text-base",
};

export default function ButtonLink({
  children,
  className,
  href,
  variant = "primary",
  size = "md",
  ...props
}: Props) {
  return (
    <Link
      href={href}
      className={cn(base, variants[variant], sizes[size], className)}
      {...props}
    >
      {children}
    </Link>
  );
}

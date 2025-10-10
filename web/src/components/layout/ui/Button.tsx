import * as React from "react";
import { cn } from "@/lib/cn";

type Variant = "primary" | "outline" | "ghost" | "inverted";
type Size = "sm" | "md" | "lg";

type Props = React.ButtonHTMLAttributes<HTMLButtonElement> & {
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
  // Para usar sobre fondos oscuros (por ej. el card destacado)
  inverted: "bg-white text-slate-900 hover:bg-slate-100 focus-visible:ring-white",
};

const sizes: Record<Size, string> = {
  sm: "h-9 px-3 text-sm",
  md: "h-10 px-4 text-sm",
  lg: "h-11 px-5 text-base",
};

export default function Button({
  className,
  variant = "primary",
  size = "md",
  type = "button",
  ...props
}: Props) {
  return (
    <button
      type={type}
      className={cn(base, variants[variant], sizes[size], className)}
      {...props}
    />
  );
}

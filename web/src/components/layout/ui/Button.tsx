"use client";
import Link, { type LinkProps } from "next/link";
import { cn } from "@/lib/cn";
import type { ButtonHTMLAttributes, AnchorHTMLAttributes } from "react";

// variantes de estilo
type Variant = "primary" | "outline";

// Si viene href => es link; si no => button
type ButtonAsLinkProps = {
  href: string;
  variant?: Variant;
  className?: string;
} & LinkProps &
  Omit<AnchorHTMLAttributes<HTMLAnchorElement>, "href">;

type ButtonAsButtonProps = {
  href?: undefined;
  variant?: Variant;
  className?: string;
} & ButtonHTMLAttributes<HTMLButtonElement>;

type Props = ButtonAsLinkProps | ButtonAsButtonProps;

export default function Button(props: Props) {
  const { variant = "primary", className } = props as Props;
  const base = variant === "primary" ? "btn-primary" : "btn-outline";

  if ("href" in props && props.href) {
    const { href, ...rest } = props as ButtonAsLinkProps;
    return (
      <Link href={href} className={cn(base, className)} {...rest} />
    );
  }

  const rest = props as ButtonAsButtonProps;
  return <button className={cn(base, className)} {...rest} />;
}

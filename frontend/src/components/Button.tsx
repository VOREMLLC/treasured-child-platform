import Link from "next/link";
import type { ButtonHTMLAttributes } from "react";

import { Icon, type IconName } from "./Icon";

export type ButtonVariant = "primary" | "secondary" | "ghost";

interface StyleOptions {
  variant?: ButtonVariant;
  full?: boolean;
  size?: "md" | "lg";
  className?: string;
}

const VARIANTS: Record<ButtonVariant, string> = {
  primary:
    "bg-blue text-white shadow-s hover:bg-blue-deep disabled:opacity-70",
  secondary:
    "bg-surface text-ink border-2 border-line hover:border-blue hover:text-blue-ink",
  ghost: "bg-transparent text-blue-ink hover:bg-blue-soft",
};

/** Shared classes so links and buttons look identical. */
export function buttonClasses({
  variant = "primary",
  full = false,
  size = "md",
  className = "",
}: StyleOptions = {}): string {
  return [
    "inline-flex items-center justify-center gap-2 rounded-control font-body font-extrabold",
    "select-none transition-[transform,background-color,border-color,color] duration-150 ease-out",
    "motion-safe:active:scale-[.98] disabled:cursor-not-allowed",
    "focus-visible:outline focus-visible:outline-[3px] focus-visible:outline-offset-2",
    size === "lg" ? "min-h-14 px-6 text-label" : "min-h-12 px-5 text-label",
    full ? "w-full" : "",
    VARIANTS[variant],
    className,
  ].join(" ");
}

function Spinner() {
  return (
    <svg
      viewBox="0 0 24 24"
      width={22}
      height={22}
      aria-hidden
      className="motion-safe:animate-spin"
    >
      <circle
        cx="12"
        cy="12"
        r="9"
        fill="none"
        stroke="currentColor"
        strokeOpacity=".3"
        strokeWidth="3"
      />
      <path
        d="M21 12a9 9 0 00-9-9"
        fill="none"
        stroke="currentColor"
        strokeWidth="3"
        strokeLinecap="round"
      />
    </svg>
  );
}

interface ButtonProps
  extends ButtonHTMLAttributes<HTMLButtonElement>,
    StyleOptions {
  loading?: boolean;
  icon?: IconName;
  iconRight?: IconName;
}

export function Button({
  variant,
  full,
  size,
  className,
  loading = false,
  icon,
  iconRight,
  children,
  disabled,
  type = "button",
  ...rest
}: ButtonProps) {
  return (
    <button
      type={type}
      disabled={disabled || loading}
      aria-busy={loading || undefined}
      className={buttonClasses({ variant, full, size, className })}
      {...rest}
    >
      {loading ? <Spinner /> : icon ? <Icon name={icon} /> : null}
      <span>{children}</span>
      {iconRight && !loading && <Icon name={iconRight} />}
    </button>
  );
}

interface ButtonLinkProps extends StyleOptions {
  href: string;
  children: React.ReactNode;
  icon?: IconName;
  iconRight?: IconName;
  /** For tel:, mailto: and https: links that leave the app. */
  external?: boolean;
}

export function ButtonLink({
  href,
  children,
  icon,
  iconRight,
  external = false,
  ...style
}: ButtonLinkProps) {
  const inner = (
    <>
      {icon && <Icon name={icon} />}
      <span>{children}</span>
      {iconRight && <Icon name={iconRight} />}
    </>
  );
  if (external) {
    const opensTab = href.startsWith("http");
    return (
      <a
        href={href}
        className={buttonClasses(style)}
        target={opensTab ? "_blank" : undefined}
        rel={opensTab ? "noopener noreferrer" : undefined}
      >
        {inner}
      </a>
    );
  }
  return (
    <Link href={href} className={buttonClasses(style)}>
      {inner}
    </Link>
  );
}

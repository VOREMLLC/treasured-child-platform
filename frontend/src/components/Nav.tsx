"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

import { Brand } from "./Brand";
import { buttonClasses } from "./Button";
import { MobileBottomBar, isPortalPath } from "./MobileBottomBar";

interface NavLink {
  href: string;
  label: string;
}

const PUBLIC_LINKS: NavLink[] = [
  { href: "/about", label: "About" },
  { href: "/programmes", label: "Programmes" },
  { href: "/pay", label: "Pay fees" },
  { href: "/login", label: "Sign in" },
];

const PORTAL_LINKS: NavLink[] = [
  { href: "/portal", label: "Home" },
  { href: "/portal/courses", label: "My courses" },
  { href: "/pay", label: "Pay fees" },
  { href: "/portal/me", label: "Me" },
];

/**
 * Top bar (64px). On phones it shows only the logo; navigation moves to
 * the bottom bar where thumbs can reach it.
 */
export function Nav() {
  const pathname = usePathname() ?? "/";
  const portal = isPortalPath(pathname);
  const links = portal ? PORTAL_LINKS : PUBLIC_LINKS;

  return (
    <>
      <header className="sticky top-0 z-40 border-b border-line bg-surface">
        <div className="wrap flex h-16 items-center justify-between gap-4">
          <Brand priority href={portal ? "/portal" : "/"} />

          <nav aria-label="Primary" className="hidden items-center gap-2 md:flex">
            {links.map((l) => {
              const active =
                l.href === pathname ||
                (l.href !== "/portal" && pathname.startsWith(l.href));
              return (
                <Link
                  key={l.href}
                  href={l.href}
                  aria-current={active ? "page" : undefined}
                  className={[
                    "inline-flex min-h-12 items-center rounded-control px-3 text-body font-bold transition-colors duration-200",
                    active ? "text-blue-ink" : "text-muted hover:text-ink",
                  ].join(" ")}
                >
                  {l.label}
                </Link>
              );
            })}
            {!portal && (
              <Link
                href="/apply"
                className={buttonClasses({ className: "ml-2 !text-body" })}
              >
                Apply now
              </Link>
            )}
          </nav>
        </div>
      </header>
      <MobileBottomBar />
    </>
  );
}

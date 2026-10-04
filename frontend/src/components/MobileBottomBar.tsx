"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

import { Icon, type IconName } from "./Icon";

interface Tab {
  href: string;
  label: string;
  icon: IconName;
  /** Path prefixes that light this tab up. */
  match: (path: string) => boolean;
}

const PUBLIC_TABS: Tab[] = [
  { href: "/", label: "Home", icon: "home", match: (p) => p === "/" },
  { href: "/apply", label: "Apply", icon: "school", match: (p) => p.startsWith("/apply") },
  { href: "/pay", label: "Pay fees", icon: "card", match: (p) => p.startsWith("/pay") },
  {
    href: "/login",
    label: "Sign in",
    icon: "user",
    match: (p) => ["/login", "/register", "/forgot-password", "/reset-password"].some((x) => p.startsWith(x)),
  },
];

const PORTAL_TABS: Tab[] = [
  { href: "/portal", label: "Home", icon: "home", match: (p) => p === "/portal" },
  {
    href: "/portal/courses",
    label: "My courses",
    icon: "book",
    match: (p) => p.startsWith("/portal/courses"),
  },
  { href: "/portal/me", label: "Me", icon: "user", match: (p) => p.startsWith("/portal/me") },
];

export function isPortalPath(path: string): boolean {
  return path === "/portal" || path.startsWith("/portal/");
}

/** Phone-only tab bar, fixed to the bottom and clear of the home indicator. */
export function MobileBottomBar() {
  const pathname = usePathname() ?? "/";
  const tabs = isPortalPath(pathname) ? PORTAL_TABS : PUBLIC_TABS;

  return (
    <nav
      aria-label="Main"
      className="fixed inset-x-0 bottom-0 z-40 border-t border-line bg-surface pb-[env(safe-area-inset-bottom)] md:hidden"
    >
      <ul className="mx-auto flex max-w-[560px] gap-2 px-2">
        {tabs.map((tab) => {
          const active = tab.match(pathname);
          return (
            <li key={tab.href} className="flex-1">
              <Link
                href={tab.href}
                aria-current={active ? "page" : undefined}
                className={[
                  "flex h-16 flex-col items-center justify-center gap-0.5 rounded-control text-caption font-bold",
                  "transition-[transform,color] duration-150 ease-out motion-safe:active:scale-[.98]",
                  active ? "text-blue-ink" : "text-muted",
                ].join(" ")}
              >
                <span
                  className={`grid h-8 w-14 place-items-center rounded-full ${active ? "bg-blue-soft" : ""}`}
                >
                  <Icon name={tab.icon} size={22} />
                </span>
                {tab.label}
              </Link>
            </li>
          );
        })}
      </ul>
    </nav>
  );
}

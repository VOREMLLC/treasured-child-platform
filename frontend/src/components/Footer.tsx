import Link from "next/link";

import { Brand } from "./Brand";
import { Icon, type IconName } from "./Icon";
import { SCHOOL_PHONE_DISPLAY, SCHOOL_PHONE_TEL, WHATSAPP_URL } from "@/lib/contact";

export function Footer() {
  return (
    <footer className="mt-16 border-t border-line bg-surface">
      <div className="wrap grid gap-8 py-12 sm:grid-cols-2 md:grid-cols-[1.4fr_1fr_1fr]">
        <div>
          <Brand />
          <p className="mt-3 flex items-center gap-2 text-body text-muted">
            <Icon name="pin" size={20} />
            Orerokpe, Delta State, Nigeria
          </p>
        </div>

        <FooterCol title="School">
          <FooterLink href="/about">About us</FooterLink>
          <FooterLink href="/programmes">Programmes</FooterLink>
          <FooterLink href="/apply">Apply now</FooterLink>
          <FooterLink href="/pay">Pay fees</FooterLink>
        </FooterCol>

        <FooterCol title="Talk to us">
          <FooterLink href={WHATSAPP_URL} icon="whatsapp">
            WhatsApp us
          </FooterLink>
          <FooterLink href={SCHOOL_PHONE_TEL} icon="phone">
            {SCHOOL_PHONE_DISPLAY}
          </FooterLink>
          <FooterLink href="/login" icon="user">
            Sign in
          </FooterLink>
        </FooterCol>
      </div>

      <p className="wrap border-t border-line py-5 text-caption text-muted">
        © {new Date().getFullYear()} Treasured Child School
      </p>
    </footer>
  );
}

function FooterCol({
  title,
  children,
}: {
  title: string;
  children: React.ReactNode;
}) {
  return (
    <div>
      <h2 className="mb-2 font-display text-title font-bold text-ink">
        {title}
      </h2>
      <ul>{children}</ul>
    </div>
  );
}

function FooterLink({
  href,
  icon,
  children,
}: {
  href: string;
  icon?: IconName;
  children: React.ReactNode;
}) {
  const cls =
    "inline-flex min-h-12 items-center gap-2 text-body text-muted transition-colors duration-200 hover:text-blue-ink";
  const inner = (
    <>
      {icon && <Icon name={icon} size={20} />}
      {children}
    </>
  );
  return (
    <li>
      {href.startsWith("/") ? (
        <Link href={href} className={cls}>
          {inner}
        </Link>
      ) : (
        <a
          href={href}
          className={cls}
          target={href.startsWith("http") ? "_blank" : undefined}
          rel={href.startsWith("http") ? "noopener noreferrer" : undefined}
        >
          {inner}
        </a>
      )}
    </li>
  );
}

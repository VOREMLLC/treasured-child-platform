import Link from "next/link";
import { Brand } from "./Brand";

export function Footer() {
  return (
    <footer
      id="contact"
      className="bg-surface border-t border-line px-[6vw] py-12 text-muted text-[14px]"
    >
      <div className="grid grid-cols-2 md:grid-cols-[1.4fr_1fr_1fr_1fr] gap-8 max-w-[1180px] mx-auto">
        <div>
          <Brand className="mb-3.5" alt="" />
          <p>Orerokpe, Delta State, Nigeria.</p>
        </div>

        <FooterCol title="School">
          <FooterLink href="/about">About</FooterLink>
          <FooterLink href="/about#leadership">Leadership</FooterLink>
          <FooterLink href="/#programmes">Programmes</FooterLink>
        </FooterCol>

        <FooterCol title="Online">
          <FooterLink href="/programmes/bece-prep">BECE prep</FooterLink>
          <FooterLink href="/programmes/ai-data">AI &amp; data</FooterLink>
          <FooterLink href="/login">Sign in</FooterLink>
        </FooterCol>

        <FooterCol title="Contact">
          <FooterLink href="mailto:hello@treasuredchild.example">
            hello@treasuredchild.example
          </FooterLink>
          <FooterLink href="tel:+2347035918488">+234 703 591 8488</FooterLink>
          <FooterLink href="/pay">Pay fees online</FooterLink>
        </FooterCol>
      </div>

      <p className="border-t border-line mt-7 pt-4 text-center text-[12.5px] text-muted">
        © Treasured Child School. Content is placeholder until the proprietor
        supplies copy and photos.
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
      <h4 className="font-display text-[14px] text-paper mb-3 font-semibold">
        {title}
      </h4>
      {children}
    </div>
  );
}

function FooterLink({
  href,
  children,
}: {
  href: string;
  children: React.ReactNode;
}) {
  if (href.startsWith("/")) {
    return (
      <Link href={href} className="block py-1 hover:text-blue-soft transition">
        {children}
      </Link>
    );
  }
  return (
    <a href={href} className="block py-1 hover:text-blue-soft transition">
      {children}
    </a>
  );
}

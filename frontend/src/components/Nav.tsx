import Link from "next/link";
import { Brand } from "./Brand";

export function Nav() {
  return (
    <nav
      aria-label="Primary"
      className="sticky top-0 z-40 flex items-center justify-between px-[6vw] py-3.5 backdrop-blur-md border-b border-line bg-[rgba(10,22,38,0.85)]"
    >
      <Brand priority />

      <div className="hidden md:flex gap-7 text-[15px] font-medium text-muted">
        <Link href="/about" className="hover:text-blue-soft transition">
          About
        </Link>
        <Link href="/#programmes" className="hover:text-blue-soft transition">
          Programmes
        </Link>
        <Link href="/#why" className="hover:text-blue-soft transition">
          Why us
        </Link>
        <Link href="/#contact" className="hover:text-blue-soft transition">
          Contact
        </Link>
      </div>

      <div className="flex gap-2.5">
        <Link
          href="/login"
          className="hidden md:inline-flex items-center px-4 py-2 rounded-pill border border-line text-paper text-[13.5px] font-semibold hover:border-blue-bright transition"
        >
          Sign in
        </Link>
        <Link
          href="/apply"
          className="inline-flex items-center px-4 py-2 rounded-pill bg-gradient-to-b from-blue to-blue-deep text-white text-[13.5px] font-semibold shadow-[0_10px_24px_-10px_rgba(31,99,201,0.55)] hover:from-blue-bright hover:to-blue transition"
        >
          Apply now
        </Link>
      </div>
    </nav>
  );
}

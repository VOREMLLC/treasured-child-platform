import Link from "next/link";
import { Nav } from "@/components/Nav";
import { Footer } from "@/components/Footer";
import { SignOutButton } from "./SignOutButton";

export const metadata = {
  title: "Portal — Treasured Child School",
  description: "Your Treasured Child portal.",
};

export default function PortalPage() {
  return (
    <>
      <Nav />

      {/* ===== Page header ===== */}
      <header
        className="px-[6vw] pt-[70px] pb-12"
        style={{
          background:
            "radial-gradient(900px 520px at 82% -10%, rgba(47,127,212,0.18) 0, transparent 60%), var(--bg)",
        }}
      >
        <div className="max-w-[1180px] mx-auto">
          <span className="inline-flex items-center gap-2 text-[12px] font-bold uppercase tracking-[0.20em] text-gold mb-4">
            <span className="w-[7px] h-[7px] bg-gold rotate-45 inline-block" />
            Your portal
          </span>
          <h1 className="font-display font-bold text-paper text-[clamp(34px,5vw,56px)] leading-[1.08] tracking-tight mb-2.5">
            You&apos;re signed in.
          </h1>
          <p className="text-[17px] text-muted max-w-[640px]">
            This is the placeholder portal. The real dashboard, course list,
            and learning experience land in slices S15 through S25 of
            BUILD_PLAN.md.
          </p>
        </div>
      </header>

      {/* ===== Body ===== */}
      <section className="px-[6vw] py-14 max-w-[820px] mx-auto">
        <article className="bg-card border border-line rounded-lg p-6 sm:p-8">
          <div className="text-[12px] font-bold uppercase tracking-[0.18em] text-gold mb-2">
            What&apos;s here today
          </div>
          <h2 className="font-display text-paper text-[24px] mb-3">
            Session is alive.
          </h2>
          <p className="text-muted text-[15.5px] mb-2">
            Your sign-in worked. Two httpOnly cookies (access_token, refresh_token)
            are set on your browser by the backend. JavaScript cannot read
            them — only the server can — which is the point.
          </p>
          <p className="text-muted text-[15.5px] mb-6">
            The role-based access middleware (slice S10) will guard this
            page so unauthenticated visitors are redirected to{" "}
            <Link
              href="/login"
              className="text-blue-soft font-semibold hover:underline"
            >
              /login
            </Link>
            . Until then, this page is reachable without a session — that&apos;s
            a known v1 gap.
          </p>
          <div className="flex flex-wrap gap-3">
            <SignOutButton />
            <Link
              href="/"
              className="inline-flex items-center px-5 py-3 rounded-pill border border-line text-paper font-semibold hover:border-blue-bright transition"
            >
              Back to home
            </Link>
          </div>
        </article>
      </section>

      <Footer />
    </>
  );
}

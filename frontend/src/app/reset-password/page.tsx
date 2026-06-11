import { Suspense } from "react";
import Link from "next/link";
import { Nav } from "@/components/Nav";
import { Footer } from "@/components/Footer";
import { ResetPasswordForm } from "./ResetPasswordForm";

export const metadata = {
  title: "Set a new password — Treasured Child School",
  description: "Choose a new password for your Treasured Child account.",
};

export default function ResetPasswordPage() {
  return (
    <>
      <Nav />

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
            Reset password
          </span>
          <h1 className="font-display font-bold text-paper text-[clamp(34px,5vw,56px)] leading-[1.08] tracking-tight mb-2.5">
            Set a new password.
          </h1>
          <p className="text-[17px] text-muted max-w-[640px]">
            Choose something at least 8 characters long. The link you
            followed can only be used once.
          </p>
        </div>
      </header>

      <section className="px-[6vw] py-14 max-w-[480px] mx-auto">
        <Suspense
          fallback={
            <div className="bg-card border border-line rounded-lg p-6 text-muted">
              Loading…
            </div>
          }
        >
          <ResetPasswordForm />
        </Suspense>
        <p className="text-muted text-[14px] text-center mt-6">
          Wrong page?{" "}
          <Link
            href="/login"
            className="text-blue-soft font-semibold hover:underline"
          >
            Sign in
          </Link>
          .
        </p>
      </section>

      <Footer />
    </>
  );
}

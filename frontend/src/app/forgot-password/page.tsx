import Link from "next/link";
import { Nav } from "@/components/Nav";
import { Footer } from "@/components/Footer";
import { ForgotPasswordForm } from "./ForgotPasswordForm";

export const metadata = {
  title: "Forgot your password — Treasured Child School",
  description:
    "Send yourself a password-reset link for your Treasured Child account.",
};

export default function ForgotPasswordPage() {
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
            Forgot password
          </span>
          <h1 className="font-display font-bold text-paper text-[clamp(34px,5vw,56px)] leading-[1.08] tracking-tight mb-2.5">
            Reset your password.
          </h1>
          <p className="text-[17px] text-muted max-w-[640px]">
            Enter the email on your account. We&apos;ll send a one-time
            reset link.
          </p>
        </div>
      </header>

      <section className="px-[6vw] py-14 max-w-[480px] mx-auto">
        <ForgotPasswordForm />
        <p className="text-muted text-[14px] text-center mt-6">
          Remembered it?{" "}
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

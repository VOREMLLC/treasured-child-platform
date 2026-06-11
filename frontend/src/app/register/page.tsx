import Link from "next/link";
import { Nav } from "@/components/Nav";
import { Footer } from "@/components/Footer";
import { RegisterForm } from "./RegisterForm";

export const metadata = {
  title: "Create an account — Treasured Child School",
  description:
    "Open an account at Treasured Child School in Orerokpe, Delta State.",
};

export default function RegisterPage() {
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
            Create an account
          </span>
          <h1 className="font-display font-bold text-paper text-[clamp(34px,5vw,56px)] leading-[1.08] tracking-tight mb-2.5">
            Open your account.
          </h1>
          <p className="text-[17px] text-muted max-w-[640px]">
            Parents and guardians register here. Your child&apos;s learner
            profile is linked to this account.
          </p>
        </div>
      </header>

      {/* ===== Form ===== */}
      <section className="px-[6vw] py-14 max-w-[560px] mx-auto">
        <RegisterForm />
        <p className="text-muted text-[14px] text-center mt-6">
          Already have an account?{" "}
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

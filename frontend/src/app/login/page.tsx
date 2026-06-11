import Link from "next/link";
import { Nav } from "@/components/Nav";
import { Footer } from "@/components/Footer";
import { LoginForm } from "./LoginForm";

export const metadata = {
  title: "Sign in — Treasured Child School",
  description: "Sign in to your Treasured Child account.",
};

export default function LoginPage() {
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
            Sign in
          </span>
          <h1 className="font-display font-bold text-paper text-[clamp(34px,5vw,56px)] leading-[1.08] tracking-tight mb-2.5">
            Welcome back.
          </h1>
          <p className="text-[17px] text-muted max-w-[640px]">
            Parents, learners and staff sign in here.
          </p>
        </div>
      </header>

      {/* ===== Form ===== */}
      <section className="px-[6vw] py-14 max-w-[480px] mx-auto">
        <LoginForm />
        <p className="text-muted text-[14px] text-center mt-6">
          No account yet?{" "}
          <Link
            href="/register"
            className="text-blue-soft font-semibold hover:underline"
          >
            Create one
          </Link>
          .
        </p>
      </section>

      <Footer />
    </>
  );
}

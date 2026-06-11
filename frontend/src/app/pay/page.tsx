import Link from "next/link";
import Script from "next/script";
import { Nav } from "@/components/Nav";
import { Footer } from "@/components/Footer";
import { PayForm } from "./PayForm";

export const metadata = {
  title: "Pay fees online — Treasured Child School",
  description:
    "Pay term fees or enrol in a paid online programme via Paystack.",
};

export default function PayPage() {
  return (
    <>
      <Nav />

      {/* Paystack inline widget — loaded lazily. Adds window.PaystackPop. */}
      <Script
        src="https://js.paystack.co/v1/inline.js"
        strategy="lazyOnload"
      />

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
            Pay online
          </span>
          <h1 className="font-display font-bold text-paper text-[clamp(34px,5vw,56px)] leading-[1.08] tracking-tight mb-2.5">
            Pay fees or enrol.
          </h1>
          <p className="text-[17px] text-muted max-w-[640px]">
            Secure payment via Paystack. You must be signed in to your
            account.
          </p>
        </div>
      </header>

      {/* ===== Form ===== */}
      <section className="px-[6vw] py-14 max-w-[560px] mx-auto">
        <PayForm />
        <p className="text-muted text-[14px] text-center mt-6">
          Not signed in?{" "}
          <Link
            href="/login"
            className="text-blue-soft font-semibold hover:underline"
          >
            Sign in
          </Link>
          {" "}or{" "}
          <Link
            href="/register"
            className="text-blue-soft font-semibold hover:underline"
          >
            create an account
          </Link>
          .
        </p>
      </section>

      <Footer />
    </>
  );
}

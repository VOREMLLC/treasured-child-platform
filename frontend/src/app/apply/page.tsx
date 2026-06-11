import { Nav } from "@/components/Nav";
import { Footer } from "@/components/Footer";
import { ApplyForm } from "./ApplyForm";

export const metadata = {
  title: "Apply — Treasured Child School",
  description:
    "Apply for a place at Treasured Child School in Orerokpe, Delta State. We respond within 48 hours.",
};

export default function ApplyPage() {
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
            Admissions
          </span>
          <h1 className="font-display font-bold text-paper text-[clamp(34px,5vw,56px)] leading-[1.08] tracking-tight mb-2.5">
            Apply for admission.
          </h1>
          <p className="text-[17px] text-muted max-w-[640px]">
            Tell us about your child. We&apos;ll reply by email within 48
            hours with next steps.
          </p>
        </div>
      </header>

      {/* ===== Form ===== */}
      <section className="px-[6vw] py-14 max-w-[820px] mx-auto">
        <ApplyForm />
      </section>

      <Footer />
    </>
  );
}

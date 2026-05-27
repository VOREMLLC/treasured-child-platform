import Link from "next/link";
import Image from "next/image";
import { Nav } from "@/components/Nav";
import { Footer } from "@/components/Footer";
import { SectionHead } from "@/components/SectionHead";

export default function Home() {
  return (
    <>
      <Nav />

      {/* ===== Hero ===== */}
      <header
        className="px-[6vw] pt-[70px] pb-[84px]"
        style={{
          background:
            "radial-gradient(900px 520px at 82% -10%, rgba(47,127,212,0.18) 0, transparent 60%), var(--bg)",
        }}
      >
        <div className="grid md:grid-cols-[1.05fr_.95fr] gap-11 items-center max-w-[1180px] mx-auto">
          <div>
            <span className="inline-flex items-center gap-2 text-[12px] font-bold uppercase tracking-[0.20em] text-gold mb-4">
              <span className="w-[7px] h-[7px] bg-gold rotate-45 inline-block" />
              Treasured Child School, Orerokpe
            </span>
            <h1 className="font-display font-bold text-paper text-[clamp(34px,5vw,56px)] leading-[1.08] tracking-tight mb-2.5">
              A school where every child is treasured.
            </h1>
            <p className="font-display italic text-gold text-[clamp(17px,2.3vw,22px)] mb-4">
              Knowledge · character · purpose.
            </p>
            <p className="text-[17px] text-muted max-w-[500px] mb-6">
              Nursery, primary and secondary in Delta State — and a growing set
              of online programmes that bring our classrooms to learners
              anywhere in Nigeria.
            </p>

            <div className="flex flex-wrap gap-3">
              <Link
                href="/apply"
                className="inline-flex items-center px-5 py-3 rounded-pill bg-gradient-to-b from-blue to-blue-deep text-white text-[15px] font-semibold shadow-[0_10px_24px_-10px_rgba(31,99,201,0.55)] hover:from-blue-bright transition"
              >
                Apply for admission
              </Link>
              <Link
                href="/pay"
                className="inline-flex items-center px-5 py-3 rounded-pill bg-gradient-to-b from-gold to-gold-deep text-ink text-[15px] font-semibold hover:brightness-105 transition"
              >
                Pay fees online
              </Link>
              <Link
                href="/login"
                className="inline-flex items-center px-5 py-3 rounded-pill border border-line text-paper text-[15px] font-semibold hover:border-blue-bright transition"
              >
                Student portal
              </Link>
            </div>

            <div className="flex flex-wrap gap-8 mt-8">
              <Stat value="From 18 to 200" label="learners since founding" />
              <Stat value="3 acres" label="of campus in Orerokpe" />
              <Stat value="K–12" label="nursery to senior secondary" />
            </div>
          </div>

          <div className="grid place-items-center order-first md:order-none">
            <span className="bg-white rounded-xl shadow-s p-7 inline-flex">
              <Image
                src="/logo.png"
                alt=""
                width={240}
                height={196}
                className="object-contain w-[180px] h-[148px] md:w-[240px] md:h-[196px]"
                priority
              />
            </span>
          </div>
        </div>
      </header>

      {/* ===== Why us ===== */}
      <section id="why" className="px-[6vw] py-16 max-w-[1180px] mx-auto">
        <SectionHead
          kicker="Why families choose us"
          heading="Strong teaching, warm community, real outcomes."
          sub="We pair classroom discipline with modern tools, so children learn how to think — not just what to memorise."
        />
        <div className="grid md:grid-cols-3 gap-6">
          <FeatureCard number="01" title="Small class sizes">
            Every learner is known by name. Teachers know each child&apos;s
            pace, strengths and gaps.
          </FeatureCard>
          <FeatureCard number="02" title="Modern curriculum">
            Foundational subjects plus digital literacy and AI fundamentals —
            preparing children for the world they will live in.
          </FeatureCard>
          <FeatureCard number="03" title="Safe and structured">
            Strict child-safety guardrails apply on campus and inside our
            online lessons. Parents stay informed.
          </FeatureCard>
        </div>
      </section>

      {/* ===== Programmes ===== */}
      <section
        id="programmes"
        className="px-[6vw] py-16 max-w-[1180px] mx-auto"
      >
        <SectionHead
          kicker="Programmes"
          heading="School and online — one platform, two engines."
          sub="Three featured programmes to start with. The full catalogue opens after sign-in."
        />
        <div className="grid md:grid-cols-3 gap-6">
          <ProgrammeCard
            bandGradient="linear-gradient(135deg, var(--blue-deep), var(--navy))"
            bandLabel="Junior secondary"
            pill="School · on campus"
            title="JSS 1–3"
          >
            The core academic years that prepare learners for BECE and senior
            secondary.
          </ProgrammeCard>
          <ProgrammeCard
            bandGradient="linear-gradient(135deg, var(--blue), var(--blue-bright))"
            bandLabel="BECE prep"
            pill="Online · paid"
            title="Common entrance & BECE"
          >
            Targeted online practice in maths, English and verbal reasoning
            with the AI tutor on hand.
          </ProgrammeCard>
          <ProgrammeCard
            bandGradient="linear-gradient(135deg, var(--gold-deep), var(--gold))"
            bandTextColor="#2a1f00"
            bandLabel="AI & data"
            pill="Online · flagship"
            pillVariant="gold"
            title="AI & data analytics"
          >
            An accessible introduction to AI and data — designed for ages 12+.
            Project-based, with safety guardrails throughout.
          </ProgrammeCard>
        </div>
      </section>

      {/* ===== CTA band ===== */}
      <section
        id="apply"
        className="px-[6vw] py-16 max-w-[1180px] mx-auto text-center"
      >
        <SectionHead
          kicker="Ready to apply?"
          heading="Take the next step."
          sub="Online application takes about three minutes. We'll be in touch within 48 hours."
        />
        <div className="flex flex-wrap gap-3 justify-center">
          <Link
            href="/apply"
            className="inline-flex items-center px-5 py-3 rounded-pill bg-gradient-to-b from-blue to-blue-deep text-white font-semibold shadow-[0_10px_24px_-10px_rgba(31,99,201,0.55)] hover:from-blue-bright transition"
          >
            Apply for admission
          </Link>
          <Link
            href="/contact"
            className="inline-flex items-center px-5 py-3 rounded-pill border border-line text-paper font-semibold hover:border-blue-bright transition"
          >
            Talk to admissions
          </Link>
        </div>
      </section>

      <Footer />
    </>
  );
}

/* ---- Page-specific helpers (only used on this page) ---- */

function Stat({ value, label }: { value: string; label: string }) {
  return (
    <div className="flex flex-col gap-1">
      <b className="font-display text-[28px] font-bold text-paper leading-none">
        {value}
      </b>
      <span className="text-[12.5px] text-muted">{label}</span>
    </div>
  );
}

function FeatureCard({
  number,
  title,
  children,
}: {
  number: string;
  title: string;
  children: React.ReactNode;
}) {
  return (
    <article className="bg-card border border-line rounded-lg p-6 transition hover:-translate-y-1 hover:shadow hover:border-blue-deep">
      <div className="w-11 h-11 rounded-md grid place-items-center mb-3.5 bg-gradient-to-b from-blue to-blue-deep text-white font-display text-[20px] font-semibold">
        {number}
      </div>
      <h3 className="font-display text-[19px] text-paper mb-1.5">{title}</h3>
      <p className="text-muted text-[14.5px]">{children}</p>
    </article>
  );
}

function ProgrammeCard({
  bandGradient,
  bandLabel,
  bandTextColor = "#fff",
  pill,
  pillVariant = "blue",
  title,
  children,
}: {
  bandGradient: string;
  bandLabel: string;
  bandTextColor?: string;
  pill: string;
  pillVariant?: "blue" | "gold";
  title: string;
  children: React.ReactNode;
}) {
  return (
    <article className="bg-card border border-line rounded-lg overflow-hidden flex flex-col transition hover:-translate-y-1 hover:shadow">
      <div
        className="h-24 grid place-items-center font-display text-[24px] tracking-tight"
        style={{ background: bandGradient, color: bandTextColor }}
      >
        {bandLabel}
      </div>
      <div className="p-5 pt-5 pb-6">
        <span
          className={
            "inline-block text-[12px] font-semibold px-2.5 py-1 rounded-pill " +
            (pillVariant === "gold"
              ? "bg-[rgba(239,183,0,0.14)] text-gold"
              : "bg-[rgba(47,127,212,0.14)] text-blue-soft")
          }
        >
          {pill}
        </span>
        <h3 className="font-display text-[19px] text-paper mt-2 mb-1.5">
          {title}
        </h3>
        <p className="text-muted text-[14.5px] mb-3.5">{children}</p>
        <a href="#" className="text-blue-soft font-semibold text-[14px]">
          Learn more →
        </a>
      </div>
    </article>
  );
}

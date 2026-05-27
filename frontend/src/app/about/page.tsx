import Link from "next/link";
import { Nav } from "@/components/Nav";
import { Footer } from "@/components/Footer";
import { SectionHead } from "@/components/SectionHead";

export const metadata = {
  title: "About — Treasured Child School",
  description:
    "Our school, our story. A K–12 school in Orerokpe, Delta State — now teaching online too.",
};

export default function About() {
  return (
    <>
      <Nav />

      {/* ===== Page header ===== */}
      <header
        className="px-[6vw] pt-[70px] pb-14"
        style={{
          background:
            "radial-gradient(900px 520px at 82% -10%, rgba(47,127,212,0.18) 0, transparent 60%), var(--bg)",
        }}
      >
        <div className="max-w-[1180px] mx-auto">
          <span className="inline-flex items-center gap-2 text-[12px] font-bold uppercase tracking-[0.20em] text-gold mb-4">
            <span className="w-[7px] h-[7px] bg-gold rotate-45 inline-block" />
            About Treasured Child
          </span>
          <h1 className="font-display font-bold text-paper text-[clamp(34px,5vw,56px)] leading-[1.08] tracking-tight mb-2.5">
            Our school, our story.
          </h1>
          <p className="font-display italic text-gold text-[clamp(17px,2.3vw,22px)] mb-4">
            Knowledge · character · purpose.
          </p>
          <p className="text-[17px] text-muted max-w-[640px]">
            Treasured Child is a nursery, primary and secondary school in
            Orerokpe, Delta State, Nigeria — and a growing online platform
            that brings our classrooms to learners anywhere in the country.
          </p>
        </div>
      </header>

      {/* ===== School story ===== */}
      <section className="px-[6vw] py-16 max-w-[820px] mx-auto">
        <SectionHead
          kicker="Our story"
          heading="From 18 learners to 200 — on reputation alone."
        />
        <div className="space-y-5 text-[16.5px] text-muted leading-relaxed">
          <p>
            Treasured Child was founded with a simple conviction:{" "}
            <strong className="text-paper">every child is treasured</strong>{" "}
            — and a school&apos;s job is to honour that, academically, in
            character, and in the small habits of daily life.
          </p>
          <p>
            We started small. Word travelled. Parents who saw their first
            child blossom brought the second; neighbours followed. The school
            has grown from 18 learners to more than 200 without a single
            advertisement — on reputation alone.
          </p>
          <p>
            The campus sits on three acres in Orerokpe. We teach the full
            K–12 ladder — nursery, primary, junior secondary and senior
            secondary — and we now extend the same care to online learners
            through paid programmes in exam preparation and an accessible
            introduction to AI and data analytics.
          </p>
        </div>
      </section>

      {/* ===== Values ===== */}
      <section className="px-[6vw] py-12 max-w-[1180px] mx-auto">
        <SectionHead
          kicker="What we stand for"
          heading="Three things we won't compromise on."
        />
        <div className="grid md:grid-cols-3 gap-6">
          <ValueCard title="Care for every child">
            Every learner is known by name. Class sizes stay small so a
            teacher can meet each child where they are.
          </ValueCard>
          <ValueCard title="A strong academic foundation">
            Reading, writing, mathematics and science come first. Everything
            else builds on top of that.
          </ValueCard>
          <ValueCard title="Modern tools, child-safe">
            Digital literacy and AI fundamentals belong in the curriculum —
            with strict guardrails for the children using them.
          </ValueCard>
        </div>
      </section>

      {/* ===== Leadership ===== */}
      <section
        id="leadership"
        className="px-[6vw] py-16 max-w-[1180px] mx-auto"
      >
        <SectionHead
          kicker="Leadership"
          heading="The people who run the school."
          sub="Names, photos and biographies will appear here once the proprietor supplies them. We do not list invented credentials."
        />
        <div className="grid md:grid-cols-3 gap-6">
          <LeaderPlaceholder role="Proprietor" />
          <LeaderPlaceholder role="Head teacher" />
          <LeaderPlaceholder role="Head of online programmes" />
        </div>
      </section>

      {/* ===== Visit / contact CTA ===== */}
      <section className="px-[6vw] py-16 max-w-[1180px] mx-auto text-center">
        <SectionHead
          kicker="Visit"
          heading="Come and see for yourself."
          sub="Orerokpe, Delta State, Nigeria. We welcome enquiries by email or phone; campus visits are by appointment."
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

/* ---- Page-specific helpers ---- */

function ValueCard({
  title,
  children,
}: {
  title: string;
  children: React.ReactNode;
}) {
  return (
    <article className="bg-card border border-line rounded-lg p-6 transition hover:-translate-y-1 hover:shadow hover:border-blue-deep">
      <h3 className="font-display text-[19px] text-paper mb-2">{title}</h3>
      <p className="text-muted text-[14.5px]">{children}</p>
    </article>
  );
}

function LeaderPlaceholder({ role }: { role: string }) {
  return (
    <article className="bg-card border border-line rounded-lg p-6">
      <div
        aria-hidden
        className="w-16 h-16 rounded-full bg-gradient-to-b from-blue-deep to-navy grid place-items-center mb-4"
      >
        <span className="font-display font-semibold text-paper text-[22px]">
          —
        </span>
      </div>
      <h3 className="font-display text-[18px] text-paper mb-1">{role}</h3>
      <p className="text-muted text-[13.5px]">
        Name and biography to be supplied by the proprietor.
      </p>
    </article>
  );
}

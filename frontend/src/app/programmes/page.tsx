import { Nav } from "@/components/Nav";
import { Footer } from "@/components/Footer";
import { SectionHead } from "@/components/SectionHead";
import { ProgrammeCard } from "@/components/ProgrammeCard";
import {
  getSchoolProgrammes,
  getOnlineProgrammes,
} from "@/lib/programmes";

export const metadata = {
  title: "Programmes — Treasured Child School",
  description:
    "Our nursery, primary, junior and senior secondary programmes, plus online courses for learners anywhere in Nigeria.",
};

export default function Programmes() {
  const school = getSchoolProgrammes();
  const online = getOnlineProgrammes();

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
            Programmes
          </span>
          <h1 className="font-display font-bold text-paper text-[clamp(34px,5vw,56px)] leading-[1.08] tracking-tight mb-2.5">
            School and online — one platform, two engines.
          </h1>
          <p className="text-[17px] text-muted max-w-[640px]">
            On-campus K–12 in Orerokpe, plus paid online programmes for
            learners anywhere in Nigeria. Click any programme to see the
            details.
          </p>
        </div>
      </header>

      {/* ===== On campus ===== */}
      <section className="px-[6vw] py-14 max-w-[1180px] mx-auto">
        <SectionHead
          kicker="On campus"
          heading="Our school programmes."
          sub="The full K–12 ladder, taught in person at our Orerokpe campus."
        />
        <div className="grid md:grid-cols-2 lg:grid-cols-2 gap-6">
          {school.map((p) => (
            <ProgrammeCard
              key={p.slug}
              href={`/programmes/${p.slug}`}
              bandGradient={p.bandGradient}
              bandLabel={p.bandLabel}
              bandTextColor={p.bandTextColor}
              pill={p.pill}
              pillVariant={p.pillVariant}
              title={p.title}
            >
              {p.summary}
            </ProgrammeCard>
          ))}
        </div>
      </section>

      {/* ===== Online ===== */}
      <section className="px-[6vw] py-14 max-w-[1180px] mx-auto">
        <SectionHead
          kicker="Online"
          heading="Paid online programmes."
          sub="For learners anywhere in Nigeria. Child-safe by design — every AI reply passes through the VOREM safety guardrails."
        />
        <div className="grid md:grid-cols-2 gap-6">
          {online.map((p) => (
            <ProgrammeCard
              key={p.slug}
              href={`/programmes/${p.slug}`}
              bandGradient={p.bandGradient}
              bandLabel={p.bandLabel}
              bandTextColor={p.bandTextColor}
              pill={p.pill}
              pillVariant={p.pillVariant}
              title={p.title}
            >
              {p.summary}
            </ProgrammeCard>
          ))}
        </div>
      </section>

      <Footer />
    </>
  );
}

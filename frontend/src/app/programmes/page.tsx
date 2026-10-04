import { Footer } from "@/components/Footer";
import { Nav } from "@/components/Nav";
import { PageHeader } from "@/components/PageHeader";
import { ProgrammeCard } from "@/components/ProgrammeCard";
import { getOnlineProgrammes, getSchoolProgrammes } from "@/lib/programmes";

export const metadata = {
  title: "Programmes | Treasured Child School",
  description:
    "Nursery, primary, junior and senior secondary on campus, plus online courses for learners anywhere in Nigeria.",
};

export default function Programmes() {
  return (
    <>
      <Nav />
      <PageHeader
        title="Programmes and fees"
        lead="Classes on our Orerokpe campus, and online courses your child can take from anywhere."
      />

      <main>
        <section className="wrap py-8" aria-labelledby="campus">
          <h2 id="campus" className="mb-1 font-display text-[28px] font-bold text-ink sm:text-h3">
            At our school
          </h2>
          <p className="mb-6 text-body text-muted">Nursery all the way to SS 3.</p>
          <div className="grid gap-4 sm:grid-cols-2">
            {getSchoolProgrammes().map((p) => (
              <ProgrammeCard key={p.slug} programme={p} />
            ))}
          </div>
        </section>

        <section className="wrap py-8" aria-labelledby="online">
          <h2 id="online" className="mb-1 font-display text-[28px] font-bold text-ink sm:text-h3">
            Online courses
          </h2>
          <p className="mb-6 text-body text-muted">
            Learn on a phone from anywhere in Nigeria, with a safe helper in
            every lesson.
          </p>
          <div className="grid gap-4 sm:grid-cols-2">
            {getOnlineProgrammes().map((p) => (
              <ProgrammeCard key={p.slug} programme={p} />
            ))}
          </div>
        </section>
      </main>

      <Footer />
    </>
  );
}

import Link from "next/link";
import { notFound } from "next/navigation";
import { Nav } from "@/components/Nav";
import { Footer } from "@/components/Footer";
import { PROGRAMMES, getProgramme } from "@/lib/programmes";

interface PageProps {
  params: { slug: string };
}

export function generateStaticParams() {
  return PROGRAMMES.map((p) => ({ slug: p.slug }));
}

export function generateMetadata({ params }: PageProps) {
  const p = getProgramme(params.slug);
  if (!p) return { title: "Programme — Treasured Child School" };
  return {
    title: `${p.title} — Treasured Child School`,
    description: p.summary,
  };
}

export default function ProgrammeDetail({ params }: PageProps) {
  const p = getProgramme(params.slug);
  if (!p) notFound();

  const enrolHref =
    p.kind === "online"
      ? `/login?redirect=/programmes/${p.slug}`
      : "/apply";
  const enrolLabel =
    p.kind === "online" ? "Enrol online" : "Apply for admission";

  return (
    <>
      <Nav />

      {/* ===== Coloured band header ===== */}
      <header
        className="px-[6vw] pt-[68px] pb-14"
        style={{ background: p.bandGradient, color: p.bandTextColor ?? "#fff" }}
      >
        <div className="max-w-[1180px] mx-auto">
          <Link
            href="/programmes"
            className="inline-flex items-center gap-1.5 text-[13px] font-semibold opacity-80 hover:opacity-100 transition mb-4"
          >
            ← All programmes
          </Link>
          <span
            className={
              "inline-block text-[12px] font-semibold px-2.5 py-1 rounded-pill mb-3 " +
              (p.pillVariant === "gold"
                ? "bg-[rgba(0,0,0,0.18)] text-current"
                : "bg-[rgba(255,255,255,0.18)] text-current")
            }
          >
            {p.pill}
          </span>
          <h1 className="font-display font-bold text-[clamp(32px,5vw,52px)] leading-[1.08] tracking-tight mb-2.5">
            {p.title}
          </h1>
          <p className="text-[17px] max-w-[640px] opacity-90">{p.summary}</p>
          <div className="flex flex-wrap gap-3 mt-6 text-[13px] font-medium opacity-85">
            <Meta label="Level" value={p.level} />
            <Meta label="Age range" value={p.ageRange} />
            <Meta
              label="Type"
              value={p.kind === "online" ? "Online" : "On campus"}
            />
            {p.isPaid && <Meta label="Pricing" value="Paid · see below" />}
          </div>
        </div>
      </header>

      {/* ===== Body ===== */}
      <article className="px-[6vw] py-14 max-w-[820px] mx-auto">
        <h2 className="font-display text-[24px] text-paper mb-4">
          About the programme
        </h2>
        <div className="space-y-4 text-[16.5px] text-muted leading-relaxed">
          {p.description.map((para, i) => (
            <p key={i}>{para}</p>
          ))}
        </div>

        <h2 className="font-display text-[24px] text-paper mt-12 mb-4">
          What&apos;s included
        </h2>
        <ul className="space-y-2 text-[15.5px] text-muted">
          {p.whatsIncluded.map((item, i) => (
            <li key={i} className="flex gap-3">
              <span
                aria-hidden
                className="mt-2 w-1.5 h-1.5 rounded-full bg-blue-bright flex-none"
              />
              <span>{item}</span>
            </li>
          ))}
        </ul>

        {p.priceNote && (
          <div className="mt-10 border border-line rounded-lg p-5 bg-card">
            <div className="text-[12px] font-bold uppercase tracking-[0.18em] text-gold mb-1">
              Pricing
            </div>
            <p className="text-paper text-[15.5px]">{p.priceNote}</p>
          </div>
        )}

        <div className="mt-12 flex flex-wrap gap-3">
          <Link
            href={enrolHref}
            className="inline-flex items-center px-5 py-3 rounded-pill bg-gradient-to-b from-blue to-blue-deep text-white font-semibold shadow-[0_10px_24px_-10px_rgba(31,99,201,0.55)] hover:from-blue-bright transition"
          >
            {enrolLabel}
          </Link>
          <Link
            href="/contact"
            className="inline-flex items-center px-5 py-3 rounded-pill border border-line text-paper font-semibold hover:border-blue-bright transition"
          >
            Talk to admissions
          </Link>
        </div>
      </article>

      <Footer />
    </>
  );
}

function Meta({ label, value }: { label: string; value: string }) {
  return (
    <span className="inline-flex items-center gap-1.5">
      <span className="opacity-70">{label}:</span>
      <span className="font-semibold">{value}</span>
    </span>
  );
}


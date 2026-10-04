import Link from "next/link";
import { notFound } from "next/navigation";

import { ButtonLink } from "@/components/Button";
import { Footer } from "@/components/Footer";
import { Icon } from "@/components/Icon";
import { Nav } from "@/components/Nav";
import { PageHeader } from "@/components/PageHeader";
import { PROGRAMMES, formatNaira, getProgramme } from "@/lib/programmes";

interface PageProps {
  params: { slug: string };
}

export function generateStaticParams() {
  return PROGRAMMES.map((p) => ({ slug: p.slug }));
}

export function generateMetadata({ params }: PageProps) {
  const p = getProgramme(params.slug);
  if (!p) return { title: "Programme | Treasured Child School" };
  return {
    title: `${p.title} | Treasured Child School`,
    description: p.summary,
  };
}

export default function ProgrammeDetail({ params }: PageProps) {
  const p = getProgramme(params.slug);
  if (!p) notFound();

  const online = p.kind === "online";

  return (
    <>
      <Nav />
      <PageHeader
        title={p.title}
        lead={p.summary}
        above={
          <Link
            href="/programmes"
            className="inline-flex min-h-12 items-center gap-2 text-body font-bold text-muted hover:text-blue-ink"
          >
            <Icon name="arrow-left" size={20} />
            All programmes
          </Link>
        }
      >
        <ul className="flex flex-wrap gap-2 text-caption font-semibold">
          <li className="rounded-full bg-surface px-3 py-1.5 text-ink shadow-s">
            {online ? "Online" : "On campus"}
          </li>
          <li className="rounded-full bg-surface px-3 py-1.5 text-ink shadow-s">
            {p.ageRange}
          </li>
        </ul>
      </PageHeader>

      <main className="wrap grid gap-10 py-10 md:grid-cols-[1fr_340px] md:items-start">
        <article className="max-w-[62ch]">
          <div className="space-y-4 text-body text-muted">
            {p.description.map((para, i) => (
              <p key={i}>{para}</p>
            ))}
          </div>

          <h2 className="mb-4 mt-10 font-display text-title font-bold text-ink sm:text-h3">
            What your child gets
          </h2>
          <ul className="space-y-3">
            {p.whatsIncluded.map((item) => (
              <li key={item} className="flex items-start gap-3 text-body text-ink">
                <span className="mt-0.5 grid h-7 w-7 shrink-0 place-items-center rounded-full bg-success-soft text-success">
                  <Icon name="check" size={18} strokeWidth={3} />
                </span>
                {item}
              </li>
            ))}
          </ul>
        </article>

        <aside className="rounded-card border border-line bg-card p-5 shadow-s md:sticky md:top-24">
          <p className="text-caption font-semibold text-muted">Fees</p>
          <p className="font-display text-h3 font-bold text-ink">
            {formatNaira(p.priceNaira)}
          </p>
          <p className="mb-5 text-body text-muted">{p.pricePer}</p>
          <ButtonLink href={online ? `/pay?for=${p.slug}` : "/apply"} size="lg" full>
            {online ? "Pay fees" : "Apply now"}
          </ButtonLink>
          <Link
            href="/contact"
            className="mt-2 inline-flex min-h-12 w-full items-center justify-center text-body font-bold text-blue-ink"
          >
            Questions? Talk to us
          </Link>
        </aside>
      </main>

      <Footer />
    </>
  );
}

import Image from "next/image";

import { ButtonLink } from "@/components/Button";
import { Footer } from "@/components/Footer";
import { Icon, type IconName } from "@/components/Icon";
import { Nav } from "@/components/Nav";
import { ProgrammeCard } from "@/components/ProgrammeCard";
import { getProgramme, type Programme } from "@/lib/programmes";

const FEATURED = ["primary", "junior-secondary", "bece-prep", "ai-data"]
  .map((slug) => getProgramme(slug))
  .filter((p): p is Programme => p !== undefined);

export default function Home() {
  return (
    <>
      <Nav />

      {/* ===== Hero ===== */}
      <header className="overflow-hidden bg-[linear-gradient(180deg,var(--blue-soft),var(--bg))]">
        <div className="wrap grid items-center gap-10 py-10 sm:py-16 md:grid-cols-[1.1fr_.9fr]">
          <div>
            <h1 className="max-w-[16ch] font-display text-[36px] font-bold text-ink sm:text-h1 lg:text-[52px]">
              A school where every child is treasured.
            </h1>
            <p className="mt-4 max-w-[46ch] text-label text-muted">
              Nursery to secondary in Orerokpe, Delta State, plus online
              classes your child can take from anywhere in Nigeria.
            </p>
            <div className="mt-8 flex flex-col gap-3 sm:flex-row">
              <ButtonLink href="/apply" size="lg">
                Apply now
              </ButtonLink>
              <ButtonLink href="/pay" size="lg" variant="secondary" icon="card">
                Pay fees
              </ButtonLink>
            </div>
          </div>

          <HeroArt />
        </div>
      </header>

      {/* ===== Stats ===== */}
      <section aria-label="About the school in numbers" className="wrap">
        <dl className="grid grid-cols-3 gap-3 rounded-card border border-line bg-card p-4 shadow-s sm:p-6">
          <Stat value="200+" label="happy learners" />
          <Stat value="3 acres" label="of green campus" />
          <Stat value="Ages 3 to 17" label="nursery to SS 3" />
        </dl>
      </section>

      {/* ===== Why families choose us: alternating rows ===== */}
      <section className="wrap py-16">
        <h2 className="max-w-[22ch] font-display text-[28px] font-bold text-ink sm:text-h2">
          Why families choose Treasured Child
        </h2>
        <div className="mt-10 space-y-12">
          <WhyRow
            icon="heart"
            tone="blue"
            title="Every child is known by name"
            body="Classes stay small, so teachers see each child's pace, strengths and gaps. Many of our families came because a neighbour told them."
          />
          <WhyRow
            flip
            icon="sparkle"
            tone="gold"
            title="Strong basics, ready for tomorrow"
            body="Reading, writing and maths come first. On top of that, children learn computers and the basics of AI, with safe tools made for young people."
          />
          <WhyRow
            icon="shield"
            tone="blue"
            title="Safe on campus and online"
            body="Our online helper only talks about the lesson, never asks for personal details, and passes worries to a real teacher. Parents stay in the loop."
          />
        </div>
      </section>

      {/* ===== Programmes ===== */}
      <section id="programmes" className="wrap py-8">
        <div className="mb-6 flex flex-wrap items-end justify-between gap-4">
          <h2 className="font-display text-[28px] font-bold text-ink sm:text-h2">
            Programmes and fees
          </h2>
          <ButtonLink href="/programmes" variant="ghost" iconRight="arrow-right">
            See all programmes
          </ButtonLink>
        </div>
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {FEATURED.map((p) => (
            <ProgrammeCard key={p.slug} programme={p} />
          ))}
        </div>
      </section>

      {/* ===== Closing call to action ===== */}
      <section className="wrap py-16">
        <div className="relative overflow-hidden rounded-card bg-navy px-6 py-10 text-white sm:px-12">
          <span
            aria-hidden
            className="absolute -right-10 -top-10 h-40 w-40 rounded-full bg-gold opacity-90"
          />
          <h2 className="relative max-w-[20ch] font-display text-[28px] font-bold sm:text-h2">
            Ready when you are.
          </h2>
          <p className="relative mt-2 max-w-[44ch] text-label opacity-90">
            Applying takes about two minutes. We&apos;ll call or WhatsApp
            you within 48 hours.
          </p>
          <div className="relative mt-6 flex flex-col gap-3 sm:flex-row">
            <ButtonLink href="/apply" size="lg" className="!bg-white !text-navy hover:!bg-blue-soft">
              Apply now
            </ButtonLink>
          </div>
        </div>
      </section>

      <Footer />
    </>
  );
}

/* ---- Page helpers ---- */

/**
 * Brand composition shown in place of photos.
 * TODO(photos): when real campus photos arrive, add them to /public and
 * swap the logo below for e.g.
 *   <Image src="/campus/hero.jpg" alt="Pupils at morning assembly"
 *          fill sizes="(min-width: 768px) 45vw, 90vw" className="object-cover" priority />
 * inside the rounded frame. Use real photos only, never stock.
 */
function HeroArt() {
  return (
    <div aria-hidden className="relative mx-auto aspect-square w-full max-w-[380px]">
      <span className="absolute inset-[6%] rounded-full bg-blue-soft" />
      <span className="absolute right-[4%] top-[6%] h-[26%] w-[26%] rounded-full bg-gold" />
      <span className="absolute bottom-[8%] left-[2%] h-[16%] w-[16%] rounded-full border-[6px] border-blue" />
      <span className="absolute bottom-[18%] right-[8%] grid h-14 w-14 place-items-center rounded-control bg-surface text-gold-text shadow">
        <Icon name="star" size={28} />
      </span>
      <span className="absolute left-[8%] top-[22%] grid h-14 w-14 place-items-center rounded-control bg-surface text-blue-ink shadow">
        <Icon name="book" size={28} />
      </span>
      <div className="absolute inset-[22%] grid place-items-center rounded-card bg-white p-4 shadow">
        <Image
          src="/logo.png"
          alt=""
          width={348}
          height={284}
          priority
          className="h-auto w-full object-contain"
        />
      </div>
    </div>
  );
}

function Stat({ value, label }: { value: string; label: string }) {
  return (
    <div className="flex flex-col-reverse text-center">
      <dt className="text-caption text-muted">{label}</dt>
      <dd className="font-display text-title font-bold text-ink sm:text-h3">
        {value}
      </dd>
    </div>
  );
}

function WhyRow({
  icon,
  tone,
  title,
  body,
  flip = false,
}: {
  icon: IconName;
  tone: "blue" | "gold";
  title: string;
  body: string;
  flip?: boolean;
}) {
  return (
    <div className="grid items-center gap-6 md:grid-cols-2 md:gap-12">
      <div
        aria-hidden
        className={`relative grid h-48 place-items-center overflow-hidden rounded-card sm:h-56 ${tone === "gold" ? "bg-gold-soft" : "bg-blue-soft"} ${flip ? "md:order-2" : ""}`}
      >
        <span
          className={`absolute -bottom-8 -left-8 h-32 w-32 rounded-full ${tone === "gold" ? "bg-gold" : "bg-blue"} opacity-20`}
        />
        <span
          className={`grid h-24 w-24 place-items-center rounded-full ${tone === "gold" ? "bg-gold text-ink" : "bg-blue text-white"}`}
        >
          <Icon name={icon} size={44} />
        </span>
      </div>
      <div>
        <h3 className="font-display text-title font-bold text-ink sm:text-h3">
          {title}
        </h3>
        <p className="mt-2 max-w-[48ch] text-body text-muted">{body}</p>
      </div>
    </div>
  );
}

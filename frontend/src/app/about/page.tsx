import { ButtonLink } from "@/components/Button";
import { Footer } from "@/components/Footer";
import { Icon, type IconName } from "@/components/Icon";
import { Nav } from "@/components/Nav";
import { PageHeader } from "@/components/PageHeader";

export const metadata = {
  title: "About us | Treasured Child School",
  description:
    "Our story. A nursery, primary and secondary school in Orerokpe, Delta State, now teaching online too.",
};

const VALUES: { icon: IconName; title: string; body: string }[] = [
  {
    icon: "heart",
    title: "Care for every child",
    body: "Every learner is known by name. Small classes let teachers meet each child where they are.",
  },
  {
    icon: "book",
    title: "Strong basics first",
    body: "Reading, writing, maths and science come first. Everything else builds on top.",
  },
  {
    icon: "shield",
    title: "Modern tools, kept safe",
    body: "Computers and AI belong in school today, with strict safety rules for the children using them.",
  },
];

export default function About() {
  return (
    <>
      <Nav />
      <PageHeader
        title="Our school, our story"
        lead="A nursery, primary and secondary school in Orerokpe, Delta State, now bringing our classrooms online for learners anywhere in Nigeria."
      />

      <main>
        <section className="wrap grid gap-10 py-12 md:grid-cols-[1.2fr_.8fr] md:items-start">
          <div className="max-w-[62ch] space-y-5 text-body text-muted">
            <h2 className="font-display text-[28px] font-bold text-ink sm:text-h3">
              From 18 learners to more than 200
            </h2>
            <p>
              Treasured Child began with one simple belief:{" "}
              <strong className="font-extrabold text-ink">every child is treasured</strong>.
              A school&apos;s job is to honour that in lessons, in character
              and in the small habits of every day.
            </p>
            <p>
              We started small. Parents who saw their first child blossom
              brought the second, and neighbours followed. We have grown from
              18 learners to more than 200 without a single advert.
            </p>
            <p>
              Our campus sits on three acres in Orerokpe. We teach every
              stage from nursery to senior secondary, and we now offer the same
              care online through exam preparation and a first course in AI
              and data.
            </p>
          </div>

          {/* TODO(photos): replace this panel with a real campus photo via
              next/image once the school supplies one. */}
          <div
            aria-hidden
            className="relative grid aspect-[4/3] place-items-center overflow-hidden rounded-card bg-blue-soft"
          >
            <span className="absolute -right-6 -top-6 h-28 w-28 rounded-full bg-gold" />
            <span className="absolute -bottom-10 -left-10 h-40 w-40 rounded-full bg-blue opacity-20" />
            <span className="grid h-24 w-24 place-items-center rounded-full bg-blue text-white">
              <Icon name="school" size={44} />
            </span>
          </div>
        </section>

        <section className="wrap py-8">
          <h2 className="mb-6 font-display text-[28px] font-bold text-ink sm:text-h3">
            What we stand for
          </h2>
          <ul className="divide-y divide-line rounded-card border border-line bg-card shadow-s">
            {VALUES.map((v) => (
              <li key={v.title} className="flex items-start gap-4 p-5">
                <span className="grid h-12 w-12 shrink-0 place-items-center rounded-control bg-blue-soft text-blue-ink">
                  <Icon name={v.icon} />
                </span>
                <div>
                  <h3 className="font-display text-title font-bold text-ink">{v.title}</h3>
                  <p className="text-body text-muted">{v.body}</p>
                </div>
              </li>
            ))}
          </ul>
        </section>

        {/* Leadership profiles go here once the school supplies real names,
            photos and short biographies. */}

        <section className="wrap py-12">
          <div className="flex flex-col items-start gap-4 rounded-card bg-gold-soft p-6 sm:flex-row sm:items-center sm:justify-between sm:p-8">
            <div>
              <h2 className="font-display text-title font-bold text-ink sm:text-h3">
                Come and see us
              </h2>
              <p className="text-body text-muted">
                Campus visits are by appointment. Call or WhatsApp to book.
              </p>
            </div>
            <div className="flex w-full flex-col gap-3 sm:w-auto sm:flex-row">
              <ButtonLink href="/apply">Apply now</ButtonLink>
              <ButtonLink href="/contact" variant="secondary">
                Contact us
              </ButtonLink>
            </div>
          </div>
        </section>
      </main>

      <Footer />
    </>
  );
}

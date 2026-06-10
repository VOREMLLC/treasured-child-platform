import { Nav } from "@/components/Nav";
import { Footer } from "@/components/Footer";
import { SectionHead } from "@/components/SectionHead";

export const metadata = {
  title: "Contact — Treasured Child School",
  description:
    "Visit, call or email Treasured Child School in Orerokpe, Delta State.",
};

export default function Contact() {
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
            Contact
          </span>
          <h1 className="font-display font-bold text-paper text-[clamp(34px,5vw,56px)] leading-[1.08] tracking-tight mb-2.5">
            Get in touch.
          </h1>
          <p className="text-[17px] text-muted max-w-[640px]">
            Email or call us during school hours, or send a short message
            using the form below. We respond to enquiries by email within
            one working day.
          </p>
        </div>
      </header>

      {/* ===== Contact details ===== */}
      <section className="px-[6vw] py-12 max-w-[1180px] mx-auto">
        <div className="grid md:grid-cols-3 gap-6">
          <DetailCard
            kicker="Visit us"
            heading="Orerokpe campus"
            body="Orerokpe, Delta State, Nigeria. Visits are welcome by appointment."
          />
          <DetailCard
            kicker="Call us"
            heading={
              <a
                href="tel:+2347035918488"
                className="hover:text-blue-soft transition"
              >
                +234 703 591 8488
              </a>
            }
            body="Direct line to the school office."
          />
          <DetailCard
            kicker="Email us"
            heading={
              <a
                href="mailto:hello@treasuredchild.example"
                className="hover:text-blue-soft transition"
              >
                hello@treasuredchild.example
              </a>
            }
            body="We reply by email within one working day."
          />
        </div>
      </section>

      {/* ===== Form + map placeholder ===== */}
      <section className="px-[6vw] py-14 max-w-[1180px] mx-auto">
        <div className="grid lg:grid-cols-[1.05fr_.95fr] gap-10">
          {/* Message form (client-only; submit disabled until S6) */}
          <div>
            <SectionHead kicker="Send a message" heading="Quick message" />
            <form className="bg-card border border-line rounded-lg p-6 space-y-4">
              <Field id="name" label="Your name">
                <input
                  id="name"
                  name="name"
                  type="text"
                  required
                  autoComplete="name"
                  className="w-full bg-page border border-line rounded-md px-3 py-2.5 text-paper text-[15px] focus:outline-none focus:border-blue-bright focus:shadow-[0_0_0_3px_rgba(47,127,212,0.25)] transition"
                />
              </Field>
              <Field id="email" label="Email">
                <input
                  id="email"
                  name="email"
                  type="email"
                  required
                  autoComplete="email"
                  className="w-full bg-page border border-line rounded-md px-3 py-2.5 text-paper text-[15px] focus:outline-none focus:border-blue-bright focus:shadow-[0_0_0_3px_rgba(47,127,212,0.25)] transition"
                />
              </Field>
              <Field id="subject" label="Subject">
                <input
                  id="subject"
                  name="subject"
                  type="text"
                  required
                  className="w-full bg-page border border-line rounded-md px-3 py-2.5 text-paper text-[15px] focus:outline-none focus:border-blue-bright focus:shadow-[0_0_0_3px_rgba(47,127,212,0.25)] transition"
                />
              </Field>
              <Field id="message" label="Message">
                <textarea
                  id="message"
                  name="message"
                  rows={5}
                  required
                  className="w-full bg-page border border-line rounded-md px-3 py-2.5 text-paper text-[15px] resize-y focus:outline-none focus:border-blue-bright focus:shadow-[0_0_0_3px_rgba(47,127,212,0.25)] transition"
                />
              </Field>
              <button
                type="submit"
                disabled
                aria-disabled
                className="inline-flex items-center px-5 py-3 rounded-pill bg-gradient-to-b from-blue to-blue-deep text-white font-semibold opacity-50 cursor-not-allowed"
              >
                Send message
              </button>
              <p className="text-muted text-[13px]">
                Form submission goes live in slice S6 — for now, please use
                the email or phone above.
              </p>
            </form>
          </div>

          {/* Map placeholder — no third-party embed until provider + coords are confirmed */}
          <div>
            <SectionHead kicker="Find us" heading="Map of campus" />
            <div className="bg-card border border-line rounded-lg overflow-hidden">
              <div
                aria-label="Map placeholder"
                className="h-[280px] grid place-items-center text-muted text-[14px]"
                style={{
                  background:
                    "repeating-linear-gradient(135deg, rgba(47,127,212,0.07) 0 14px, transparent 14px 28px)",
                }}
              >
                <div className="text-center px-6">
                  <div className="font-display text-paper text-[22px] mb-1">
                    Orerokpe, Delta State
                  </div>
                  <p className="text-[14px] max-w-[300px] mx-auto">
                    A real map embed lands when the proprietor confirms exact
                    coordinates and which map provider to use.
                  </p>
                </div>
              </div>
              <div className="p-5 border-t border-line">
                <p className="text-muted text-[14px]">
                  Visits to campus are welcome by appointment. Email us first
                  so we can arrange a guide.
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      <Footer />
    </>
  );
}

/* ---- Page-specific helpers ---- */

function DetailCard({
  kicker,
  heading,
  body,
}: {
  kicker: string;
  heading: React.ReactNode;
  body: string;
}) {
  return (
    <article className="bg-card border border-line rounded-lg p-6">
      <div className="text-[12px] font-bold uppercase tracking-[0.18em] text-gold mb-2">
        {kicker}
      </div>
      <h3 className="font-display text-[19px] text-paper mb-2">{heading}</h3>
      <p className="text-muted text-[14px]">{body}</p>
    </article>
  );
}

function Field({
  id,
  label,
  children,
}: {
  id: string;
  label: string;
  children: React.ReactNode;
}) {
  return (
    <div className="flex flex-col gap-1.5">
      <label htmlFor={id} className="text-[13px] font-semibold text-paper">
        {label}
      </label>
      {children}
    </div>
  );
}

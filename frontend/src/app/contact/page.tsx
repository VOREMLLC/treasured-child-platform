import { ButtonLink } from "@/components/Button";
import { Footer } from "@/components/Footer";
import { Icon } from "@/components/Icon";
import { Nav } from "@/components/Nav";
import { PageHeader } from "@/components/PageHeader";
import { SCHOOL_PHONE_DISPLAY, SCHOOL_PHONE_TEL, WHATSAPP_URL } from "@/lib/contact";

export const metadata = {
  title: "Contact us | Treasured Child School",
  description: "Call, WhatsApp or visit Treasured Child School in Orerokpe, Delta State.",
};

export default function Contact() {
  return (
    <>
      <Nav />
      <PageHeader
        narrow
        title="Talk to us"
        lead="The quickest way to reach us is WhatsApp or a phone call during school hours."
      />

      <main className="wrap max-w-[640px] space-y-6 pb-8">
        <div className="grid gap-3 sm:grid-cols-2">
          <ButtonLink href={WHATSAPP_URL} external size="lg" icon="whatsapp" full>
            WhatsApp us
          </ButtonLink>
          <ButtonLink href={SCHOOL_PHONE_TEL} external size="lg" variant="secondary" icon="phone" full>
            Call {SCHOOL_PHONE_DISPLAY}
          </ButtonLink>
        </div>

        <section className="flex items-start gap-4 rounded-card border border-line bg-card p-5 shadow-s">
          <span className="grid h-12 w-12 shrink-0 place-items-center rounded-control bg-blue-soft text-blue-ink">
            <Icon name="pin" />
          </span>
          <div>
            <h2 className="font-display text-title font-bold text-ink">Visit the campus</h2>
            <p className="text-body text-muted">
              Orerokpe, Delta State, Nigeria. Visits are by appointment, so
              send us a message first and we will arrange a guide.
            </p>
          </div>
        </section>

        {/* A map embed goes here once the exact campus location and map
            provider are confirmed. */}
      </main>

      <Footer />
    </>
  );
}

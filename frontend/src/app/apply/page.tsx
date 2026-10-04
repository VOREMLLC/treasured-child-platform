import { Nav } from "@/components/Nav";
import { Footer } from "@/components/Footer";
import { PageHeader } from "@/components/PageHeader";
import { ApplyForm } from "./ApplyForm";

export const metadata = {
  title: "Apply now | Treasured Child School",
  description:
    "Apply for a place at Treasured Child School in Orerokpe, Delta State. We reply within 48 hours.",
};

export default function ApplyPage() {
  return (
    <>
      <Nav />
      <PageHeader
        narrow
        title="Apply for a place"
        lead="It takes about two minutes. We'll call or WhatsApp you within 48 hours."
      />
      <main className="wrap max-w-[640px] pb-8">
        <ApplyForm />
      </main>
      <Footer />
    </>
  );
}

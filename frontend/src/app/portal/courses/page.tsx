import Link from "next/link";
import { Nav } from "@/components/Nav";
import { Footer } from "@/components/Footer";
import { CoursesList } from "./CoursesList";

export const metadata = {
  title: "My courses — Treasured Child School",
  description: "The courses you are enrolled in.",
};

export default function CoursesPage() {
  return (
    <>
      <Nav />

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
            My courses
          </span>
          <h1 className="font-display font-bold text-paper text-[clamp(34px,5vw,56px)] leading-[1.08] tracking-tight mb-2.5">
            Your courses.
          </h1>
          <p className="text-[17px] text-muted max-w-[640px]">
            Everything you&apos;re currently enrolled in. Click a card to
            open the course outline.
          </p>
        </div>
      </header>

      <section className="px-[6vw] py-14 max-w-[1180px] mx-auto">
        <CoursesList />
        <div className="mt-10 text-center">
          <Link
            href="/portal"
            className="text-muted text-[13px] hover:text-blue-soft transition"
          >
            ← Back to portal
          </Link>
        </div>
      </section>

      <Footer />
    </>
  );
}

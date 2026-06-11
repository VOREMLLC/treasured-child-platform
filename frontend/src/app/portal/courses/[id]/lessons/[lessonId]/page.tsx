import Link from "next/link";
import { Nav } from "@/components/Nav";
import { Footer } from "@/components/Footer";
import { LessonView } from "./LessonView";

export const metadata = {
  title: "Lesson — Treasured Child School",
};

interface PageProps {
  params: { id: string; lessonId: string };
}

export default function LessonPage({ params }: PageProps) {
  return (
    <>
      <Nav />
      <section className="px-[6vw] py-10 max-w-[1180px] mx-auto">
        <Link
          href={`/portal/courses/${params.id}`}
          className="inline-flex items-center gap-1.5 text-muted text-[13px] hover:text-blue-soft transition mb-5"
        >
          ← Back to course
        </Link>
        <LessonView courseId={params.id} lessonId={params.lessonId} />
      </section>
      <Footer />
    </>
  );
}

import Link from "next/link";

import { Footer } from "@/components/Footer";
import { Icon } from "@/components/Icon";
import { Nav } from "@/components/Nav";
import { LessonView } from "./LessonView";

export const metadata = {
  title: "Lesson | Treasured Child School",
};

interface PageProps {
  params: { id: string; lessonId: string };
}

export default function LessonPage({ params }: PageProps) {
  return (
    <>
      <Nav />
      <main className="wrap py-6 sm:py-10">
        <Link
          href={`/portal/courses/${params.id}`}
          className="mb-4 inline-flex min-h-12 items-center gap-2 text-body font-bold text-muted hover:text-blue-ink"
        >
          <Icon name="arrow-left" size={20} />
          Back to course
        </Link>
        <LessonView key={params.lessonId} courseId={params.id} lessonId={params.lessonId} />
      </main>
      <Footer />
    </>
  );
}

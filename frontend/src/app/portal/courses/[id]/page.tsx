import Link from "next/link";
import { Nav } from "@/components/Nav";
import { Footer } from "@/components/Footer";
import { CourseDetailView } from "./CourseDetailView";

export const metadata = {
  title: "Course — Treasured Child School",
};

interface PageProps {
  params: { id: string };
}

export default function CourseDetailPage({ params }: PageProps) {
  return (
    <>
      <Nav />
      <section className="px-[6vw] py-12 max-w-[1180px] mx-auto">
        <Link
          href="/portal/courses"
          className="inline-flex items-center gap-1.5 text-muted text-[13px] hover:text-blue-soft transition mb-6"
        >
          ← All my courses
        </Link>
        <CourseDetailView courseId={params.id} />
      </section>
      <Footer />
    </>
  );
}

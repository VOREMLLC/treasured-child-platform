import Link from "next/link";

import { Footer } from "@/components/Footer";
import { Icon } from "@/components/Icon";
import { Nav } from "@/components/Nav";
import { CourseDetailView } from "./CourseDetailView";

export const metadata = {
  title: "Course | Treasured Child School",
};

interface PageProps {
  params: { id: string };
}

export default function CourseDetailPage({ params }: PageProps) {
  return (
    <>
      <Nav />
      <main className="wrap max-w-[880px] py-6 sm:py-10">
        <Link
          href="/portal/courses"
          className="mb-4 inline-flex min-h-12 items-center gap-2 text-body font-bold text-muted hover:text-blue-ink"
        >
          <Icon name="arrow-left" size={20} />
          My courses
        </Link>
        <CourseDetailView courseId={params.id} />
      </main>
      <Footer />
    </>
  );
}

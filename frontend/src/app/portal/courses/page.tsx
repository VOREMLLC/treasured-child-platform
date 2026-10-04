import { Footer } from "@/components/Footer";
import { Nav } from "@/components/Nav";
import { CoursesList } from "./CoursesList";

export const metadata = {
  title: "My courses | Treasured Child School",
  description: "The courses you have joined.",
};

export default function CoursesPage() {
  return (
    <>
      <Nav />
      <main className="wrap max-w-[880px] py-8 sm:py-12">
        <h1 className="mb-6 font-display text-[32px] font-bold text-ink sm:text-h2">
          My courses
        </h1>
        <CoursesList />
      </main>
      <Footer />
    </>
  );
}

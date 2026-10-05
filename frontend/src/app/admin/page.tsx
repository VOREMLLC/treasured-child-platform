import { Nav } from "@/components/Nav";
import { Footer } from "@/components/Footer";
import { AdminView } from "./AdminView";

export const metadata = {
  title: "School office | Treasured Child School",
  robots: { index: false },
};

export default function AdminPage() {
  return (
    <>
      <Nav />
      <main className="wrap py-8 sm:py-12">
        <AdminView />
      </main>
      <Footer />
    </>
  );
}

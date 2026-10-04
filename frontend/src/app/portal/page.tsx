import { Nav } from "@/components/Nav";
import { Footer } from "@/components/Footer";
import { PortalHome } from "./PortalHome";

export const metadata = {
  title: "My page | Treasured Child School",
  description: "Your lessons, progress and payments.",
};

export default function PortalPage() {
  return (
    <>
      <Nav />
      <main className="wrap max-w-[880px] py-8 sm:py-12">
        <PortalHome />
      </main>
      <Footer />
    </>
  );
}

import { Nav } from "@/components/Nav";
import { Footer } from "@/components/Footer";
import { MeView } from "./MeView";

export const metadata = {
  title: "Me | Treasured Child School",
};

export default function MePage() {
  return (
    <>
      <Nav />
      <main className="wrap max-w-[640px] py-8 sm:py-12">
        <MeView />
      </main>
      <Footer />
    </>
  );
}

import { Suspense } from "react";

import { Nav } from "@/components/Nav";
import { Footer } from "@/components/Footer";
import { PageHeader } from "@/components/PageHeader";
import { Skeleton } from "@/components/Skeleton";
import { PayForm } from "./PayForm";

export const metadata = {
  title: "Pay fees | Treasured Child School",
  description: "Pay school fees or an online course safely with Paystack.",
};

export default function PayPage() {
  return (
    <>
      <Nav />
      <PageHeader
        narrow
        title="Pay fees"
        lead="Choose what you are paying for, then tap pay."
      />
      <main className="wrap max-w-[640px] pb-8">
        <Suspense fallback={<Skeleton className="h-64 w-full rounded-card" />}>
          <PayForm />
        </Suspense>
      </main>
      <Footer />
    </>
  );
}

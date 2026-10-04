import { Suspense } from "react";

import { Footer } from "@/components/Footer";
import { Nav } from "@/components/Nav";
import { PageHeader } from "@/components/PageHeader";
import { Skeleton } from "@/components/Skeleton";
import { ResetPasswordForm } from "./ResetPasswordForm";

export const metadata = {
  title: "New password | Treasured Child School",
  description: "Choose a new password for your Treasured Child account.",
};

export default function ResetPasswordPage() {
  return (
    <>
      <Nav />
      <PageHeader narrow title="Choose a new password" />
      <main className="wrap max-w-[640px] pb-8">
        <Suspense fallback={<Skeleton className="h-60 w-full rounded-card" />}>
          <ResetPasswordForm />
        </Suspense>
      </main>
      <Footer />
    </>
  );
}

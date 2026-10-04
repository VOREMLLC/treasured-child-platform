import { Suspense } from "react";

import { Footer } from "@/components/Footer";
import { Nav } from "@/components/Nav";
import { PageHeader } from "@/components/PageHeader";
import { Skeleton } from "@/components/Skeleton";
import { LoginForm } from "./LoginForm";

export const metadata = {
  title: "Sign in | Treasured Child School",
  description: "Sign in to see your lessons or pay fees.",
};

export default function LoginPage() {
  return (
    <>
      <Nav />
      <PageHeader
        narrow
        title="Welcome back"
        lead="Sign in to see your lessons or pay fees."
      />
      <main className="wrap max-w-[640px] pb-8">
        <Suspense fallback={<Skeleton className="h-72 w-full rounded-card" />}>
          <LoginForm />
        </Suspense>
      </main>
      <Footer />
    </>
  );
}

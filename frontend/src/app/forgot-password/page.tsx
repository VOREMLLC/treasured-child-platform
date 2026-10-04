import { Footer } from "@/components/Footer";
import { Nav } from "@/components/Nav";
import { PageHeader } from "@/components/PageHeader";
import { ForgotPasswordForm } from "./ForgotPasswordForm";

export const metadata = {
  title: "Forgot password | Treasured Child School",
  description: "Get a link to set a new password.",
};

export default function ForgotPasswordPage() {
  return (
    <>
      <Nav />
      <PageHeader
        narrow
        title="Forgot your password?"
        lead="Type your email and we'll send you a link to set a new one."
      />
      <main className="wrap max-w-[640px] pb-8">
        <ForgotPasswordForm />
      </main>
      <Footer />
    </>
  );
}

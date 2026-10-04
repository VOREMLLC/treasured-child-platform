import { Footer } from "@/components/Footer";
import { Nav } from "@/components/Nav";
import { PageHeader } from "@/components/PageHeader";
import { RegisterForm } from "./RegisterForm";

export const metadata = {
  title: "Create an account | Treasured Child School",
  description: "Create your Treasured Child account to pay fees and follow lessons.",
};

export default function RegisterPage() {
  return (
    <>
      <Nav />
      <PageHeader
        narrow
        title="Create your account"
        lead="One account lets you pay fees and follow your child's lessons."
      />
      <main className="wrap max-w-[640px] pb-8">
        <RegisterForm />
      </main>
      <Footer />
    </>
  );
}

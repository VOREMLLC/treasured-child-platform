import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Treasured Child School",
  description:
    "Nursery, primary and secondary in Orerokpe, Delta State — and a growing set of online programmes.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-page text-paper font-body antialiased">
        {children}
      </body>
    </html>
  );
}

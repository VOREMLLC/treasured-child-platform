import type { Metadata, Viewport } from "next";
import { Baloo_2, Nunito } from "next/font/google";
import "./globals.css";

const display = Baloo_2({
  subsets: ["latin"],
  weight: ["600", "700"],
  variable: "--font-display",
  display: "swap",
});

const body = Nunito({
  subsets: ["latin"],
  weight: ["400", "600", "800"],
  variable: "--font-body",
  display: "swap",
});

export const metadata: Metadata = {
  title: "Treasured Child School",
  description:
    "Nursery, primary and secondary school in Orerokpe, Delta State, with online classes for learners anywhere in Nigeria.",
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  viewportFit: "cover",
  themeColor: [
    { media: "(prefers-color-scheme: light)", color: "#f6f8fc" },
    { media: "(prefers-color-scheme: dark)", color: "#0e1824" },
  ],
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className={`${display.variable} ${body.variable}`}>
      {/* Bottom padding leaves room for the mobile bottom bar. */}
      <body className="min-h-screen bg-page text-ink font-body text-body antialiased pb-[calc(64px+env(safe-area-inset-bottom))] md:pb-0">
        {children}
      </body>
    </html>
  );
}

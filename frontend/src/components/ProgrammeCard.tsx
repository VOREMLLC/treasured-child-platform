import Link from "next/link";

interface ProgrammeCardProps {
  href: string;
  bandGradient: string;
  bandLabel: string;
  bandTextColor?: string;
  pill: string;
  pillVariant?: "blue" | "gold";
  title: string;
  children: React.ReactNode;
}

export function ProgrammeCard({
  href,
  bandGradient,
  bandLabel,
  bandTextColor = "#fff",
  pill,
  pillVariant = "blue",
  title,
  children,
}: ProgrammeCardProps) {
  return (
    <Link
      href={href}
      className="bg-card border border-line rounded-lg overflow-hidden flex flex-col transition hover:-translate-y-1 hover:shadow hover:border-blue-deep group"
    >
      <div
        className="h-24 grid place-items-center font-display text-[24px] tracking-tight"
        style={{ background: bandGradient, color: bandTextColor }}
      >
        {bandLabel}
      </div>
      <div className="p-5 pt-5 pb-6">
        <span
          className={
            "inline-block text-[12px] font-semibold px-2.5 py-1 rounded-pill " +
            (pillVariant === "gold"
              ? "bg-[rgba(239,183,0,0.14)] text-gold"
              : "bg-[rgba(47,127,212,0.14)] text-blue-soft")
          }
        >
          {pill}
        </span>
        <h3 className="font-display text-[19px] text-paper mt-2 mb-1.5">
          {title}
        </h3>
        <p className="text-muted text-[14.5px] mb-3.5">{children}</p>
        <span className="text-blue-soft font-semibold text-[14px] inline-block transition group-hover:translate-x-0.5">
          Learn more →
        </span>
      </div>
    </Link>
  );
}

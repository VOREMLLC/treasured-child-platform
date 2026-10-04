interface PageHeaderProps {
  title: string;
  lead?: React.ReactNode;
  /** Optional row of actions or a back link shown above the title. */
  above?: React.ReactNode;
  children?: React.ReactNode;
  narrow?: boolean;
}

/** The one page header used across the site (replaces per-page heroes). */
export function PageHeader({
  title,
  lead,
  above,
  children,
  narrow = false,
}: PageHeaderProps) {
  return (
    <header className="bg-[linear-gradient(180deg,var(--blue-soft),var(--bg))]">
      <div
        className={`wrap pb-8 pt-8 sm:pb-12 sm:pt-12 ${narrow ? "max-w-[640px]" : ""}`}
      >
        {above && <div className="mb-4">{above}</div>}
        <h1 className="font-display text-[32px] font-bold text-ink sm:text-h2 md:text-h1">
          {title}
        </h1>
        {lead && (
          <p className="mt-3 max-w-[56ch] text-label text-muted">{lead}</p>
        )}
        {children && <div className="mt-6">{children}</div>}
      </div>
    </header>
  );
}

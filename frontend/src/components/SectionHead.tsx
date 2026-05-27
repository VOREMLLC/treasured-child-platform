interface SectionHeadProps {
  kicker: string;
  heading: string;
  sub?: string;
}

export function SectionHead({ kicker, heading, sub }: SectionHeadProps) {
  return (
    <div className="text-center mb-10">
      <span className="inline-flex items-center gap-2 text-[12px] font-bold uppercase tracking-[0.22em] text-gold">
        {kicker}
      </span>
      <h2 className="font-display font-semibold text-paper text-[clamp(27px,4vw,40px)] mt-2">
        {heading}
      </h2>
      {sub && (
        <p className="text-muted max-w-[540px] mx-auto mt-2">{sub}</p>
      )}
    </div>
  );
}

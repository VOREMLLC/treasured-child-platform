interface ProgressBarProps {
  value: number;
  /** Visible text label; defaults to "{value}% done". */
  label?: string;
  className?: string;
}

/** Gold progress bar with a text label (never colour alone). */
export function ProgressBar({ value, label, className = "" }: ProgressBarProps) {
  const pct = Math.max(0, Math.min(100, Math.round(value)));
  const text = label ?? `${pct}% done`;
  return (
    <div className={className}>
      <div
        role="progressbar"
        aria-valuenow={pct}
        aria-valuemin={0}
        aria-valuemax={100}
        aria-label={text}
        className="h-3 overflow-hidden rounded-full bg-gold-soft"
      >
        <div
          className="h-full w-full origin-left rounded-full bg-gold transition-transform duration-200 ease-out"
          style={{ transform: `scaleX(${pct / 100})` }}
        />
      </div>
      <p className="mt-1.5 text-caption font-semibold text-muted">{text}</p>
    </div>
  );
}

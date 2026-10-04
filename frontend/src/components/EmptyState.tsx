import { Icon, type IconName } from "./Icon";

type Tone = "blue" | "gold" | "success" | "danger";

const TONES: Record<Tone, string> = {
  blue: "bg-blue-soft text-blue-ink",
  gold: "bg-gold-soft text-gold-text",
  success: "bg-success-soft text-success",
  danger: "bg-danger-soft text-danger",
};

interface EmptyStateProps {
  icon: IconName;
  title: string;
  children?: React.ReactNode;
  actions?: React.ReactNode;
  tone?: Tone;
  /** Use "alert" for errors so screen readers announce them. */
  role?: "status" | "alert";
}

/** A composed, friendly card for empty, signed-out and error states. */
export function EmptyState({
  icon,
  title,
  children,
  actions,
  tone = "blue",
  role,
}: EmptyStateProps) {
  return (
    <section
      role={role}
      className="rounded-card border border-line bg-card px-5 py-10 text-center shadow-s sm:px-10"
    >
      <span
        className={`mx-auto mb-5 grid h-16 w-16 place-items-center rounded-full ${TONES[tone]}`}
      >
        <Icon name={icon} size={32} />
      </span>
      <h2 className="mb-2 font-display text-title font-bold text-ink">
        {title}
      </h2>
      {children && (
        <div className="mx-auto max-w-[44ch] text-body text-muted">
          {children}
        </div>
      )}
      {actions && (
        <div className="mt-6 flex flex-col items-stretch justify-center gap-3 sm:flex-row sm:items-center">
          {actions}
        </div>
      )}
    </section>
  );
}

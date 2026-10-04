/** Grey placeholder shapes shown while data loads (instead of "Loading"). */

export function Skeleton({ className = "" }: { className?: string }) {
  return (
    <div
      aria-hidden
      className={`rounded-control bg-line motion-safe:animate-pulse ${className}`}
    />
  );
}

/** A card-shaped skeleton: title line, two body lines, a button. */
export function SkeletonCard({ className = "" }: { className?: string }) {
  return (
    <div
      aria-hidden
      className={`rounded-card border border-line bg-card p-5 shadow-s ${className}`}
    >
      <Skeleton className="mb-4 h-6 w-2/3" />
      <Skeleton className="mb-2 h-4 w-full" />
      <Skeleton className="mb-5 h-4 w-4/5" />
      <Skeleton className="h-12 w-40" />
    </div>
  );
}

/** Wraps skeletons so screen readers hear one short status message. */
export function SkeletonGroup({
  label,
  children,
}: {
  label: string;
  children: React.ReactNode;
}) {
  return (
    <div role="status" aria-live="polite">
      <span className="sr-only">{label}</span>
      {children}
    </div>
  );
}

import Link from "next/link";

import { buttonClasses } from "./Button";
import { Icon } from "./Icon";
import { formatNaira, type Programme } from "@/lib/programmes";

/**
 * A programme card with its price and ONE action: school programmes
 * lead to the application form, online ones to payment.
 */
export function ProgrammeCard({ programme: p }: { programme: Programme }) {
  const online = p.kind === "online";
  return (
    <article className="flex flex-col rounded-card border border-line bg-card p-5 shadow-s">
      <div className="mb-4 flex items-center gap-3">
        <span
          className={`grid h-12 w-12 place-items-center rounded-control ${online ? "bg-gold-soft text-gold-text" : "bg-blue-soft text-blue-ink"}`}
        >
          <Icon name={p.icon} />
        </span>
        <span className="text-caption font-semibold text-muted">
          {online ? "Online" : "On campus"}, {p.ageRange}
        </span>
      </div>
      <h3 className="font-display text-title font-bold text-ink">
        <Link
          href={`/programmes/${p.slug}`}
          className="rounded-control hover:text-blue-ink"
        >
          {p.title}
        </Link>
      </h3>
      <p className="mt-1 flex-1 text-body text-muted">{p.summary}</p>
      <p className="mt-4 text-body text-muted">
        <span className="font-display text-title font-bold text-ink">
          {formatNaira(p.priceNaira)}
        </span>{" "}
        {p.pricePer}
      </p>
      <Link
        href={online ? `/pay?for=${p.slug}` : "/apply"}
        className={buttonClasses({
          variant: online ? "primary" : "secondary",
          full: true,
          className: "mt-4",
        })}
      >
        {online ? "Pay fees" : "Apply now"}
      </Link>
    </article>
  );
}

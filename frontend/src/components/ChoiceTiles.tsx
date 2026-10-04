"use client";

import { Icon, type IconName } from "./Icon";

export interface ChoiceOption<V extends string> {
  value: V;
  title: string;
  description?: string;
  /** Shown big on the right, e.g. "₦125,000". */
  price?: string;
  icon?: IconName;
}

interface ChoiceTilesProps<V extends string> {
  name: string;
  legend: string;
  options: ChoiceOption<V>[];
  value: V | "";
  onChange: (value: V) => void;
  error?: string;
  /** Two columns from sm up (for short options like class levels). */
  grid?: boolean;
}

/**
 * Big tap-friendly radio cards. Real radio inputs underneath, so the
 * keyboard (arrow keys) and screen readers behave like a normal radio group.
 */
export function ChoiceTiles<V extends string>({
  name,
  legend,
  options,
  value,
  onChange,
  error,
  grid = false,
}: ChoiceTilesProps<V>) {
  return (
    <fieldset>
      <legend className="mb-2 text-label font-bold text-ink">{legend}</legend>
      <div className={grid ? "grid gap-3 sm:grid-cols-2" : "grid gap-3"}>
        {options.map((opt) => {
          const checked = opt.value === value;
          return (
            <label
              key={opt.value}
              className={[
                "relative flex min-h-16 cursor-pointer items-center gap-4 rounded-card border-2 p-4",
                "transition-[transform,border-color,background-color] duration-200 ease-out motion-safe:active:scale-[.98]",
                "has-[:focus-visible]:outline has-[:focus-visible]:outline-[3px] has-[:focus-visible]:outline-offset-2 has-[:focus-visible]:outline-[color:var(--ring)]",
                checked
                  ? "border-blue bg-blue-soft"
                  : error
                    ? "border-danger bg-surface"
                    : "border-line bg-surface hover:border-blue",
              ].join(" ")}
            >
              <input
                type="radio"
                name={name}
                value={opt.value}
                checked={checked}
                onChange={() => onChange(opt.value)}
                className="sr-only"
              />
              {opt.icon && (
                <span
                  className={[
                    "grid h-12 w-12 shrink-0 place-items-center rounded-control",
                    checked ? "bg-blue text-white" : "bg-blue-soft text-blue-ink",
                  ].join(" ")}
                >
                  <Icon name={opt.icon} />
                </span>
              )}
              <span className="flex-1">
                <span className="block text-label font-extrabold text-ink">
                  {opt.title}
                </span>
                {opt.description && (
                  <span className="block text-caption text-muted">
                    {opt.description}
                  </span>
                )}
              </span>
              {opt.price && (
                <span className="font-display text-title font-bold text-ink">
                  {opt.price}
                </span>
              )}
              <span
                aria-hidden
                className={[
                  "grid h-7 w-7 shrink-0 place-items-center rounded-full border-2",
                  checked
                    ? "border-blue bg-blue text-white"
                    : "border-line bg-surface text-transparent",
                ].join(" ")}
              >
                <Icon name="check" size={18} strokeWidth={3} />
              </span>
            </label>
          );
        })}
      </div>
      {error && (
        <p
          role="alert"
          className="mt-2 flex items-start gap-2 text-body text-danger"
        >
          <Icon name="alert" size={20} className="mt-0.5" />
          <span>{error}</span>
        </p>
      )}
    </fieldset>
  );
}

"use client";

import {
  useState,
  type InputHTMLAttributes,
  type TextareaHTMLAttributes,
} from "react";

import { Icon } from "./Icon";

/**
 * Form fields. Label sits above the control, hint below it, and an
 * error (with icon) replaces the hint. Controls are 48px+ tall with a
 * 17px font so phones don't zoom in on focus.
 */

export function controlClass(hasError: boolean): string {
  return [
    "w-full min-h-12 rounded-control border-2 bg-surface px-4 py-2.5 text-body text-ink",
    "placeholder:text-muted transition-colors duration-200 ease-out",
    "focus:outline-none focus-visible:outline-none focus:shadow-[0_0_0_3px_var(--ring)]",
    hasError
      ? "border-danger focus:border-danger"
      : "border-line focus:border-blue",
  ].join(" ");
}

interface ShellProps {
  id: string;
  label: string;
  hint?: string;
  error?: string;
  optional?: boolean;
  children: React.ReactNode;
}

export function FieldShell({
  id,
  label,
  hint,
  error,
  optional,
  children,
}: ShellProps) {
  return (
    <div className="flex flex-col gap-2">
      <label htmlFor={id} className="text-label font-bold text-ink">
        {label}
        {optional && (
          <span className="font-semibold text-muted"> (optional)</span>
        )}
      </label>
      {children}
      {error ? (
        <p
          id={`${id}-msg`}
          role="alert"
          className="flex items-start gap-2 text-body text-danger"
        >
          <Icon name="alert" size={20} className="mt-0.5" />
          <span>{error}</span>
        </p>
      ) : hint ? (
        <p id={`${id}-msg`} className="text-caption text-muted">
          {hint}
        </p>
      ) : null}
    </div>
  );
}

interface TextFieldProps
  extends Omit<InputHTMLAttributes<HTMLInputElement>, "id"> {
  id: string;
  label: string;
  hint?: string;
  error?: string;
  optional?: boolean;
}

export function TextField({
  id,
  label,
  hint,
  error,
  optional,
  ...input
}: TextFieldProps) {
  return (
    <FieldShell
      id={id}
      label={label}
      hint={hint}
      error={error}
      optional={optional}
    >
      <input
        id={id}
        name={id}
        aria-invalid={error ? true : undefined}
        aria-describedby={error || hint ? `${id}-msg` : undefined}
        className={controlClass(!!error)}
        {...input}
      />
    </FieldShell>
  );
}

interface TextAreaFieldProps
  extends Omit<TextareaHTMLAttributes<HTMLTextAreaElement>, "id"> {
  id: string;
  label: string;
  hint?: string;
  error?: string;
  optional?: boolean;
}

export function TextAreaField({
  id,
  label,
  hint,
  error,
  optional,
  ...area
}: TextAreaFieldProps) {
  return (
    <FieldShell
      id={id}
      label={label}
      hint={hint}
      error={error}
      optional={optional}
    >
      <textarea
        id={id}
        name={id}
        rows={4}
        aria-invalid={error ? true : undefined}
        aria-describedby={error || hint ? `${id}-msg` : undefined}
        className={`${controlClass(!!error)} resize-y`}
        {...area}
      />
    </FieldShell>
  );
}

/** Password input with a show/hide toggle (typing on phones is error-prone). */
export function PasswordField(props: Omit<TextFieldProps, "type">) {
  const { id, label, hint, error, optional, ...input } = props;
  const [shown, setShown] = useState(false);
  return (
    <FieldShell
      id={id}
      label={label}
      hint={hint}
      error={error}
      optional={optional}
    >
      <div className="relative">
        <input
          id={id}
          name={id}
          type={shown ? "text" : "password"}
          aria-invalid={error ? true : undefined}
          aria-describedby={error || hint ? `${id}-msg` : undefined}
          className={`${controlClass(!!error)} pr-14`}
          {...input}
        />
        <button
          type="button"
          onClick={() => setShown((s) => !s)}
          aria-label={shown ? "Hide password" : "Show password"}
          aria-pressed={shown}
          className="absolute right-1 top-1/2 -translate-y-1/2 grid h-12 w-12 place-items-center rounded-control text-muted hover:text-ink"
        >
          <Icon name={shown ? "eye-off" : "eye"} />
        </button>
      </div>
    </FieldShell>
  );
}

/** Banner for a whole-form problem (shown above the fields). */
export function FormAlert({ children }: { children: React.ReactNode }) {
  return (
    <div
      role="alert"
      className="flex items-start gap-3 rounded-control bg-danger-soft px-4 py-3 text-body text-danger"
    >
      <Icon name="alert" className="mt-0.5" />
      <div>{children}</div>
    </div>
  );
}

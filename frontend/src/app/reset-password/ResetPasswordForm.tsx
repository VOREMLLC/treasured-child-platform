"use client";

import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { useState, type FormEvent } from "react";

import { ApiError, postResetPassword } from "@/lib/api";

interface FormState {
  password: string;
  confirm: string;
}

const INITIAL: FormState = { password: "", confirm: "" };

export function ResetPasswordForm() {
  const params = useSearchParams();
  const token = params.get("token") ?? "";

  const [form, setForm] = useState<FormState>(INITIAL);
  const [submitting, setSubmitting] = useState(false);
  const [topError, setTopError] = useState<string | null>(null);
  const [fieldError, setFieldError] = useState<string | null>(null);
  const [done, setDone] = useState(false);

  if (!token) {
    return (
      <article
        role="alert"
        className="bg-card border border-danger/40 rounded-lg p-6 text-center"
      >
        <div className="inline-flex items-center gap-2 text-[12px] font-bold uppercase tracking-[0.22em] text-danger mb-2">
          Missing token
        </div>
        <p className="text-muted text-[15px] mb-4">
          This page expects a reset link from your email. Open the link
          again or request a fresh one.
        </p>
        <Link
          href="/forgot-password"
          className="inline-flex items-center px-5 py-3 rounded-pill border border-line text-paper font-semibold hover:border-blue-bright transition"
        >
          Request a new link
        </Link>
      </article>
    );
  }

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setTopError(null);
    setFieldError(null);

    if (form.password.length < 8) {
      setFieldError("Password must be at least 8 characters.");
      return;
    }
    if (form.password !== form.confirm) {
      setFieldError("The two passwords don't match.");
      return;
    }

    setSubmitting(true);
    try {
      await postResetPassword({
        token,
        new_password: form.password,
      });
      setDone(true);
    } catch (err) {
      if (err instanceof ApiError) {
        setTopError(err.message);
      } else {
        setTopError("Something unexpected happened. Please try again.");
      }
      setSubmitting(false);
    }
  }

  if (done) {
    return (
      <article
        role="status"
        className="bg-card border border-line rounded-lg p-8 text-center"
      >
        <div className="inline-flex items-center gap-2 text-[12px] font-bold uppercase tracking-[0.22em] text-gold mb-3">
          Password updated
        </div>
        <h2 className="font-display text-paper text-[24px] mb-3">
          You can sign in now.
        </h2>
        <p className="text-muted text-[15px] max-w-[420px] mx-auto mb-6">
          Your new password is active. The reset link you used is now
          spent.
        </p>
        <Link
          href="/login"
          className="inline-flex items-center px-5 py-3 rounded-pill bg-gradient-to-b from-blue to-blue-deep text-white font-semibold shadow-[0_10px_24px_-10px_rgba(31,99,201,0.55)] hover:from-blue-bright transition"
        >
          Sign in
        </Link>
      </article>
    );
  }

  return (
    <form
      onSubmit={onSubmit}
      noValidate
      className="bg-card border border-line rounded-lg p-6 sm:p-8 space-y-5"
    >
      {topError && (
        <div
          role="alert"
          className="rounded-md border border-danger/40 bg-[rgba(210,74,74,0.10)] px-4 py-3 text-[14px] text-danger"
        >
          {topError}
        </div>
      )}

      <Field
        id="password"
        label="New password"
        hint="At least 8 characters."
        error={fieldError ?? undefined}
      >
        <input
          id="password"
          name="password"
          type="password"
          required
          minLength={8}
          autoComplete="new-password"
          value={form.password}
          onChange={(e) =>
            setForm((p) => ({ ...p, password: e.target.value }))
          }
          className="w-full bg-page border border-line rounded-md px-3 py-2.5 text-paper text-[15px] focus:outline-none focus:border-blue-bright focus:shadow-[0_0_0_3px_rgba(47,127,212,0.25)] transition"
        />
      </Field>

      <Field id="confirm" label="Confirm new password">
        <input
          id="confirm"
          name="confirm"
          type="password"
          required
          minLength={8}
          autoComplete="new-password"
          value={form.confirm}
          onChange={(e) =>
            setForm((p) => ({ ...p, confirm: e.target.value }))
          }
          className="w-full bg-page border border-line rounded-md px-3 py-2.5 text-paper text-[15px] focus:outline-none focus:border-blue-bright focus:shadow-[0_0_0_3px_rgba(47,127,212,0.25)] transition"
        />
      </Field>

      <button
        type="submit"
        disabled={submitting}
        className="w-full inline-flex items-center justify-center px-5 py-3 rounded-pill bg-gradient-to-b from-blue to-blue-deep text-white font-semibold shadow-[0_10px_24px_-10px_rgba(31,99,201,0.55)] hover:from-blue-bright transition disabled:opacity-60 disabled:cursor-not-allowed"
      >
        {submitting ? "Updating…" : "Set new password"}
      </button>
    </form>
  );
}

function Field({
  id,
  label,
  hint,
  error,
  children,
}: {
  id: string;
  label: string;
  hint?: string;
  error?: string;
  children: React.ReactNode;
}) {
  return (
    <div className="flex flex-col gap-1.5">
      <label htmlFor={id} className="text-[13px] font-semibold text-paper">
        {label}
      </label>
      {children}
      {hint && !error && (
        <p className="text-muted text-[12.5px]">{hint}</p>
      )}
      {error && (
        <p className="text-danger text-[12.5px]" role="alert">
          {error}
        </p>
      )}
    </div>
  );
}

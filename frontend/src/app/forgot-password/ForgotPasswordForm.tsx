"use client";

import { useState, type FormEvent } from "react";

import { ApiError, postForgotPassword } from "@/lib/api";

export function ForgotPasswordForm() {
  const [email, setEmail] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [topError, setTopError] = useState<string | null>(null);
  const [sent, setSent] = useState(false);

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setTopError(null);
    setSubmitting(true);
    try {
      await postForgotPassword({ email: email.trim() });
      // Always show the same confirmation regardless of whether the
      // email is registered — matches the backend's no-leak design.
      setSent(true);
    } catch (err) {
      if (err instanceof ApiError) {
        setTopError(err.message);
      } else {
        setTopError("Something unexpected happened. Please try again.");
      }
      setSubmitting(false);
    }
  }

  if (sent) {
    return (
      <article
        role="status"
        className="bg-card border border-line rounded-lg p-8 text-center"
      >
        <div className="inline-flex items-center gap-2 text-[12px] font-bold uppercase tracking-[0.22em] text-gold mb-3">
          Check your email
        </div>
        <h2 className="font-display text-paper text-[24px] mb-3">
          If that email is registered, a reset link is on its way.
        </h2>
        <p className="text-muted text-[15px] max-w-[420px] mx-auto">
          The link expires in 60 minutes and can only be used once. Look
          in your spam folder if you don&apos;t see it.
        </p>
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

      <div className="flex flex-col gap-1.5">
        <label
          htmlFor="email"
          className="text-[13px] font-semibold text-paper"
        >
          Email
        </label>
        <input
          id="email"
          name="email"
          type="email"
          required
          autoComplete="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          className="w-full bg-page border border-line rounded-md px-3 py-2.5 text-paper text-[15px] focus:outline-none focus:border-blue-bright focus:shadow-[0_0_0_3px_rgba(47,127,212,0.25)] transition"
        />
      </div>

      <button
        type="submit"
        disabled={submitting}
        className="w-full inline-flex items-center justify-center px-5 py-3 rounded-pill bg-gradient-to-b from-blue to-blue-deep text-white font-semibold shadow-[0_10px_24px_-10px_rgba(31,99,201,0.55)] hover:from-blue-bright transition disabled:opacity-60 disabled:cursor-not-allowed"
      >
        {submitting ? "Sending…" : "Send reset link"}
      </button>
    </form>
  );
}

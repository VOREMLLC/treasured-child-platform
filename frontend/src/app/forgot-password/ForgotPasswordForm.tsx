"use client";

import Link from "next/link";
import { useState, type FormEvent } from "react";

import { Button, ButtonLink } from "@/components/Button";
import { EmptyState } from "@/components/EmptyState";
import { FormAlert, TextField } from "@/components/Field";
import { ApiError, postForgotPassword } from "@/lib/api";

export function ForgotPasswordForm() {
  const [email, setEmail] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [sent, setSent] = useState(false);

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      await postForgotPassword({ email: email.trim() });
      // Same message whether or not the email exists, so we never reveal
      // who has an account.
      setSent(true);
    } catch (err) {
      setError(
        err instanceof ApiError ? err.message : "Something went wrong. Please try again.",
      );
      setSubmitting(false);
    }
  }

  if (sent) {
    return (
      <EmptyState
        icon="check"
        tone="success"
        role="status"
        title="Check your email"
        actions={<ButtonLink href="/login" variant="secondary">Sign in</ButtonLink>}
      >
        If that email has an account, we sent a link to set a new password.
        It works once, for one hour. Look in spam if you can&apos;t find it.
      </EmptyState>
    );
  }

  return (
    <form onSubmit={onSubmit} noValidate className="space-y-6">
      {error && <FormAlert>{error}</FormAlert>}
      <TextField
        id="email"
        label="Email"
        type="email"
        inputMode="email"
        required
        autoComplete="email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
      />
      <Button type="submit" size="lg" full loading={submitting}>
        Send me a link
      </Button>
      <p className="text-center text-body text-muted">
        Remembered it?{" "}
        <Link href="/login" className="inline-flex min-h-12 items-center font-bold text-blue-ink">
          Sign in
        </Link>
      </p>
    </form>
  );
}

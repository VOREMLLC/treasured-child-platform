"use client";

import { useSearchParams } from "next/navigation";
import { useState, type FormEvent } from "react";

import { Button, ButtonLink } from "@/components/Button";
import { EmptyState } from "@/components/EmptyState";
import { FormAlert, PasswordField } from "@/components/Field";
import { ApiError, postResetPassword } from "@/lib/api";

export function ResetPasswordForm() {
  const token = useSearchParams().get("token") ?? "";

  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [topError, setTopError] = useState<string | null>(null);
  const [passwordError, setPasswordError] = useState<string | undefined>();
  const [confirmError, setConfirmError] = useState<string | undefined>();
  const [done, setDone] = useState(false);

  if (!token) {
    return (
      <EmptyState
        icon="alert"
        tone="danger"
        role="alert"
        title="This link is not complete"
        actions={
          <ButtonLink href="/forgot-password" variant="secondary">
            Send me a new link
          </ButtonLink>
        }
      >
        Please open the link from your email again, or ask for a new one.
      </EmptyState>
    );
  }

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setTopError(null);
    setPasswordError(undefined);
    setConfirmError(undefined);

    if (password.length < 8) {
      setPasswordError("Use at least 8 letters or numbers.");
      return;
    }
    if (password !== confirm) {
      setConfirmError("The two passwords are different.");
      return;
    }

    setSubmitting(true);
    try {
      await postResetPassword({ token, new_password: password });
      setDone(true);
    } catch (err) {
      setTopError(
        err instanceof ApiError ? err.message : "Something went wrong. Please try again.",
      );
      setSubmitting(false);
    }
  }

  if (done) {
    return (
      <EmptyState
        icon="check"
        tone="success"
        role="status"
        title="Password changed"
        actions={<ButtonLink href="/login">Sign in</ButtonLink>}
      >
        You can sign in with your new password now.
      </EmptyState>
    );
  }

  return (
    <form onSubmit={onSubmit} noValidate className="space-y-6">
      {topError && <FormAlert>{topError}</FormAlert>}
      <PasswordField
        id="password"
        label="New password"
        required
        minLength={8}
        autoComplete="new-password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        hint="At least 8 letters or numbers."
        error={passwordError}
      />
      <PasswordField
        id="confirm"
        label="Type it again"
        required
        minLength={8}
        autoComplete="new-password"
        value={confirm}
        onChange={(e) => setConfirm(e.target.value)}
        error={confirmError}
      />
      <Button type="submit" size="lg" full loading={submitting}>
        Save new password
      </Button>
    </form>
  );
}

"use client";

import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { useState, type FormEvent } from "react";

import { Button } from "@/components/Button";
import { FormAlert, PasswordField, TextField } from "@/components/Field";
import { ApiError, postLogin } from "@/lib/api";

/** Same-site paths only; "//x" and "/\\x" would leave the site. */
function safeNext(raw: string | null): string {
  if (raw && /^\/(?![/\\])/.test(raw)) return raw;
  return "/portal";
}

export function LoginForm() {
  const router = useRouter();
  const next = safeNext(useSearchParams().get("next"));
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      await postLogin({ email: email.trim(), password });
      router.push(next);
      router.refresh();
    } catch (err) {
      setError(
        err instanceof ApiError ? err.message : "Something went wrong. Please try again.",
      );
      setSubmitting(false);
    }
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
        onChange={(e) => {
          setEmail(e.target.value);
          setError(null);
        }}
      />

      <PasswordField
        id="password"
        label="Password"
        required
        autoComplete="current-password"
        value={password}
        onChange={(e) => {
          setPassword(e.target.value);
          setError(null);
        }}
      />

      <Button type="submit" size="lg" full loading={submitting}>
        Sign in
      </Button>

      <div className="flex flex-col items-center gap-1 text-body">
        <Link
          href="/forgot-password"
          className="inline-flex min-h-12 items-center font-bold text-blue-ink"
        >
          Forgot your password?
        </Link>
        <p className="text-muted">
          New here?{" "}
          <Link href="/register" className="inline-flex min-h-12 items-center font-bold text-blue-ink">
            Create an account
          </Link>
        </p>
      </div>
    </form>
  );
}

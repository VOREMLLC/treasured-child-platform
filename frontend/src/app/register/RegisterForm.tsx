"use client";

import Link from "next/link";
import { useState, type FormEvent } from "react";

import { Button, ButtonLink } from "@/components/Button";
import { FormAlert, PasswordField, TextField } from "@/components/Field";
import { Icon } from "@/components/Icon";
import { ApiError, postRegister, type RegisterRequest } from "@/lib/api";
import { firstName } from "@/lib/useApi";

interface FormState {
  name: string;
  email: string;
  phone: string;
  password: string;
}

const INITIAL: FormState = { name: "", email: "", phone: "", password: "" };

export function RegisterForm() {
  const [form, setForm] = useState<FormState>(INITIAL);
  const [submitting, setSubmitting] = useState(false);
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});
  const [topError, setTopError] = useState<string | null>(null);
  const [doneName, setDoneName] = useState<string | null>(null);

  function update<K extends keyof FormState>(key: K, value: FormState[K]) {
    setForm((prev) => ({ ...prev, [key]: value }));
    if (fieldErrors[key]) {
      setFieldErrors((prev) => {
        const next = { ...prev };
        delete next[key];
        return next;
      });
    }
  }

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setFieldErrors({});
    setTopError(null);

    const payload: RegisterRequest = {
      name: form.name.trim(),
      email: form.email.trim(),
      phone: form.phone.trim() || undefined,
      password: form.password,
    };

    setSubmitting(true);
    try {
      const user = await postRegister(payload);
      setDoneName(user.name);
      setForm(INITIAL);
      window.scrollTo({ top: 0 });
    } catch (err) {
      if (err instanceof ApiError) {
        const map: Record<string, string> = {};
        for (const fe of err.fieldErrors) {
          if (fe.field) map[fe.field] = fe.message;
        }
        setFieldErrors(map);
        setTopError(
          err.status === 422 ? "Please check the boxes marked in red." : err.message,
        );
      } else {
        setTopError("Something went wrong. Please try again.");
      }
    } finally {
      setSubmitting(false);
    }
  }

  if (doneName) {
    return (
      <section
        role="status"
        className="rounded-card border border-line bg-card px-5 py-10 text-center shadow-s"
      >
        <span className="mx-auto mb-5 grid h-24 w-24 place-items-center rounded-full bg-success text-white motion-safe:animate-celebrate">
          <Icon name="check" size={52} strokeWidth={3} />
        </span>
        <h2 className="font-display text-h3 font-bold text-ink">
          Welcome, {firstName(doneName)}!
        </h2>
        <p className="mx-auto mt-2 max-w-[40ch] text-label text-muted">
          Your account is made. We will switch it on soon and let you know,
          then you can sign in.
        </p>
        <div className="mx-auto mt-6 flex max-w-[360px] flex-col gap-3">
          <ButtonLink href="/login" full>
            Sign in
          </ButtonLink>
          <ButtonLink href="/" variant="secondary" full>
            Back to home
          </ButtonLink>
        </div>
      </section>
    );
  }

  return (
    <form onSubmit={onSubmit} noValidate className="space-y-6">
      {topError && <FormAlert>{topError}</FormAlert>}

      <TextField
        id="name"
        label="Your full name"
        type="text"
        required
        autoComplete="name"
        value={form.name}
        onChange={(e) => update("name", e.target.value)}
        error={fieldErrors.name}
      />

      <TextField
        id="email"
        label="Email"
        type="email"
        inputMode="email"
        required
        autoComplete="email"
        value={form.email}
        onChange={(e) => update("email", e.target.value)}
        error={fieldErrors.email}
      />

      <TextField
        id="phone"
        label="Phone (WhatsApp)"
        optional
        type="tel"
        inputMode="tel"
        autoComplete="tel"
        placeholder="0803 123 4567"
        value={form.phone}
        onChange={(e) => update("phone", e.target.value)}
        error={fieldErrors.phone}
      />

      <PasswordField
        id="password"
        label="Choose a password"
        required
        minLength={8}
        autoComplete="new-password"
        value={form.password}
        onChange={(e) => update("password", e.target.value)}
        error={fieldErrors.password}
        hint="At least 8 letters or numbers."
      />

      <Button type="submit" size="lg" full loading={submitting}>
        Create account
      </Button>

      <p className="text-center text-body text-muted">
        Already have an account?{" "}
        <Link href="/login" className="inline-flex min-h-12 items-center font-bold text-blue-ink">
          Sign in
        </Link>
      </p>
    </form>
  );
}

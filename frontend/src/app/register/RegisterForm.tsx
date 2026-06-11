"use client";

import { useState, type FormEvent } from "react";

import { ApiError, postRegister, type RegisterRequest } from "@/lib/api";

interface FormState {
  name: string;
  email: string;
  phone: string;
  password: string;
}

const INITIAL: FormState = {
  name: "",
  email: "",
  phone: "",
  password: "",
};

export function RegisterForm() {
  const [form, setForm] = useState<FormState>(INITIAL);
  const [submitting, setSubmitting] = useState(false);
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});
  const [topError, setTopError] = useState<string | null>(null);
  const [success, setSuccess] = useState<{ name: string } | null>(null);

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
      setSuccess({ name: user.name });
      setForm(INITIAL);
    } catch (err) {
      if (err instanceof ApiError) {
        const map: Record<string, string> = {};
        for (const fe of err.fieldErrors) {
          if (fe.field) map[fe.field] = fe.message;
        }
        setFieldErrors(map);
        setTopError(err.message);
      } else {
        setTopError("Something unexpected happened. Please try again.");
      }
    } finally {
      setSubmitting(false);
    }
  }

  if (success) {
    return (
      <article
        role="status"
        className="bg-card border border-line rounded-lg p-8 text-center"
      >
        <div className="inline-flex items-center gap-2 text-[12px] font-bold uppercase tracking-[0.22em] text-gold mb-3">
          Account created
        </div>
        <h2 className="font-display text-paper text-[26px] mb-3">
          Welcome, {success.name}.
        </h2>
        <p className="text-muted text-[15.5px] max-w-[440px] mx-auto mb-2">
          Your account has been created and is pending activation.
        </p>
        <p className="text-muted text-[13.5px] max-w-[440px] mx-auto mb-6">
          Email activation will land in a future update. For now, our team
          will be in touch about next steps.
        </p>
        <button
          type="button"
          onClick={() => setSuccess(null)}
          className="inline-flex items-center px-5 py-3 rounded-pill border border-line text-paper font-semibold hover:border-blue-bright transition"
        >
          Register another account
        </button>
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

      <Field id="name" label="Your full name" error={fieldErrors.name}>
        <input
          id="name"
          name="name"
          type="text"
          required
          autoComplete="name"
          value={form.name}
          onChange={(e) => update("name", e.target.value)}
          className={inputClass(!!fieldErrors.name)}
        />
      </Field>

      <Field id="email" label="Email" error={fieldErrors.email}>
        <input
          id="email"
          name="email"
          type="email"
          required
          autoComplete="email"
          value={form.email}
          onChange={(e) => update("email", e.target.value)}
          className={inputClass(!!fieldErrors.email)}
        />
      </Field>

      <Field
        id="phone"
        label="Phone (optional)"
        error={fieldErrors.phone}
        hint="Nigerian number — +234 703 591 8488 or 07035918488."
      >
        <input
          id="phone"
          name="phone"
          type="tel"
          autoComplete="tel"
          value={form.phone}
          onChange={(e) => update("phone", e.target.value)}
          className={inputClass(!!fieldErrors.phone)}
        />
      </Field>

      <Field
        id="password"
        label="Password"
        error={fieldErrors.password}
        hint="At least 8 characters."
      >
        <input
          id="password"
          name="password"
          type="password"
          required
          minLength={8}
          autoComplete="new-password"
          value={form.password}
          onChange={(e) => update("password", e.target.value)}
          className={inputClass(!!fieldErrors.password)}
        />
      </Field>

      <button
        type="submit"
        disabled={submitting}
        className="w-full inline-flex items-center justify-center px-5 py-3 rounded-pill bg-gradient-to-b from-blue to-blue-deep text-white font-semibold shadow-[0_10px_24px_-10px_rgba(31,99,201,0.55)] hover:from-blue-bright transition disabled:opacity-60 disabled:cursor-not-allowed"
      >
        {submitting ? "Creating account…" : "Create account"}
      </button>
    </form>
  );
}

function inputClass(hasError: boolean): string {
  const base =
    "w-full bg-page border rounded-md px-3 py-2.5 text-paper text-[15px] focus:outline-none transition";
  if (hasError) {
    return `${base} border-danger focus:border-danger focus:shadow-[0_0_0_3px_rgba(210,74,74,0.25)]`;
  }
  return `${base} border-line focus:border-blue-bright focus:shadow-[0_0_0_3px_rgba(47,127,212,0.25)]`;
}

function Field({
  id,
  label,
  error,
  hint,
  children,
}: {
  id: string;
  label: string;
  error?: string;
  hint?: string;
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

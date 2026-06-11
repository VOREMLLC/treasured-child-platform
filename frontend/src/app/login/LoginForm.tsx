"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState, type FormEvent } from "react";

import { ApiError, postLogin } from "@/lib/api";

interface FormState {
  email: string;
  password: string;
}

const INITIAL: FormState = { email: "", password: "" };

export function LoginForm() {
  const router = useRouter();
  const [form, setForm] = useState<FormState>(INITIAL);
  const [submitting, setSubmitting] = useState(false);
  const [topError, setTopError] = useState<string | null>(null);

  function update<K extends keyof FormState>(key: K, value: FormState[K]) {
    setForm((prev) => ({ ...prev, [key]: value }));
    if (topError) setTopError(null);
  }

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setTopError(null);
    setSubmitting(true);
    try {
      await postLogin({
        email: form.email.trim(),
        password: form.password,
      });
      // Cookies are now set by the response Set-Cookie headers.
      router.push("/portal");
    } catch (err) {
      if (err instanceof ApiError) {
        setTopError(err.message);
      } else {
        setTopError("Something unexpected happened. Please try again.");
      }
      setSubmitting(false);
    }
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

      <Field id="email" label="Email">
        <input
          id="email"
          name="email"
          type="email"
          required
          autoComplete="email"
          value={form.email}
          onChange={(e) => update("email", e.target.value)}
          className="w-full bg-page border border-line rounded-md px-3 py-2.5 text-paper text-[15px] focus:outline-none focus:border-blue-bright focus:shadow-[0_0_0_3px_rgba(47,127,212,0.25)] transition"
        />
      </Field>

      <Field id="password" label="Password">
        <input
          id="password"
          name="password"
          type="password"
          required
          autoComplete="current-password"
          value={form.password}
          onChange={(e) => update("password", e.target.value)}
          className="w-full bg-page border border-line rounded-md px-3 py-2.5 text-paper text-[15px] focus:outline-none focus:border-blue-bright focus:shadow-[0_0_0_3px_rgba(47,127,212,0.25)] transition"
        />
      </Field>

      <div className="flex items-center justify-between">
        <Link
          href="/forgot-password"
          className="text-muted text-[13px] hover:text-blue-soft transition"
        >
          Forgot password?
        </Link>
      </div>

      <button
        type="submit"
        disabled={submitting}
        className="w-full inline-flex items-center justify-center px-5 py-3 rounded-pill bg-gradient-to-b from-blue to-blue-deep text-white font-semibold shadow-[0_10px_24px_-10px_rgba(31,99,201,0.55)] hover:from-blue-bright transition disabled:opacity-60 disabled:cursor-not-allowed"
      >
        {submitting ? "Signing in…" : "Sign in"}
      </button>
    </form>
  );
}

function Field({
  id,
  label,
  children,
}: {
  id: string;
  label: string;
  children: React.ReactNode;
}) {
  return (
    <div className="flex flex-col gap-1.5">
      <label htmlFor={id} className="text-[13px] font-semibold text-paper">
        {label}
      </label>
      {children}
    </div>
  );
}

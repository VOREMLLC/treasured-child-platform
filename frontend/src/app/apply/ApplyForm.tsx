"use client";

import { useState, type FormEvent } from "react";

import {
  ApiError,
  postApplication,
  type ApplicationCreate,
  type ClassLevel,
} from "@/lib/api";

interface FormState {
  child_name: string;
  guardian_name: string;
  email: string;
  phone: string;
  class_level: ClassLevel | "";
  message: string;
}

const INITIAL: FormState = {
  child_name: "",
  guardian_name: "",
  email: "",
  phone: "",
  class_level: "",
  message: "",
};

const CLASS_OPTIONS: { value: ClassLevel; label: string }[] = [
  { value: "nursery", label: "Nursery" },
  { value: "primary", label: "Primary" },
  { value: "junior_secondary", label: "Junior secondary" },
  { value: "senior_secondary", label: "Senior secondary" },
];

export function ApplyForm() {
  const [form, setForm] = useState<FormState>(INITIAL);
  const [submitting, setSubmitting] = useState(false);
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});
  const [topError, setTopError] = useState<string | null>(null);
  const [success, setSuccess] = useState<{ guardianName: string } | null>(
    null,
  );

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

    if (!form.class_level) {
      setFieldErrors({ class_level: "Please choose a level." });
      return;
    }

    const payload: ApplicationCreate = {
      child_name: form.child_name.trim(),
      guardian_name: form.guardian_name.trim(),
      email: form.email.trim(),
      phone: form.phone.trim(),
      class_level: form.class_level,
      message: form.message.trim() || undefined,
    };

    setSubmitting(true);
    try {
      await postApplication(payload);
      setSuccess({ guardianName: payload.guardian_name });
      setForm(INITIAL);
    } catch (err) {
      if (err instanceof ApiError) {
        const fieldMap: Record<string, string> = {};
        for (const fe of err.fieldErrors) {
          if (fe.field) fieldMap[fe.field] = fe.message;
        }
        setFieldErrors(fieldMap);
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
          Application received
        </div>
        <h2 className="font-display text-paper text-[28px] mb-3">
          Thank you, {success.guardianName}.
        </h2>
        <p className="text-muted text-[16px] max-w-[520px] mx-auto mb-2">
          Your application has been received. Our admissions team will be in
          touch by email within 48 hours.
        </p>
        <p className="text-muted text-[14px] max-w-[520px] mx-auto mb-6">
          A confirmation email is on its way to the address you provided.
        </p>
        <button
          type="button"
          onClick={() => setSuccess(null)}
          className="inline-flex items-center px-5 py-3 rounded-pill border border-line text-paper font-semibold hover:border-blue-bright transition"
        >
          Submit another application
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

      <Field
        id="child_name"
        label="Child's name"
        error={fieldErrors.child_name}
      >
        <input
          id="child_name"
          name="child_name"
          type="text"
          required
          autoComplete="off"
          value={form.child_name}
          onChange={(e) => update("child_name", e.target.value)}
          className={inputClass(!!fieldErrors.child_name)}
        />
      </Field>

      <Field
        id="guardian_name"
        label="Parent or guardian's name"
        error={fieldErrors.guardian_name}
      >
        <input
          id="guardian_name"
          name="guardian_name"
          type="text"
          required
          autoComplete="name"
          value={form.guardian_name}
          onChange={(e) => update("guardian_name", e.target.value)}
          className={inputClass(!!fieldErrors.guardian_name)}
        />
      </Field>

      <Field
        id="email"
        label="Email"
        error={fieldErrors.email}
        hint="We'll send a confirmation here."
      >
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
        label="Phone"
        error={fieldErrors.phone}
        hint="Nigerian number, e.g. +234 703 591 8488 or 07035918488."
      >
        <input
          id="phone"
          name="phone"
          type="tel"
          required
          autoComplete="tel"
          value={form.phone}
          onChange={(e) => update("phone", e.target.value)}
          className={inputClass(!!fieldErrors.phone)}
        />
      </Field>

      <Field
        id="class_level"
        label="Level applying for"
        error={fieldErrors.class_level}
      >
        <select
          id="class_level"
          name="class_level"
          required
          value={form.class_level}
          onChange={(e) =>
            update("class_level", e.target.value as ClassLevel | "")
          }
          className={inputClass(!!fieldErrors.class_level)}
        >
          <option value="" disabled>
            Choose a level…
          </option>
          {CLASS_OPTIONS.map((opt) => (
            <option key={opt.value} value={opt.value}>
              {opt.label}
            </option>
          ))}
        </select>
      </Field>

      <Field
        id="message"
        label="Message (optional)"
        error={fieldErrors.message}
      >
        <textarea
          id="message"
          name="message"
          rows={4}
          value={form.message}
          onChange={(e) => update("message", e.target.value)}
          className={inputClass(!!fieldErrors.message) + " resize-y"}
        />
      </Field>

      <button
        type="submit"
        disabled={submitting}
        className="inline-flex items-center px-5 py-3 rounded-pill bg-gradient-to-b from-blue to-blue-deep text-white font-semibold shadow-[0_10px_24px_-10px_rgba(31,99,201,0.55)] hover:from-blue-bright transition disabled:opacity-60 disabled:cursor-not-allowed"
      >
        {submitting ? "Submitting…" : "Submit application"}
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

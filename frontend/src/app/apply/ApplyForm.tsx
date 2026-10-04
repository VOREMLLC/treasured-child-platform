"use client";

import { useState, type FormEvent } from "react";

import { Button, ButtonLink } from "@/components/Button";
import { ChoiceTiles, type ChoiceOption } from "@/components/ChoiceTiles";
import { FormAlert, TextAreaField, TextField } from "@/components/Field";
import { Icon } from "@/components/Icon";
import {
  ApiError,
  postApplication,
  type ApplicationCreate,
  type ClassLevel,
} from "@/lib/api";
import { firstName } from "@/lib/useApi";

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

const LEVELS: ChoiceOption<ClassLevel>[] = [
  { value: "nursery", title: "Nursery", description: "Ages 3 to 5", icon: "heart" },
  { value: "primary", title: "Primary", description: "Ages 6 to 11", icon: "book" },
  {
    value: "junior_secondary",
    title: "Junior secondary",
    description: "JSS 1 to 3",
    icon: "school",
  },
  {
    value: "senior_secondary",
    title: "Senior secondary",
    description: "SS 1 to 3",
    icon: "star",
  },
];

export function ApplyForm() {
  const [form, setForm] = useState<FormState>(INITIAL);
  const [submitting, setSubmitting] = useState(false);
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});
  const [topError, setTopError] = useState<string | null>(null);
  const [showNote, setShowNote] = useState(false);
  const [doneFor, setDoneFor] = useState<string | null>(null);

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
      setFieldErrors({ class_level: "Please choose a class." });
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
      setDoneFor(payload.guardian_name);
      setForm(INITIAL);
      window.scrollTo({ top: 0 });
    } catch (err) {
      if (err instanceof ApiError) {
        const map: Record<string, string> = {};
        for (const fe of err.fieldErrors) {
          if (fe.field) map[fe.field] = fe.message;
        }
        setFieldErrors(map);
        if (map.message) setShowNote(true);
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

  if (doneFor) {
    return (
      <section
        role="status"
        className="rounded-card border border-line bg-card px-5 py-10 text-center shadow-s"
      >
        <span className="mx-auto mb-5 grid h-24 w-24 place-items-center rounded-full bg-success text-white motion-safe:animate-celebrate">
          <Icon name="check" size={52} strokeWidth={3} />
        </span>
        <h2 className="font-display text-h3 font-bold text-ink sm:text-h2">
          Thank you, {firstName(doneFor)}!
        </h2>
        <p className="mx-auto mt-2 max-w-[40ch] text-label text-muted">
          We&apos;ll call or WhatsApp you within 48 hours.
        </p>
        <div className="mx-auto mt-6 flex max-w-[360px] flex-col gap-3">
          <ButtonLink href="/pay" full>
            Pay fees
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

      <ChoiceTiles
        name="class_level"
        legend="Which class?"
        options={LEVELS}
        value={form.class_level}
        onChange={(v) => update("class_level", v)}
        error={fieldErrors.class_level}
        grid
      />

      <TextField
        id="child_name"
        label="Child's name"
        type="text"
        required
        autoComplete="off"
        value={form.child_name}
        onChange={(e) => update("child_name", e.target.value)}
        error={fieldErrors.child_name}
      />

      <TextField
        id="guardian_name"
        label="Your name"
        type="text"
        required
        autoComplete="name"
        value={form.guardian_name}
        onChange={(e) => update("guardian_name", e.target.value)}
        error={fieldErrors.guardian_name}
      />

      <TextField
        id="phone"
        label="Phone (WhatsApp)"
        type="tel"
        inputMode="tel"
        required
        autoComplete="tel"
        placeholder="0803 123 4567"
        value={form.phone}
        onChange={(e) => update("phone", e.target.value)}
        error={fieldErrors.phone}
        hint="We'll call or WhatsApp you on this number."
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
        hint="We'll send a copy of your application here."
      />

      {showNote ? (
        <TextAreaField
          id="message"
          label="Your note"
          optional
          value={form.message}
          onChange={(e) => update("message", e.target.value)}
          error={fieldErrors.message}
          autoFocus
        />
      ) : (
        <Button variant="ghost" onClick={() => setShowNote(true)} icon="sparkle">
          Add a note
        </Button>
      )}

      {/* Sticky on phones so the button is always one thumb away. */}
      <div className="sticky bottom-[calc(64px+env(safe-area-inset-bottom))] z-10 -mx-4 bg-page px-4 py-3 sm:-mx-6 sm:px-6 md:static md:mx-0 md:bg-transparent md:px-0 md:py-0">
        <Button type="submit" size="lg" full loading={submitting}>
          Apply now
        </Button>
      </div>
    </form>
  );
}

"use client";

import { useState, type FormEvent } from "react";

import {
  ApiError,
  postPaymentsInitialize,
  postPaymentsVerify,
  type PaymentInitializeResponse,
  type PaymentPurpose,
  type PaymentResponse,
} from "@/lib/api";

// Paystack inline widget — loaded via <Script> in page.tsx.
interface PaystackConfig {
  key: string;
  email: string;
  amount: number;
  ref: string;
  currency?: string;
  callback: (response: { reference: string; status?: string }) => void;
  onClose: () => void;
}
declare global {
  interface Window {
    PaystackPop?: {
      setup: (config: PaystackConfig) => { openIframe: () => void };
    };
  }
}

interface Option {
  label: string;
  purpose: PaymentPurpose;
  target?: string;
}

const OPTIONS: Option[] = [
  { label: "Term fees (₦125,000)", purpose: "fees" },
  { label: "BECE / Common entrance prep (₦20,000)", purpose: "programme", target: "bece-prep" },
  { label: "AI & data analytics (₦35,000)", purpose: "programme", target: "ai-data" },
];

function formatNgn(kobo: number): string {
  return `₦${(kobo / 100).toLocaleString("en-NG")}`;
}

function looksLikePlaceholderKey(key: string): boolean {
  // Real Paystack test keys are pk_test_<32 hex chars>. Our default
  // placeholder is 'pk_test_xxx' — anything that obviously isn't real.
  return /xxx/i.test(key) || key.length < 16;
}

export function PayForm() {
  const [optionIdx, setOptionIdx] = useState(0);
  const [submitting, setSubmitting] = useState(false);
  const [topError, setTopError] = useState<string | null>(null);
  const [initialized, setInitialized] =
    useState<PaymentInitializeResponse | null>(null);
  const [verifying, setVerifying] = useState(false);
  const [result, setResult] = useState<PaymentResponse | null>(null);

  const selected = OPTIONS[optionIdx];

  async function onInitialize(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setTopError(null);
    setResult(null);
    setSubmitting(true);
    try {
      const init = await postPaymentsInitialize({
        purpose: selected.purpose,
        target: selected.target,
      });
      setInitialized(init);
    } catch (err) {
      if (err instanceof ApiError) {
        if (err.status === 401) {
          setTopError(
            "Please sign in first. Use the link below the form.",
          );
        } else {
          setTopError(err.message);
        }
      } else {
        setTopError("Could not start the payment. Please try again.");
      }
    } finally {
      setSubmitting(false);
    }
  }

  function openPaystack() {
    if (!initialized) return;
    if (typeof window === "undefined" || !window.PaystackPop) {
      setTopError(
        "The Paystack widget is still loading. Wait a moment and try again.",
      );
      return;
    }
    const handler = window.PaystackPop.setup({
      key: initialized.public_key,
      email: initialized.payer_email,
      amount: initialized.amount_kobo,
      ref: initialized.reference,
      currency: "NGN",
      callback: (response) => {
        // Paystack invokes this on successful charge. Hand off to verify.
        void doVerify(response.reference);
      },
      onClose: () => {
        // User dismissed the popup before paying. No-op.
      },
    });
    handler.openIframe();
  }

  async function doVerify(reference: string) {
    setVerifying(true);
    setTopError(null);
    try {
      const verified = await postPaymentsVerify({ reference });
      setResult(verified);
    } catch (err) {
      if (err instanceof ApiError) {
        setTopError(err.message);
      } else {
        setTopError("Verification failed. Please contact admissions.");
      }
    } finally {
      setVerifying(false);
    }
  }

  // ── Success / failure card ────────────────────────────────
  if (result) {
    if (result.status === "success") {
      return (
        <article
          role="status"
          className="bg-card border border-line rounded-lg p-8 text-center"
        >
          <div className="inline-flex items-center gap-2 text-[12px] font-bold uppercase tracking-[0.22em] text-gold mb-3">
            Payment received
          </div>
          <h2 className="font-display text-paper text-[24px] mb-3">
            {formatNgn(result.amount_kobo)} — thank you.
          </h2>
          <p className="text-muted text-[15px] max-w-[440px] mx-auto mb-2">
            Reference: <span className="text-paper font-mono">{result.reference}</span>
          </p>
          <p className="text-muted text-[13.5px] max-w-[440px] mx-auto">
            A receipt email will land in your inbox shortly (when the
            stubbed sender is replaced by the real provider).
          </p>
        </article>
      );
    }
    return (
      <article
        role="alert"
        className="bg-card border border-danger/40 rounded-lg p-8 text-center"
      >
        <div className="inline-flex items-center gap-2 text-[12px] font-bold uppercase tracking-[0.22em] text-danger mb-3">
          Verification failed
        </div>
        <p className="text-muted text-[15px] max-w-[440px] mx-auto">
          We couldn&apos;t confirm that payment with Paystack. No charge
          was applied if you didn&apos;t complete the form. Contact
          admissions if you believe this is a mistake.
        </p>
      </article>
    );
  }

  // ── After initialize: show summary + Pay with Paystack ──────────
  if (initialized) {
    const placeholder = looksLikePlaceholderKey(initialized.public_key);
    return (
      <article className="bg-card border border-line rounded-lg p-6 sm:p-8 space-y-5">
        <div>
          <div className="text-[12px] font-bold uppercase tracking-[0.18em] text-gold mb-2">
            Ready to pay
          </div>
          <h2 className="font-display text-paper text-[22px] mb-2">
            {formatNgn(initialized.amount_kobo)}
          </h2>
          <p className="text-muted text-[14px]">
            For:{" "}
            <span className="text-paper">
              {OPTIONS.find(
                (o) =>
                  o.purpose === initialized.purpose &&
                  o.target === initialized.target,
              )?.label ?? initialized.purpose}
            </span>
          </p>
          <p className="text-muted text-[12.5px] mt-1">
            Reference:{" "}
            <span className="text-paper font-mono">
              {initialized.reference}
            </span>
          </p>
        </div>

        {placeholder ? (
          <div
            role="alert"
            className="rounded-md border border-warning/40 bg-[rgba(217,154,28,0.10)] px-4 py-3 text-[13.5px] text-warning"
          >
            Paystack test keys aren&apos;t configured. Set{" "}
            <code className="font-mono text-[13px]">PAYSTACK_PUBLIC_KEY</code>{" "}
            and{" "}
            <code className="font-mono text-[13px]">PAYSTACK_SECRET_KEY</code>{" "}
            in <code className="font-mono text-[13px]">backend/.env</code>{" "}
            to enable the inline widget. The Payment row was still
            recorded server-side with status=pending.
          </div>
        ) : (
          <button
            type="button"
            onClick={openPaystack}
            disabled={verifying}
            className="w-full inline-flex items-center justify-center px-5 py-3 rounded-pill bg-gradient-to-b from-gold to-gold-deep text-ink font-semibold hover:brightness-105 transition disabled:opacity-60"
          >
            {verifying ? "Verifying…" : "Pay with Paystack"}
          </button>
        )}

        <button
          type="button"
          onClick={() => {
            setInitialized(null);
            setTopError(null);
          }}
          className="w-full text-muted text-[13px] hover:text-blue-soft transition"
        >
          ← Choose a different payment
        </button>
      </article>
    );
  }

  // ── Initial form: pick what to pay for ────────────────────
  return (
    <form
      onSubmit={onInitialize}
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

      <fieldset className="space-y-2">
        <legend className="text-[13px] font-semibold text-paper mb-2">
          What are you paying for?
        </legend>
        {OPTIONS.map((opt, i) => (
          <label
            key={opt.label}
            className={
              "flex items-center gap-3 rounded-md border px-4 py-3 cursor-pointer transition " +
              (i === optionIdx
                ? "border-blue-bright bg-[rgba(47,127,212,0.10)]"
                : "border-line hover:border-blue-deep")
            }
          >
            <input
              type="radio"
              name="purpose"
              checked={i === optionIdx}
              onChange={() => setOptionIdx(i)}
              className="accent-blue"
            />
            <span className="text-paper text-[14.5px]">{opt.label}</span>
          </label>
        ))}
      </fieldset>

      <button
        type="submit"
        disabled={submitting}
        className="w-full inline-flex items-center justify-center px-5 py-3 rounded-pill bg-gradient-to-b from-blue to-blue-deep text-white font-semibold shadow-[0_10px_24px_-10px_rgba(31,99,201,0.55)] hover:from-blue-bright transition disabled:opacity-60 disabled:cursor-not-allowed"
      >
        {submitting ? "Starting…" : "Continue"}
      </button>
    </form>
  );
}

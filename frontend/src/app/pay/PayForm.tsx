"use client";

import { useSearchParams } from "next/navigation";
import { useState } from "react";

import { Button, ButtonLink } from "@/components/Button";
import { ChoiceTiles, type ChoiceOption } from "@/components/ChoiceTiles";
import { EmptyState } from "@/components/EmptyState";
import { FormAlert } from "@/components/Field";
import { Icon } from "@/components/Icon";
import { Skeleton, SkeletonGroup } from "@/components/Skeleton";
import { ErrorCard, SignInPrompt } from "@/components/StatusViews";
import {
  ApiError,
  getMe,
  postPaymentsInitialize,
  postPaymentsVerify,
  type PaymentInitializeResponse,
  type PaymentResponse,
} from "@/lib/api";
import { SCHOOL_PHONE_DISPLAY, SCHOOL_PHONE_TEL } from "@/lib/contact";
import { PAY_CHOICES, formatNaira } from "@/lib/programmes";
import { useApi } from "@/lib/useApi";

// ── Paystack inline widget ──────────────────────────────────

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

const PAYSTACK_SRC = "https://js.paystack.co/v1/inline.js";

/** Load Paystack's script on demand (saves data for visitors who never pay). */
function loadPaystack(): Promise<void> {
  if (typeof window === "undefined") return Promise.reject(new Error("no window"));
  if (window.PaystackPop) return Promise.resolve();
  return new Promise((resolve, reject) => {
    const existing = document.querySelector<HTMLScriptElement>(
      `script[src="${PAYSTACK_SRC}"]`,
    );
    const script = existing ?? document.createElement("script");
    script.addEventListener("load", () => resolve(), { once: true });
    script.addEventListener("error", () => reject(new Error("load failed")), {
      once: true,
    });
    if (!existing) {
      script.src = PAYSTACK_SRC;
      script.async = true;
      document.body.appendChild(script);
    }
  });
}

function looksLikePlaceholderKey(key: string): boolean {
  // Real keys are pk_test_/pk_live_ plus 40 hex chars.
  return /xxx/i.test(key) || key.length < 16;
}

const IS_DEV = process.env.NODE_ENV !== "production";

// ── Component ──────────────────────────────────────────────

type Phase =
  | { kind: "choose" }
  | { kind: "paying" }
  | { kind: "verifying" }
  | { kind: "done"; payment: PaymentResponse }
  | { kind: "failed" };

const OPTIONS: ChoiceOption<string>[] = PAY_CHOICES.map((c) => ({
  value: c.key,
  title: c.title,
  description: c.description,
  price: formatNaira(c.priceNaira),
  icon: c.icon,
}));

export function PayForm() {
  const params = useSearchParams();
  const wanted = params.get("for");
  const initialKey =
    PAY_CHOICES.find((c) => c.key === wanted)?.key ?? PAY_CHOICES[0].key;
  const nextUrl = wanted ? `/pay?for=${wanted}` : "/pay";

  const { state: me, reload } = useApi(getMe, []);
  const [choiceKey, setChoiceKey] = useState<string>(initialKey);
  const [phase, setPhase] = useState<Phase>({ kind: "choose" });
  const [error, setError] = useState<string | null>(null);
  const [devNote, setDevNote] = useState<PaymentInitializeResponse | null>(null);

  const choice = PAY_CHOICES.find((c) => c.key === choiceKey) ?? PAY_CHOICES[0];

  async function verify(reference: string) {
    setPhase({ kind: "verifying" });
    try {
      const payment = await postPaymentsVerify({ reference });
      setPhase(
        payment.status === "success"
          ? { kind: "done", payment }
          : { kind: "failed" },
      );
    } catch {
      setPhase({ kind: "failed" });
    }
  }

  /** One tap: create the payment on our server, then open Paystack. */
  async function onPay() {
    setError(null);
    setDevNote(null);
    setPhase({ kind: "paying" });
    try {
      const init = await postPaymentsInitialize({
        purpose: choice.purpose,
        target: choice.target,
      });

      if (looksLikePlaceholderKey(init.public_key)) {
        if (IS_DEV) setDevNote(init);
        else
          setError(
            `Online payment is not available right now. Please call us on ${SCHOOL_PHONE_DISPLAY}.`,
          );
        setPhase({ kind: "choose" });
        return;
      }

      await loadPaystack();
      if (!window.PaystackPop) throw new Error("Paystack missing");

      // Paystack may fire onClose as the window shuts after a charge;
      // only treat it as "gave up" if no charge came back.
      let charged = false;

      window.PaystackPop.setup({
        key: init.public_key,
        email: init.payer_email,
        amount: init.amount_kobo,
        ref: init.reference,
        currency: "NGN",
        // Paystack calls this after a charge. We still confirm with our
        // own server; the browser's word is never trusted.
        callback: (response) => {
          charged = true;
          void verify(response.reference);
        },
        onClose: () => {
          if (charged) return;
          setPhase({ kind: "choose" });
          setError("Payment not finished. You can try again when you are ready.");
        },
      }).openIframe();
    } catch (err) {
      setPhase({ kind: "choose" });
      if (err instanceof ApiError && err.status === 401) {
        reload();
      } else if (err instanceof ApiError) {
        setError(err.message);
      } else {
        setError("We could not open the payment page. Check your internet and try again.");
      }
    }
  }

  // ── Screens ──────────────────────────────────────────────

  if (me.kind === "loading") {
    return (
      <SkeletonGroup label="Getting things ready">
        <Skeleton className="mb-3 h-6 w-48" />
        <Skeleton className="mb-3 h-20 w-full rounded-card" />
        <Skeleton className="mb-3 h-20 w-full rounded-card" />
        <Skeleton className="mb-6 h-20 w-full rounded-card" />
        <Skeleton className="h-14 w-full" />
      </SkeletonGroup>
    );
  }

  if (me.kind === "signed-out" || me.kind === "forbidden") {
    return (
      <SignInPrompt next={nextUrl} title="Sign in to pay">
        We link every payment to your account so you always have a record.
      </SignInPrompt>
    );
  }

  if (me.kind === "error") {
    return <ErrorCard message={me.message} onRetry={reload} />;
  }

  if (phase.kind === "verifying") {
    return (
      <EmptyState icon="card" title="Checking your payment" role="status">
        Please keep this page open. It only takes a moment.
      </EmptyState>
    );
  }

  if (phase.kind === "done") {
    return <PaidScreen payment={phase.payment} />;
  }

  if (phase.kind === "failed") {
    return (
      <EmptyState
        icon="alert"
        tone="danger"
        role="alert"
        title="We could not confirm that payment"
        actions={
          <>
            <Button onClick={() => setPhase({ kind: "choose" })}>Try again</Button>
            <ButtonLink href={SCHOOL_PHONE_TEL} external variant="secondary" icon="phone">
              Call the school
            </ButtonLink>
          </>
        }
      >
        If money left your account, do not pay again. Call us and we will
        sort it out.
      </EmptyState>
    );
  }

  const busy = phase.kind === "paying";

  return (
    <div className="space-y-6">
      {error && <FormAlert>{error}</FormAlert>}

      {devNote && (
        <div
          role="alert"
          className="rounded-control bg-warning-soft px-4 py-3 text-body text-warning"
        >
          Developer note: Paystack keys are not set, so the widget cannot
          open. The payment was recorded as pending.
        </div>
      )}

      <ChoiceTiles
        name="pay-for"
        legend="What are you paying for?"
        options={OPTIONS}
        value={choiceKey}
        onChange={setChoiceKey}
      />

      <div className="sticky bottom-[calc(64px+env(safe-area-inset-bottom))] z-10 -mx-4 bg-page px-4 py-3 sm:-mx-6 sm:px-6 md:static md:mx-0 md:bg-transparent md:px-0 md:py-0">
        <Button size="lg" full onClick={onPay} loading={busy} icon="lock">
          {busy ? "Opening Paystack" : `Pay ${formatNaira(choice.priceNaira)}`}
        </Button>
      </div>
      <p className="flex items-center justify-center gap-2 text-caption text-muted">
        <Icon name="shield" size={18} />
        Card, bank transfer or USSD, secured by Paystack.
      </p>
    </div>
  );
}

function PaidScreen({ payment }: { payment: PaymentResponse }) {
  return (
    <section
      role="status"
      className="rounded-card border border-line bg-card px-5 py-10 text-center shadow-s"
    >
      <span className="mx-auto mb-5 grid h-24 w-24 place-items-center rounded-full bg-success text-white motion-safe:animate-celebrate">
        <Icon name="check" size={52} strokeWidth={3} />
      </span>
      <h2 className="font-display text-h2 font-bold text-ink">
        Paid. Thank you.
      </h2>
      <p className="mt-2 text-label text-muted">
        {formatNaira(payment.amount_kobo / 100)} received. A receipt is on
        its way to your email.
      </p>
      <div className="mx-auto mt-6 flex max-w-[360px] flex-col gap-3">
        <ButtonLink href="/portal" full>
          Back to home
        </ButtonLink>
      </div>
      <details className="mx-auto mt-6 max-w-[360px] text-left text-caption text-muted">
        <summary className="flex min-h-12 cursor-pointer items-center justify-center gap-1 font-semibold">
          Details
          <Icon name="chevron-down" size={18} />
        </summary>
        <p className="mt-1 break-all text-center">
          Payment reference: {payment.reference}
        </p>
      </details>
    </section>
  );
}

"use client";

import { useState } from "react";

import { Button } from "@/components/Button";
import { EmptyState } from "@/components/EmptyState";
import { Skeleton, SkeletonCard, SkeletonGroup } from "@/components/Skeleton";
import { ErrorCard, SignInPrompt } from "@/components/StatusViews";
import {
  AdminApplication,
  AdminKpis,
  AdminPayment,
  AdminUser,
  ApiError,
  ApplicationStatus,
  FlaggedRun,
  UserStatus,
  getAdminApplications,
  getAdminKpis,
  getAdminPayments,
  getAdminUsers,
  getFlaggedRuns,
  setApplicationStatus,
  setUserStatus,
} from "@/lib/api";
import { useApi } from "@/lib/useApi";

type Tab = "accounts" | "applications" | "payments" | "safety";

interface OfficeData {
  users: AdminUser[];
  applications: AdminApplication[];
  payments: AdminPayment[];
  kpis: AdminKpis;
  flagged: FlaggedRun[];
}

async function loadOffice(): Promise<OfficeData> {
  const [users, applications, payments, kpis, flagged] = await Promise.all([
    getAdminUsers(),
    getAdminApplications(),
    getAdminPayments(),
    getAdminKpis(),
    getFlaggedRuns(),
  ]);
  return { users, applications, payments, kpis, flagged };
}

const naira = (kobo: number) =>
  `₦${(kobo / 100).toLocaleString("en-NG", { maximumFractionDigits: 0 })}`;

const when = (iso: string) =>
  new Date(iso).toLocaleString("en-NG", {
    day: "numeric",
    month: "short",
    hour: "2-digit",
    minute: "2-digit",
  });

const LEVELS: Record<string, string> = {
  nursery: "Nursery",
  primary: "Primary",
  junior_secondary: "Junior secondary",
  senior_secondary: "Senior secondary",
};

const STATUS_TONE: Record<string, string> = {
  pending: "bg-warning-soft text-warning",
  new: "bg-warning-soft text-warning",
  active: "bg-success-soft text-success",
  success: "bg-success-soft text-success",
  enrolled: "bg-success-soft text-success",
  contacted: "bg-blue-soft text-blue-ink",
  suspended: "bg-danger-soft text-danger",
  failed: "bg-danger-soft text-danger",
  rejected: "bg-danger-soft text-danger",
};

function Chip({ value }: { value: string }) {
  return (
    <span
      className={`inline-flex rounded-full px-3 py-1 text-caption font-bold capitalize ${
        STATUS_TONE[value] ?? "bg-page text-muted"
      }`}
    >
      {value}
    </span>
  );
}

function Row({ children }: { children: React.ReactNode }) {
  return (
    <li className="flex flex-col gap-3 rounded-card border border-line bg-card p-4 shadow-s sm:flex-row sm:items-center sm:justify-between">
      {children}
    </li>
  );
}

export function AdminView() {
  const { state, setData } = useApi(loadOffice, []);
  const [tab, setTab] = useState<Tab>("accounts");
  const [busy, setBusy] = useState<string | null>(null);
  const [actionError, setActionError] = useState<string | null>(null);

  if (state.kind === "loading") {
    return (
      <SkeletonGroup label="Opening the school office">
        <Skeleton className="mb-6 h-11 w-64" />
        <SkeletonCard className="mb-3" />
        <SkeletonCard />
      </SkeletonGroup>
    );
  }
  if (state.kind === "signed-out") {
    return <SignInPrompt next="/admin" title="School office">Sign in with the admin account.</SignInPrompt>;
  }
  if (state.kind === "forbidden") {
    return (
      <EmptyState icon="lock" title="This page is for the school office">
        Your account does not have access. Please ask the head of school.
      </EmptyState>
    );
  }
  if (state.kind === "error") return <ErrorCard message={state.message} />;

  const data = state.data;
  const pending = data.users.filter((u) => u.status === "pending");
  const newApps = data.applications.filter((a) => a.status === "new");

  async function changeUser(user: AdminUser, status: UserStatus) {
    setBusy(user.id);
    setActionError(null);
    try {
      const updated = await setUserStatus(user.id, status);
      setData({
        ...data,
        users: data.users.map((u) => (u.id === updated.id ? { ...u, status: updated.status } : u)),
      });
    } catch (err) {
      setActionError(err instanceof ApiError ? err.message : "That did not save. Please try again.");
    } finally {
      setBusy(null);
    }
  }

  async function changeApplication(app: AdminApplication, status: ApplicationStatus) {
    setBusy(app.id);
    setActionError(null);
    try {
      const updated = await setApplicationStatus(app.id, status);
      setData({
        ...data,
        applications: data.applications.map((a) =>
          a.id === updated.id ? { ...a, status: updated.status } : a,
        ),
      });
    } catch (err) {
      setActionError(err instanceof ApiError ? err.message : "That did not save. Please try again.");
    } finally {
      setBusy(null);
    }
  }

  const tabs: { id: Tab; label: string; count: number }[] = [
    { id: "accounts", label: "Accounts to approve", count: pending.length },
    { id: "applications", label: "New applications", count: newApps.length },
    { id: "payments", label: "Payments", count: 0 },
    { id: "safety", label: "Safety alerts", count: data.flagged.length },
  ];

  // Pending accounts first so approvals are the first thing the office sees.
  const users = [...data.users].sort(
    (a, b) => Number(b.status === "pending") - Number(a.status === "pending"),
  );

  return (
    <div className="space-y-8">
      <div>
        <h1 className="font-display text-[32px] font-bold text-ink sm:text-[36px]">School office</h1>
        <p className="mt-2 text-body text-muted">Approve new accounts, follow up applications and check payments.</p>
      </div>

      <dl className="grid grid-cols-2 gap-3 md:grid-cols-4">
        {[
          ["Fees received", naira(data.kpis.total_revenue_kobo)],
          ["Enrolments", String(data.kpis.total_enrolments)],
          ["Active learners this week", String(data.kpis.weekly_active_learners)],
          ["Courses completed", String(data.kpis.course_completions)],
        ].map(([label, value]) => (
          <div key={label} className="rounded-card border border-line bg-card p-4 shadow-s">
            <dt className="text-caption text-muted">{label}</dt>
            <dd className="mt-1 font-display text-title font-bold tabular-nums text-ink">{value}</dd>
          </div>
        ))}
      </dl>

      <div role="tablist" aria-label="Office sections" className="flex flex-wrap gap-2">
        {tabs.map((t) => (
          <button
            key={t.id}
            role="tab"
            type="button"
            aria-selected={tab === t.id}
            onClick={() => setTab(t.id)}
            className={`inline-flex min-h-12 items-center gap-2 rounded-control border px-4 text-body font-bold transition active:scale-[.98] ${
              tab === t.id ? "border-blue bg-blue text-white" : "border-line bg-card text-ink"
            }`}
          >
            {t.label}
            {t.count > 0 && (
              <span className={`rounded-full px-2 text-caption ${tab === t.id ? "bg-white text-blue-ink" : "bg-gold text-ink"}`}>
                {t.count}
              </span>
            )}
          </button>
        ))}
      </div>

      {actionError && (
        <p role="alert" className="rounded-control bg-danger-soft p-3 text-body text-danger">{actionError}</p>
      )}

      {tab === "accounts" && (
        <ul className="space-y-3">
          {users.length === 0 && <EmptyState icon="user" title="No accounts yet">New sign-ups appear here.</EmptyState>}
          {users.map((u) => (
            <Row key={u.id}>
              <div className="min-w-0">
                <p className="font-bold text-ink">{u.name || "(no name)"} <Chip value={u.status} /></p>
                <p className="break-all text-caption text-muted">{u.email} · {u.role} · joined {when(u.created_at)}</p>
              </div>
              <div className="flex flex-wrap gap-2">
                {u.status !== "active" && (
                  <Button loading={busy === u.id} onClick={() => changeUser(u, "active")} icon="check">
                    Approve
                  </Button>
                )}
                {u.status === "active" && u.role !== "admin" && (
                  <Button variant="secondary" loading={busy === u.id} onClick={() => changeUser(u, "suspended")}>
                    Switch off
                  </Button>
                )}
              </div>
            </Row>
          ))}
        </ul>
      )}

      {tab === "applications" && (
        <ul className="space-y-3">
          {data.applications.length === 0 && (
            <EmptyState icon="school" title="No applications yet">Applications from the website appear here.</EmptyState>
          )}
          {data.applications.map((a) => (
            <Row key={a.id}>
              <div className="min-w-0 space-y-1">
                <p className="font-bold text-ink">
                  {a.child_name} <span className="font-normal text-muted">· {LEVELS[a.class_level] ?? a.class_level}</span>{" "}
                  <Chip value={a.status} />
                </p>
                <p className="break-all text-caption text-muted">
                  Parent: {a.guardian_name} · {a.phone} · {a.email} · {when(a.created_at)}
                </p>
                {a.message && <p className="text-caption text-ink">“{a.message}”</p>}
              </div>
              <label className="flex flex-col gap-1 text-caption font-bold text-muted">
                Status
                <select
                  className="min-h-12 rounded-control border border-line bg-card px-3 text-body text-ink"
                  value={a.status}
                  disabled={busy === a.id}
                  onChange={(e) => changeApplication(a, e.target.value as ApplicationStatus)}
                >
                  <option value="new">New</option>
                  <option value="contacted">Contacted</option>
                  <option value="enrolled">Enrolled</option>
                  <option value="rejected">Not admitted</option>
                </select>
              </label>
            </Row>
          ))}
        </ul>
      )}

      {tab === "payments" && (
        <ul className="space-y-3">
          {data.payments.length === 0 && <EmptyState icon="card" title="No payments yet">Paystack payments appear here.</EmptyState>}
          {data.payments.map((p) => (
            <Row key={p.id}>
              <div className="min-w-0">
                <p className="font-bold tabular-nums text-ink">{naira(p.amount_kobo)} <Chip value={p.status} /></p>
                <p className="break-all text-caption text-muted">
                  {p.payer_email} · {p.purpose === "fees" ? "School fees" : p.target} · {when(p.created_at)} · ref {p.reference}
                </p>
              </div>
            </Row>
          ))}
        </ul>
      )}

      {tab === "safety" && (
        <ul className="space-y-3">
          {data.flagged.length === 0 && (
            <EmptyState icon="shield" title="No safety alerts">
              If the tutor sees a worrying message from a child, it appears here and the safeguarding lead is emailed.
            </EmptyState>
          )}
          {data.flagged.map((r) => (
            <Row key={r.id}>
              <div className="min-w-0 space-y-1">
                <p className="font-bold text-ink">{r.learner_name ?? "Unknown learner"} <span className="font-normal text-muted">· {when(r.created_at)}</span></p>
                {r.learner_email && <p className="break-all text-caption text-muted">{r.learner_email}</p>}
                <p className="rounded-control bg-warning-soft p-3 text-body text-ink">“{r.input}”</p>
              </div>
            </Row>
          ))}
        </ul>
      )}
    </div>
  );
}

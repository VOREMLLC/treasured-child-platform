"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import {
  ApiError,
  getMeCourses,
  type CourseListItem,
} from "@/lib/api";

type State =
  | { kind: "loading" }
  | { kind: "needs-signin" }
  | { kind: "error"; message: string }
  | { kind: "ready"; courses: CourseListItem[] };

export function CoursesList() {
  const [state, setState] = useState<State>({ kind: "loading" });

  useEffect(() => {
    let cancelled = false;
    getMeCourses()
      .then((courses) => {
        if (!cancelled) setState({ kind: "ready", courses });
      })
      .catch((err) => {
        if (cancelled) return;
        if (err instanceof ApiError && err.status === 401) {
          setState({ kind: "needs-signin" });
        } else if (err instanceof ApiError) {
          setState({ kind: "error", message: err.message });
        } else {
          setState({
            kind: "error",
            message: "Something unexpected happened. Please try again.",
          });
        }
      });
    return () => {
      cancelled = true;
    };
  }, []);

  if (state.kind === "loading") {
    return (
      <div
        role="status"
        className="bg-card border border-line rounded-lg p-6 text-muted text-center"
      >
        Loading your courses…
      </div>
    );
  }

  if (state.kind === "needs-signin") {
    return (
      <article className="bg-card border border-line rounded-lg p-8 text-center">
        <div className="inline-flex items-center gap-2 text-[12px] font-bold uppercase tracking-[0.22em] text-gold mb-3">
          Sign in required
        </div>
        <p className="text-muted text-[15px] max-w-[460px] mx-auto mb-6">
          Sign in to see the courses you&apos;re enrolled in.
        </p>
        <Link
          href="/login"
          className="inline-flex items-center px-5 py-3 rounded-pill bg-gradient-to-b from-blue to-blue-deep text-white font-semibold shadow-[0_10px_24px_-10px_rgba(31,99,201,0.55)] hover:from-blue-bright transition"
        >
          Sign in
        </Link>
      </article>
    );
  }

  if (state.kind === "error") {
    return (
      <article
        role="alert"
        className="bg-card border border-danger/40 rounded-lg p-6 text-center"
      >
        <p className="text-danger text-[15px]">{state.message}</p>
      </article>
    );
  }

  // state.kind === "ready"
  if (state.courses.length === 0) {
    return (
      <article className="bg-card border border-line rounded-lg p-10 text-center">
        <div className="inline-flex items-center gap-2 text-[12px] font-bold uppercase tracking-[0.22em] text-gold mb-3">
          No courses yet
        </div>
        <h2 className="font-display text-paper text-[22px] mb-3">
          You aren&apos;t enrolled in anything yet.
        </h2>
        <p className="text-muted text-[15px] max-w-[440px] mx-auto mb-6">
          Browse the catalogue to find a programme that suits you.
        </p>
        <Link
          href="/programmes"
          className="inline-flex items-center px-5 py-3 rounded-pill border border-line text-paper font-semibold hover:border-blue-bright transition"
        >
          Browse programmes
        </Link>
      </article>
    );
  }

  return (
    <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
      {state.courses.map((c) => (
        <CourseCard key={c.id} course={c} />
      ))}
    </div>
  );
}

function CourseCard({ course }: { course: CourseListItem }) {
  const typeLabel = course.type === "online" ? "Online" : "On campus";
  return (
    <Link
      href={`/portal/courses/${course.id}`}
      className="bg-card border border-line rounded-lg overflow-hidden flex flex-col transition hover:-translate-y-1 hover:shadow hover:border-blue-deep group"
    >
      <div
        className="h-20 grid place-items-center font-display text-[20px] tracking-tight"
        style={{
          background:
            course.type === "online"
              ? "linear-gradient(135deg, var(--blue), var(--blue-bright))"
              : "linear-gradient(135deg, var(--blue-deep), var(--navy))",
          color: "#fff",
        }}
      >
        {course.level || course.title}
      </div>
      <div className="p-5 flex flex-col flex-1">
        <span className="inline-block self-start text-[12px] font-semibold px-2.5 py-1 rounded-pill bg-[rgba(47,127,212,0.14)] text-blue-soft mb-2">
          {typeLabel}
        </span>
        <h3 className="font-display text-[18px] text-paper mb-1.5">
          {course.title}
        </h3>
        <p className="text-muted text-[14px] mb-3.5 flex-1">
          {course.summary}
        </p>
        <div className="mb-3.5">
          <div className="flex items-baseline justify-between mb-1">
            <span className="text-[11px] uppercase tracking-[0.16em] text-muted">
              Progress
            </span>
            <span className="text-[12px] font-semibold text-paper">
              {course.progress_percent}%
            </span>
          </div>
          <div
            role="progressbar"
            aria-valuenow={course.progress_percent}
            aria-valuemin={0}
            aria-valuemax={100}
            className="h-1.5 rounded-full overflow-hidden bg-line"
          >
            <div
              className="h-full bg-blue-bright transition-all"
              style={{ width: `${course.progress_percent}%` }}
            />
          </div>
        </div>
        <span className="text-blue-soft font-semibold text-[14px] inline-block transition group-hover:translate-x-0.5">
          Open →
        </span>
      </div>
    </Link>
  );
}

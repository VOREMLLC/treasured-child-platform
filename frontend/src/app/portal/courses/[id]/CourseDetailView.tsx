"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import { ApiError, getCourse, type CourseDetail } from "@/lib/api";

type State =
  | { kind: "loading" }
  | { kind: "needs-signin" }
  | { kind: "forbidden" }
  | { kind: "error"; message: string }
  | { kind: "ready"; course: CourseDetail };

export function CourseDetailView({ courseId }: { courseId: string }) {
  const [state, setState] = useState<State>({ kind: "loading" });

  useEffect(() => {
    let cancelled = false;
    getCourse(courseId)
      .then((course) => {
        if (!cancelled) setState({ kind: "ready", course });
      })
      .catch((err) => {
        if (cancelled) return;
        if (err instanceof ApiError && err.status === 401) {
          setState({ kind: "needs-signin" });
        } else if (err instanceof ApiError && err.status === 403) {
          setState({ kind: "forbidden" });
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
  }, [courseId]);

  if (state.kind === "loading") {
    return (
      <div
        role="status"
        className="bg-card border border-line rounded-lg p-6 text-muted text-center"
      >
        Loading…
      </div>
    );
  }

  if (state.kind === "needs-signin") {
    return (
      <article className="bg-card border border-line rounded-lg p-8 text-center">
        <p className="text-muted text-[15px] mb-4">
          Please sign in to view this course.
        </p>
        <Link
          href="/login"
          className="inline-flex items-center px-5 py-3 rounded-pill bg-gradient-to-b from-blue to-blue-deep text-white font-semibold transition"
        >
          Sign in
        </Link>
      </article>
    );
  }

  if (state.kind === "forbidden") {
    return (
      <article
        role="alert"
        className="bg-card border border-danger/40 rounded-lg p-8 text-center"
      >
        <div className="inline-flex items-center gap-2 text-[12px] font-bold uppercase tracking-[0.22em] text-danger mb-3">
          Not enrolled
        </div>
        <p className="text-muted text-[15px] max-w-[460px] mx-auto mb-6">
          You don&apos;t have access to this course. Enrol from the
          programmes catalogue to get started.
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

  const { course } = state;
  const typeLabel = course.type === "online" ? "Online" : "On campus";
  const totalLessons = course.modules.reduce(
    (sum, m) => sum + m.lessons.length,
    0,
  );
  const completedLessons = course.modules.reduce(
    (sum, m) => sum + m.lessons.filter((l) => l.completed).length,
    0,
  );

  return (
    <>
      {/* Header */}
      <header
        className="px-6 sm:px-10 py-10 rounded-xl mb-8"
        style={{
          background:
            course.type === "online"
              ? "linear-gradient(135deg, var(--blue), var(--blue-bright))"
              : "linear-gradient(135deg, var(--blue-deep), var(--navy))",
          color: "#fff",
        }}
      >
        <span className="inline-block text-[12px] font-semibold px-2.5 py-1 rounded-pill bg-[rgba(255,255,255,0.18)] mb-3">
          {typeLabel} · {course.level}
        </span>
        <h1 className="font-display font-bold text-[clamp(28px,4.5vw,44px)] leading-[1.1] tracking-tight mb-2">
          {course.title}
        </h1>
        <p className="text-[16px] max-w-[640px] opacity-90 mb-4">
          {course.summary}
        </p>
        <div className="text-[13px] opacity-85">
          Progress: {completedLessons}/{totalLessons} lessons complete
        </div>
      </header>

      {/* Body: two columns on lg, single column on small screens */}
      <div className="grid lg:grid-cols-[1.2fr_.8fr] gap-8">
        {/* Modules + lessons */}
        <div className="space-y-5">
          {course.modules.map((module) => (
            <article
              key={module.id}
              className="bg-card border border-line rounded-lg p-5"
            >
              <div className="flex items-baseline gap-3 mb-3">
                <span className="text-[12px] font-bold uppercase tracking-[0.18em] text-gold">
                  Module {module.sort_order}
                </span>
                <h2 className="font-display text-paper text-[18px]">
                  {module.title}
                </h2>
              </div>
              <ul className="divide-y divide-line/40">
                {module.lessons.map((lesson) => (
                  <li
                    key={lesson.id}
                    className="flex items-center gap-3 py-3"
                  >
                    <span
                      aria-hidden
                      className={
                        "w-7 h-7 rounded-full border flex items-center justify-center text-[12px] font-semibold " +
                        (lesson.completed
                          ? "border-success bg-[rgba(25,168,107,0.16)] text-success"
                          : "border-line text-muted")
                      }
                    >
                      {lesson.completed ? "✓" : lesson.sort_order}
                    </span>
                    <span className="flex-1 text-paper text-[14.5px]">
                      {lesson.title}
                    </span>
                    <span className="text-muted text-[12px]">
                      {lesson.duration_min} min
                    </span>
                  </li>
                ))}
              </ul>
            </article>
          ))}
        </div>

        {/* Right column placeholder for S16 lesson viewer */}
        <aside className="bg-card border border-line rounded-lg p-8 text-center min-h-[280px] grid place-items-center">
          <div>
            <div className="text-[12px] font-bold uppercase tracking-[0.22em] text-gold mb-3">
              Lesson viewer
            </div>
            <p className="text-muted text-[14.5px] max-w-[280px] mx-auto">
              Select a lesson from the list — the in-page lesson viewer
              arrives in slice S16.
            </p>
          </div>
        </aside>
      </div>
    </>
  );
}

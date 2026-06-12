"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import ReactMarkdown from "react-markdown";

import {
  ApiError,
  getLesson,
  postLessonComplete,
  type LessonDetail,
} from "@/lib/api";

type State =
  | { kind: "loading" }
  | { kind: "needs-signin" }
  | { kind: "forbidden" }
  | { kind: "error"; message: string }
  | { kind: "ready"; lesson: LessonDetail };

interface Props {
  courseId: string;
  lessonId: string;
}

export function LessonView({ courseId, lessonId }: Props) {
  const [state, setState] = useState<State>({ kind: "loading" });
  const [marking, setMarking] = useState(false);
  const [markError, setMarkError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    setState({ kind: "loading" });
    setMarkError(null);
    getLesson(courseId, lessonId)
      .then((lesson) => {
        if (!cancelled) setState({ kind: "ready", lesson });
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
  }, [courseId, lessonId]);

  async function onMarkComplete() {
    if (state.kind !== "ready") return;
    setMarking(true);
    setMarkError(null);
    try {
      const result = await postLessonComplete(state.lesson.id);
      setState({
        kind: "ready",
        lesson: { ...state.lesson, completed: result.completed },
      });
    } catch (err) {
      if (err instanceof ApiError) {
        setMarkError(err.message);
      } else {
        setMarkError("Could not mark complete. Please try again.");
      }
    } finally {
      setMarking(false);
    }
  }

  if (state.kind === "loading") {
    return (
      <div
        role="status"
        className="bg-card border border-line rounded-lg p-6 text-muted text-center"
      >
        Loading lesson…
      </div>
    );
  }

  if (state.kind === "needs-signin") {
    return (
      <article className="bg-card border border-line rounded-lg p-8 text-center">
        <p className="text-muted text-[15px] mb-4">
          Please sign in to view this lesson.
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
          Not available
        </div>
        <p className="text-muted text-[15px] max-w-[460px] mx-auto">
          This lesson isn&apos;t available. You might not be enrolled in
          the course, or the lesson doesn&apos;t exist.
        </p>
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

  const { lesson } = state;

  return (
    <>
      {/* Breadcrumb + title */}
      <div className="mb-6">
        <p className="text-muted text-[13px] mb-1">
          {lesson.course_title} · {lesson.module_title}
        </p>
        <div className="flex items-baseline gap-3 flex-wrap">
          <span className="text-[12px] font-bold uppercase tracking-[0.18em] text-gold">
            Lesson {lesson.sort_order}
          </span>
          <h1 className="font-display font-bold text-paper text-[clamp(28px,4vw,40px)] leading-[1.1]">
            {lesson.title}
          </h1>
          <span className="text-muted text-[13px]">
            {lesson.duration_min} min
          </span>
        </div>
      </div>

      {/* Two-column layout: content on left, tutor placeholder on right */}
      <div className="grid lg:grid-cols-[1.4fr_.6fr] gap-8">
        <div>
          {/* Optional media placeholder */}
          {lesson.media_url ? (
            <div className="bg-card border border-line rounded-lg overflow-hidden mb-6 aspect-video grid place-items-center">
              <p className="text-muted text-[14px]">
                Media: <span className="font-mono text-[12px]">{lesson.media_url}</span>
              </p>
            </div>
          ) : (
            <div
              className="bg-card border border-line rounded-lg p-6 mb-6 text-center"
              style={{
                background:
                  "repeating-linear-gradient(135deg, rgba(47,127,212,0.05) 0 14px, transparent 14px 28px), var(--card)",
              }}
            >
              <p className="text-muted text-[13px]">
                No media for this lesson.
              </p>
            </div>
          )}

          {/* Markdown content */}
          <article className="bg-card border border-line rounded-lg p-6 sm:p-8 prose-content">
            <ReactMarkdown
              components={{
                h1: ({ children }) => (
                  <h1 className="font-display text-paper text-[26px] mt-4 mb-3 first:mt-0">
                    {children}
                  </h1>
                ),
                h2: ({ children }) => (
                  <h2 className="font-display text-paper text-[22px] mt-5 mb-3">
                    {children}
                  </h2>
                ),
                h3: ({ children }) => (
                  <h3 className="font-display text-paper text-[18px] mt-4 mb-2">
                    {children}
                  </h3>
                ),
                p: ({ children }) => (
                  <p className="text-paper text-[15.5px] leading-relaxed mb-3.5">
                    {children}
                  </p>
                ),
                ul: ({ children }) => (
                  <ul className="list-disc pl-6 mb-3.5 text-paper text-[15.5px] space-y-1.5">
                    {children}
                  </ul>
                ),
                ol: ({ children }) => (
                  <ol className="list-decimal pl-6 mb-3.5 text-paper text-[15.5px] space-y-1.5">
                    {children}
                  </ol>
                ),
                code: ({ children }) => (
                  <code className="bg-page border border-line rounded px-1.5 py-0.5 text-[13.5px] font-mono text-blue-soft">
                    {children}
                  </code>
                ),
                strong: ({ children }) => (
                  <strong className="text-paper font-semibold">
                    {children}
                  </strong>
                ),
                a: ({ children, href }) => (
                  <a
                    href={href}
                    className="text-blue-soft hover:underline"
                    target="_blank"
                    rel="noreferrer"
                  >
                    {children}
                  </a>
                ),
              }}
            >
              {lesson.content}
            </ReactMarkdown>
          </article>

          {/* Mark complete */}
          <div className="mt-6 flex items-center gap-4 flex-wrap">
            {lesson.completed ? (
              <span className="inline-flex items-center gap-2 px-5 py-3 rounded-pill border border-success bg-[rgba(25,168,107,0.10)] text-success font-semibold">
                <span aria-hidden>✓</span> Completed
              </span>
            ) : (
              <button
                type="button"
                onClick={onMarkComplete}
                disabled={marking}
                className="inline-flex items-center px-5 py-3 rounded-pill bg-gradient-to-b from-blue to-blue-deep text-white font-semibold shadow-[0_10px_24px_-10px_rgba(31,99,201,0.55)] hover:from-blue-bright transition disabled:opacity-60 disabled:cursor-not-allowed"
              >
                {marking ? "Marking…" : "Mark complete"}
              </button>
            )}
            {markError && (
              <p className="text-danger text-[12.5px]">{markError}</p>
            )}
          </div>
        </div>

        {/* Tutor placeholder (S23) */}
        <aside className="bg-card border border-line rounded-lg p-6">
          <div className="text-[12px] font-bold uppercase tracking-[0.18em] text-gold mb-2">
            Ada — your tutor
          </div>
          <h3 className="font-display text-paper text-[18px] mb-2">
            Coming soon.
          </h3>
          <p className="text-muted text-[14px] mb-4">
            The VOREM AI tutor lives here. It will explain concepts in
            plain language, check your understanding, and adapt to your
            pace — with strict child-safety guardrails throughout.
          </p>
          <p className="text-muted text-[12.5px]">
            Arrives in slice S23 (tutor) + S24 (guardrails).
          </p>
        </aside>
      </div>

      {/* Prev / next navigation */}
      <nav
        aria-label="Lesson navigation"
        className="grid sm:grid-cols-2 gap-3 mt-10 pt-6 border-t border-line"
      >
        {lesson.prev ? (
          <Link
            href={`/portal/courses/${lesson.course_id}/lessons/${lesson.prev.id}`}
            className="flex flex-col p-4 rounded-lg border border-line hover:border-blue-deep transition"
          >
            <span className="text-[11.5px] uppercase tracking-[0.18em] text-muted mb-1">
              ← Previous
            </span>
            <span className="text-paper font-semibold text-[14.5px]">
              {lesson.prev.title}
            </span>
          </Link>
        ) : (
          <span />
        )}
        {lesson.next ? (
          <Link
            href={`/portal/courses/${lesson.course_id}/lessons/${lesson.next.id}`}
            className="flex flex-col p-4 rounded-lg border border-line hover:border-blue-deep transition sm:text-right"
          >
            <span className="text-[11.5px] uppercase tracking-[0.18em] text-muted mb-1">
              Next →
            </span>
            <span className="text-paper font-semibold text-[14.5px]">
              {lesson.next.title}
            </span>
          </Link>
        ) : (
          <span />
        )}
      </nav>
    </>
  );
}

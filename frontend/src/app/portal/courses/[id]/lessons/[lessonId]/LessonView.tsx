"use client";

import Link from "next/link";
import { useState } from "react";
import ReactMarkdown from "react-markdown";

import { Button, ButtonLink, buttonClasses } from "@/components/Button";
import { EmptyState } from "@/components/EmptyState";
import { FormAlert } from "@/components/Field";
import { Icon } from "@/components/Icon";
import { Skeleton, SkeletonGroup } from "@/components/Skeleton";
import { ErrorCard, SignInPrompt } from "@/components/StatusViews";
import {
  ApiError,
  getLesson,
  postLessonComplete,
} from "@/lib/api";
import { useApi } from "@/lib/useApi";
import { TutorCard } from "./TutorCard";

interface Props {
  courseId: string;
  lessonId: string;
}

export function LessonView({ courseId, lessonId }: Props) {
  const { state, setData, reload } = useApi(
    () => getLesson(courseId, lessonId),
    [courseId, lessonId],
  );
  const [marking, setMarking] = useState(false);
  const [markError, setMarkError] = useState<string | null>(null);
  const [celebrate, setCelebrate] = useState(false);

  const coursePath = `/portal/courses/${courseId}`;

  if (state.kind === "loading") {
    return (
      <SkeletonGroup label="Opening your lesson">
        <Skeleton className="mb-3 h-5 w-48" />
        <Skeleton className="mb-8 h-10 w-3/4" />
        <div className="max-w-[65ch] space-y-3">
          <Skeleton className="h-5 w-full" />
          <Skeleton className="h-5 w-full" />
          <Skeleton className="h-5 w-11/12" />
          <Skeleton className="h-5 w-4/5" />
        </div>
      </SkeletonGroup>
    );
  }
  if (state.kind === "signed-out") {
    return <SignInPrompt next={`${coursePath}/lessons/${lessonId}`} />;
  }
  if (state.kind === "forbidden") {
    return (
      <EmptyState
        icon="lock"
        title="This lesson is not open for you yet"
        actions={
          <ButtonLink href="/portal/courses" variant="secondary">
            My courses
          </ButtonLink>
        }
      >
        You may need to join the course first.
      </EmptyState>
    );
  }
  if (state.kind === "error") {
    return <ErrorCard message={state.message} onRetry={reload} />;
  }

  const lesson = state.data;

  async function onFinished() {
    setMarking(true);
    setMarkError(null);
    try {
      const result = await postLessonComplete(lesson.id);
      setData({ ...lesson, completed: result.completed });
      setCelebrate(true);
    } catch (err) {
      setMarkError(
        err instanceof ApiError ? err.message : "That did not save. Please try again.",
      );
    } finally {
      setMarking(false);
    }
  }

  const nextHref = lesson.next
    ? `/portal/courses/${lesson.course_id}/lessons/${lesson.next.id}`
    : null;

  return (
    <div className="grid gap-8 lg:grid-cols-[minmax(0,1fr)_320px]">
      <article>
        <p className="text-caption font-semibold text-muted">
          {lesson.course_title}, {lesson.module_title}
        </p>
        <h1 className="mt-1 font-display text-[32px] font-bold text-ink sm:text-h2">
          {lesson.title}
        </h1>
        <p className="mt-1 text-caption text-muted">
          About {lesson.duration_min} min
        </p>

        {lesson.media_url && <LessonMedia url={lesson.media_url} title={lesson.title} />}

        <div className="mt-6 max-w-[65ch] text-[18px] leading-[1.6] text-ink">
          <ReactMarkdown components={MARKDOWN}>{lesson.content}</ReactMarkdown>
        </div>

        {/* Finish + next */}
        <div className="mt-10 max-w-[65ch] rounded-card border border-line bg-card p-5 shadow-s">
          {lesson.completed ? (
            <div className="flex flex-col items-center gap-4 text-center sm:flex-row sm:text-left">
              <span className="relative grid h-16 w-16 shrink-0 place-items-center">
                <span
                  className={`grid h-16 w-16 place-items-center rounded-full bg-gold text-ink ${celebrate ? "motion-safe:animate-celebrate" : ""}`}
                >
                  <Icon name="check" size={34} strokeWidth={3} />
                </span>
                {celebrate && <Burst />}
              </span>
              <p className="flex-1 font-display text-title font-bold text-ink" role="status">
                {celebrate ? "Brilliant! Lesson done." : "You finished this lesson."}
              </p>
              {nextHref ? (
                <ButtonLink href={nextHref} size="lg" iconRight="arrow-right">
                  Next lesson
                </ButtonLink>
              ) : (
                <ButtonLink href={coursePath} size="lg">
                  Back to course
                </ButtonLink>
              )}
            </div>
          ) : (
            <>
              {markError && (
                <div className="mb-4">
                  <FormAlert>{markError}</FormAlert>
                </div>
              )}
              <Button size="lg" full onClick={onFinished} loading={marking} icon="check">
                I finished this!
              </Button>
              {nextHref && (
                <Link
                  href={nextHref}
                  className={buttonClasses({ variant: "ghost", full: true, className: "mt-2" })}
                >
                  Skip to next lesson
                </Link>
              )}
            </>
          )}
        </div>

        {lesson.prev && (
          <Link
            href={`/portal/courses/${lesson.course_id}/lessons/${lesson.prev.id}`}
            className="mt-6 inline-flex min-h-12 items-center gap-2 text-body font-bold text-muted hover:text-blue-ink"
          >
            <Icon name="arrow-left" size={20} />
            Back to: {lesson.prev.title}
          </Link>
        )}
      </article>

      <aside className="lg:sticky lg:top-24 lg:self-start">
        <TutorCard lessonId={lesson.id} />
      </aside>
    </div>
  );
}

/** Eight gold dots flying out once; transform/opacity only. */
function Burst() {
  const dots = Array.from({ length: 8 }, (_, i) => {
    const angle = (i / 8) * Math.PI * 2;
    return {
      dx: `${Math.round(Math.cos(angle) * 44)}px`,
      dy: `${Math.round(Math.sin(angle) * 44)}px`,
    };
  });
  return (
    <span aria-hidden className="pointer-events-none absolute inset-0 motion-reduce:hidden">
      {dots.map((d, i) => (
        <span
          key={i}
          className="absolute left-1/2 top-1/2 -ml-1.5 -mt-1.5 h-3 w-3 rounded-full bg-gold motion-safe:animate-burst"
          style={{ "--dx": d.dx, "--dy": d.dy } as React.CSSProperties}
        />
      ))}
    </span>
  );
}

/** Show the lesson's media; never print the raw URL. */
function LessonMedia({ url, title }: { url: string; title: string }) {
  const yt = url.match(/(?:youtube\.com\/watch\?v=|youtu\.be\/)([\w-]{6,})/);
  if (yt) {
    return (
      <div className="mt-6 aspect-video max-w-[65ch] overflow-hidden rounded-card bg-navy">
        <iframe
          src={`https://www.youtube-nocookie.com/embed/${yt[1]}`}
          title={title}
          loading="lazy"
          allow="encrypted-media; picture-in-picture"
          allowFullScreen
          className="h-full w-full"
        />
      </div>
    );
  }
  if (/\.(mp4|webm)(\?|$)/i.test(url)) {
    return (
      <video
        src={url}
        controls
        preload="none"
        className="mt-6 aspect-video w-full max-w-[65ch] rounded-card bg-navy"
      />
    );
  }
  if (/\.(png|jpe?g|gif|webp|svg)(\?|$)/i.test(url)) {
    // eslint-disable-next-line @next/next/no-img-element
    return <img src={url} alt="" loading="lazy" className="mt-6 w-full max-w-[65ch] rounded-card" />;
  }
  return (
    <div className="mt-6">
      <ButtonLink href={url} external variant="secondary" icon="play">
        Watch the video
      </ButtonLink>
    </div>
  );
}

type MarkdownComponents = NonNullable<Parameters<typeof ReactMarkdown>[0]["components"]>;

const MARKDOWN: MarkdownComponents = {
  h1: ({ children }) => (
    <h2 className="mb-3 mt-8 font-display text-h3 font-bold first:mt-0">{children}</h2>
  ),
  h2: ({ children }) => (
    <h2 className="mb-3 mt-8 font-display text-title font-bold">{children}</h2>
  ),
  h3: ({ children }) => (
    <h3 className="mb-2 mt-6 font-display text-title font-bold">{children}</h3>
  ),
  p: ({ children }) => <p className="mb-4">{children}</p>,
  ul: ({ children }) => <ul className="mb-4 list-disc space-y-2 pl-6">{children}</ul>,
  ol: ({ children }) => <ol className="mb-4 list-decimal space-y-2 pl-6">{children}</ol>,
  code: ({ children }) => (
    <code className="rounded bg-blue-soft px-1.5 py-0.5 font-mono text-[16px]">{children}</code>
  ),
  pre: ({ children }) => (
    <pre className="mb-4 overflow-x-auto rounded-control bg-blue-soft p-4">{children}</pre>
  ),
  strong: ({ children }) => <strong className="font-extrabold">{children}</strong>,
  blockquote: ({ children }) => (
    <blockquote className="mb-4 rounded-control border-l-4 border-gold bg-gold-soft px-4 py-3">
      {children}
    </blockquote>
  ),
  a: ({ children, href }) => (
    <a
      href={href}
      className="font-bold text-blue-ink underline underline-offset-2"
      target="_blank"
      rel="noopener noreferrer"
    >
      {children}
    </a>
  ),
};


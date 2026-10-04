"use client";

import Link from "next/link";

import { ButtonLink } from "@/components/Button";
import { EmptyState } from "@/components/EmptyState";
import { Icon } from "@/components/Icon";
import { ProgressBar } from "@/components/ProgressBar";
import { SkeletonCard, SkeletonGroup } from "@/components/Skeleton";
import { ErrorCard, SignInPrompt } from "@/components/StatusViews";
import { getMeCourses } from "@/lib/api";
import { useApi } from "@/lib/useApi";

export function CoursesList() {
  const { state, reload } = useApi(getMeCourses, []);

  if (state.kind === "loading") {
    return (
      <SkeletonGroup label="Getting your courses">
        <div className="grid gap-4 sm:grid-cols-2">
          <SkeletonCard />
          <SkeletonCard />
        </div>
      </SkeletonGroup>
    );
  }
  if (state.kind === "signed-out" || state.kind === "forbidden") {
    return <SignInPrompt next="/portal/courses" />;
  }
  if (state.kind === "error") {
    return <ErrorCard message={state.message} onRetry={reload} />;
  }

  const courses = state.data;
  if (courses.length === 0) {
    return (
      <EmptyState
        icon="book"
        title="No courses yet"
        actions={
          <ButtonLink href="/programmes" variant="secondary">
            See programmes
          </ButtonLink>
        }
      >
        When you join a course, it will show up here.
      </EmptyState>
    );
  }

  return (
    <ul className="grid gap-4 sm:grid-cols-2">
      {courses.map((c) => (
        <li key={c.id}>
          <Link
            href={`/portal/courses/${c.id}`}
            className="group flex h-full flex-col rounded-card border border-line bg-card p-5 shadow-s transition-[transform,border-color] duration-150 ease-out hover:border-blue motion-safe:active:scale-[.98]"
          >
            <span className="text-caption font-semibold text-muted">
              {c.type === "online" ? "Online" : "On campus"}
              {c.level ? `, ${c.level}` : ""}
            </span>
            <span className="font-display text-title font-bold text-ink">
              {c.title}
            </span>
            {c.summary && (
              <span className="mt-1 flex-1 text-body text-muted">{c.summary}</span>
            )}
            <ProgressBar className="mt-4" value={c.progress_percent} />
            <span className="mt-2 inline-flex items-center gap-1 text-body font-extrabold text-blue-ink">
              Open
              <Icon
                name="arrow-right"
                size={20}
                className="transition-transform duration-200 group-hover:translate-x-0.5"
              />
            </span>
          </Link>
        </li>
      ))}
    </ul>
  );
}

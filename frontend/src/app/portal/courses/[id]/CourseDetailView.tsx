"use client";

import Link from "next/link";

import { ButtonLink } from "@/components/Button";
import { EmptyState } from "@/components/EmptyState";
import { Icon } from "@/components/Icon";
import { ProgressBar } from "@/components/ProgressBar";
import { Skeleton, SkeletonGroup } from "@/components/Skeleton";
import { ErrorCard, SignInPrompt } from "@/components/StatusViews";
import { getCourse, type CourseDetail, type LessonRead } from "@/lib/api";
import { useApi } from "@/lib/useApi";

/** Lessons in the order the learner sees them. */
function orderedLessons(course: CourseDetail): LessonRead[] {
  return [...course.modules]
    .sort((a, b) => a.sort_order - b.sort_order)
    .flatMap((m) => [...m.lessons].sort((a, b) => a.sort_order - b.sort_order));
}

export function CourseDetailView({ courseId }: { courseId: string }) {
  const { state, reload } = useApi(() => getCourse(courseId), [courseId]);

  if (state.kind === "loading") {
    return (
      <SkeletonGroup label="Opening your course">
        <Skeleton className="mb-3 h-10 w-2/3" />
        <Skeleton className="mb-6 h-3 w-full max-w-[420px] rounded-full" />
        <Skeleton className="mb-8 h-14 w-full sm:w-56" />
        <div className="space-y-2">
          {Array.from({ length: 5 }, (_, i) => (
            <Skeleton key={i} className="h-14 w-full" />
          ))}
        </div>
      </SkeletonGroup>
    );
  }
  if (state.kind === "signed-out") {
    return <SignInPrompt next={`/portal/courses/${courseId}`} />;
  }
  if (state.kind === "forbidden") {
    return (
      <EmptyState
        icon="lock"
        title="You have not joined this course yet"
        actions={
          <ButtonLink href="/programmes" variant="secondary">
            See programmes
          </ButtonLink>
        }
      >
        Join the course to open its lessons.
      </EmptyState>
    );
  }
  if (state.kind === "error") {
    return <ErrorCard message={state.message} onRetry={reload} />;
  }

  const course = state.data;
  const lessons = orderedLessons(course);
  const done = lessons.filter((l) => l.completed).length;
  const next = lessons.find((l) => !l.completed);
  const lessonHref = (id: string) => `/portal/courses/${course.id}/lessons/${id}`;

  return (
    <>
      <header className="mb-8">
        <p className="text-caption font-semibold text-muted">
          {course.type === "online" ? "Online" : "On campus"}
          {course.level ? `, ${course.level}` : ""}
        </p>
        <h1 className="mt-1 font-display text-[32px] font-bold text-ink sm:text-h2">
          {course.title}
        </h1>
        {course.summary && (
          <p className="mt-2 max-w-[60ch] text-body text-muted">{course.summary}</p>
        )}
        <ProgressBar
          className="mt-5 max-w-[420px]"
          value={course.progress_percent}
          label={`${done} of ${lessons.length} lessons done`}
        />
        <div className="mt-6">
          {next ? (
            <ButtonLink href={lessonHref(next.id)} size="lg" icon="play">
              Continue
            </ButtonLink>
          ) : lessons.length > 0 ? (
            <p className="inline-flex items-center gap-2 rounded-full bg-gold-soft px-4 py-2 text-body font-extrabold text-gold-text">
              <Icon name="star" size={20} />
              Course complete. Well done!
            </p>
          ) : null}
        </div>
      </header>

      {lessons.length === 0 ? (
        <EmptyState icon="book" title="Lessons are on the way">
          Your teacher is still adding lessons. Check back soon.
        </EmptyState>
      ) : (
        <div className="space-y-8">
          {[...course.modules]
            .sort((a, b) => a.sort_order - b.sort_order)
            .map((module) => (
              <section key={module.id} aria-labelledby={`m-${module.id}`}>
                <h2
                  id={`m-${module.id}`}
                  className="mb-3 font-display text-title font-bold text-ink"
                >
                  {module.title}
                </h2>
                <ul className="overflow-hidden rounded-card border border-line bg-card shadow-s">
                  {[...module.lessons]
                    .sort((a, b) => a.sort_order - b.sort_order)
                    .map((lesson) => {
                      const isNext = next?.id === lesson.id;
                      return (
                        <li key={lesson.id} className="border-b border-line last:border-b-0">
                          <Link
                            href={lessonHref(lesson.id)}
                            className={[
                              "flex min-h-14 items-center gap-3 px-4 py-2 transition-colors duration-200 hover:bg-blue-soft",
                              isNext ? "bg-blue-soft" : "",
                            ].join(" ")}
                          >
                            <span
                              className={[
                                "grid h-8 w-8 shrink-0 place-items-center rounded-full text-caption font-extrabold",
                                lesson.completed
                                  ? "bg-success text-white"
                                  : isNext
                                    ? "bg-blue text-white"
                                    : "border-2 border-line text-muted",
                              ].join(" ")}
                            >
                              {lesson.completed ? (
                                <Icon name="check" size={18} strokeWidth={3} title="Done" />
                              ) : isNext ? (
                                <Icon name="play" size={16} title="Up next" />
                              ) : (
                                lesson.sort_order
                              )}
                            </span>
                            <span className="flex-1 text-body font-semibold text-ink">
                              {lesson.title}
                            </span>
                            <span className="text-caption text-muted">
                              {lesson.duration_min} min
                            </span>
                          </Link>
                        </li>
                      );
                    })}
                </ul>
              </section>
            ))}
        </div>
      )}
    </>
  );
}

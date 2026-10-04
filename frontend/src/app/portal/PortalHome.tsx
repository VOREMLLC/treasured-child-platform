"use client";

import Link from "next/link";

import { ButtonLink } from "@/components/Button";
import { Icon, type IconName } from "@/components/Icon";
import { ProgressBar } from "@/components/ProgressBar";
import { Skeleton, SkeletonCard, SkeletonGroup } from "@/components/Skeleton";
import { ErrorCard, SignInPrompt } from "@/components/StatusViews";
import {
  getMe,
  getMeDashboard,
  type DashboardCourse,
  type DashboardResponse,
  type UserResponse,
} from "@/lib/api";
import { firstName, useApi } from "@/lib/useApi";

interface PortalData {
  user: UserResponse;
  /** Null if the dashboard could not be loaded; the page still works. */
  dash: DashboardResponse | null;
}

async function loadPortal(): Promise<PortalData> {
  const user = await getMe();
  const dash = await getMeDashboard().catch(() => null);
  return { user, dash };
}

export function PortalHome() {
  const { state, reload } = useApi(loadPortal, []);

  if (state.kind === "loading") {
    return (
      <SkeletonGroup label="Getting your page ready">
        <Skeleton className="mb-3 h-11 w-56" />
        <Skeleton className="mb-8 h-5 w-72" />
        <SkeletonCard className="mb-6" />
        <div className="grid gap-4 sm:grid-cols-2">
          <SkeletonCard />
          <SkeletonCard />
        </div>
      </SkeletonGroup>
    );
  }
  if (state.kind === "signed-out" || state.kind === "forbidden") {
    return <SignInPrompt next="/portal" />;
  }
  if (state.kind === "error") {
    return <ErrorCard message={state.message} onRetry={reload} />;
  }

  const { user, dash } = state.data;
  const courses = dash?.courses ?? [];
  const isLearner = courses.length > 0;

  return (
    <div className="motion-safe:animate-rise">
      <h1 className="font-display text-[36px] font-bold text-ink sm:text-h1">
        Hi {firstName(user.name)}!
      </h1>
      <p className="mt-1 text-label text-muted">
        {isLearner ? "Ready to learn something new?" : "What would you like to do today?"}
      </p>

      {isLearner && dash ? (
        <LearnerView dash={dash} courses={courses} />
      ) : (
        <ActionsView />
      )}
    </div>
  );
}

function LearnerView({
  dash,
  courses,
}: {
  dash: DashboardResponse;
  courses: DashboardCourse[];
}) {
  const next = dash.continue_learning;
  return (
    <>
      {next ? (
        <Link
          href={`/portal/courses/${next.course_id}/lessons/${next.lesson_id}`}
          className="group mt-6 flex items-center gap-4 rounded-card bg-blue p-5 text-white shadow transition-transform duration-150 ease-out motion-safe:active:scale-[.98] sm:p-6"
        >
          <span className="grid h-16 w-16 shrink-0 place-items-center rounded-full bg-white text-blue">
            <Icon name="play" size={30} />
          </span>
          <span className="flex-1">
            <span className="block text-caption font-semibold opacity-90">
              {next.course_title}
            </span>
            <span className="block font-display text-title font-bold leading-tight">
              {next.lesson_title}
            </span>
            <span className="mt-1 inline-flex items-center gap-1 text-body font-extrabold">
              Continue
              <Icon name="arrow-right" size={20} className="transition-transform duration-200 group-hover:translate-x-0.5" />
            </span>
          </span>
        </Link>
      ) : (
        <div className="mt-6 flex items-center gap-4 rounded-card bg-gold-soft p-5 sm:p-6">
          <span className="grid h-16 w-16 shrink-0 place-items-center rounded-full bg-gold text-ink">
            <Icon name="star" size={30} />
          </span>
          <p className="font-display text-title font-bold text-ink">
            You finished every lesson. Well done!
          </p>
        </div>
      )}

      <StatsStrip dash={dash} />

      <h2 className="mb-3 mt-10 font-display text-title font-bold text-ink">
        My courses
      </h2>
      <ul className="grid gap-4 sm:grid-cols-2">
        {courses.map((c) => (
          <li key={c.id}>
            <Link
              href={`/portal/courses/${c.id}`}
              className="block rounded-card border border-line bg-card p-5 shadow-s transition-[transform,border-color] duration-150 ease-out hover:border-blue motion-safe:active:scale-[.98]"
            >
              <span className="text-caption font-semibold text-muted">
                {c.type === "online" ? "Online" : "On campus"}
                {c.level ? `, ${c.level}` : ""}
              </span>
              <span className="mb-3 block font-display text-title font-bold text-ink">
                {c.title}
              </span>
              <ProgressBar value={c.progress_percent} />
            </Link>
          </li>
        ))}
      </ul>
    </>
  );
}

function StatsStrip({ dash }: { dash: DashboardResponse }) {
  const items: { icon: IconName; text: string }[] = [
    { icon: "star", text: `Level ${dash.level}` },
    { icon: "sparkle", text: `${dash.xp.toLocaleString("en-NG")} points` },
  ];
  if (dash.streak_days > 0) {
    items.push({
      icon: "check",
      text: `${dash.streak_days} ${dash.streak_days === 1 ? "day" : "days"} in a row`,
    });
  }
  return (
    <ul className="mt-4 flex flex-wrap gap-2" aria-label="Your rewards">
      {items.map((i) => (
        <li
          key={i.text}
          className="inline-flex min-h-10 items-center gap-2 rounded-full bg-gold-soft px-4 text-body font-extrabold text-gold-text"
        >
          <Icon name={i.icon} size={20} />
          {i.text}
        </li>
      ))}
    </ul>
  );
}

function ActionsView() {
  return (
    <div className="mt-6 grid gap-4 sm:grid-cols-2">
      <ActionTile
        href="/pay"
        icon="card"
        title="Pay fees"
        body="School fees or an online course, paid safely with Paystack."
      />
      <ActionTile
        href="/apply"
        icon="school"
        title="Apply now"
        body="Ask for a place for your child. We reply within 48 hours."
      />
      <div className="sm:col-span-2">
        <ButtonLink href="/programmes" variant="ghost" iconRight="arrow-right">
          See our programmes
        </ButtonLink>
      </div>
    </div>
  );
}

function ActionTile({
  href,
  icon,
  title,
  body,
}: {
  href: string;
  icon: IconName;
  title: string;
  body: string;
}) {
  return (
    <Link
      href={href}
      className="group flex items-start gap-4 rounded-card border border-line bg-card p-5 shadow-s transition-[transform,border-color] duration-150 ease-out hover:border-blue motion-safe:active:scale-[.98]"
    >
      <span className="grid h-14 w-14 shrink-0 place-items-center rounded-control bg-blue text-white">
        <Icon name={icon} size={28} />
      </span>
      <span>
        <span className="flex items-center gap-1 font-display text-title font-bold text-ink">
          {title}
          <Icon name="arrow-right" size={20} className="text-blue-ink" />
        </span>
        <span className="block text-body text-muted">{body}</span>
      </span>
    </Link>
  );
}

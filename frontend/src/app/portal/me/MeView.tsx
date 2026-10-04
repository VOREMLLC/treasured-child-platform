"use client";

import { ButtonLink } from "@/components/Button";
import { Icon } from "@/components/Icon";
import { Skeleton, SkeletonGroup } from "@/components/Skeleton";
import { ErrorCard, SignInPrompt } from "@/components/StatusViews";
import { getMe } from "@/lib/api";
import { useApi } from "@/lib/useApi";
import { SignOutButton } from "../SignOutButton";

export function MeView() {
  const { state, reload } = useApi(getMe, []);

  if (state.kind === "loading") {
    return (
      <SkeletonGroup label="Getting your details">
        <Skeleton className="mb-6 h-24 w-full rounded-card" />
        <Skeleton className="h-12 w-full" />
      </SkeletonGroup>
    );
  }
  if (state.kind === "signed-out" || state.kind === "forbidden") {
    return <SignInPrompt next="/portal/me" />;
  }
  if (state.kind === "error") {
    return <ErrorCard message={state.message} onRetry={reload} />;
  }

  const user = state.data;
  return (
    <div className="space-y-6">
      <section className="flex items-center gap-4 rounded-card border border-line bg-card p-5 shadow-s">
        <span className="grid h-16 w-16 shrink-0 place-items-center rounded-full bg-blue-soft text-blue-ink">
          <Icon name="user" size={32} />
        </span>
        <div className="min-w-0">
          <h1 className="font-display text-h3 font-bold text-ink">{user.name}</h1>
          <p className="truncate text-body text-muted">{user.email}</p>
          {user.phone && <p className="text-body text-muted">{user.phone}</p>}
        </div>
      </section>

      <div className="grid gap-3 sm:grid-cols-2">
        <ButtonLink href="/pay" icon="card" full>
          Pay fees
        </ButtonLink>
        <SignOutButton />
      </div>
    </div>
  );
}

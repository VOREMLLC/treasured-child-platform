import { ButtonLink, Button } from "./Button";
import { EmptyState } from "./EmptyState";

/** "Please sign in" card, used wherever a signed-out visitor lands. */
export function SignInPrompt({
  next,
  title = "Please sign in",
  children = "Sign in to see your lessons or pay fees.",
}: {
  next: string;
  title?: string;
  children?: React.ReactNode;
}) {
  return (
    <EmptyState
      icon="lock"
      title={title}
      actions={
        <>
          <ButtonLink href={`/login?next=${encodeURIComponent(next)}`}>
            Sign in
          </ButtonLink>
          <ButtonLink href="/register" variant="ghost">
            New here? Create an account
          </ButtonLink>
        </>
      }
    >
      {children}
    </EmptyState>
  );
}

export function ErrorCard({
  message,
  onRetry,
}: {
  message: string;
  onRetry?: () => void;
}) {
  return (
    <EmptyState
      icon="alert"
      tone="danger"
      role="alert"
      title="That did not work"
      actions={
        onRetry ? (
          <Button onClick={onRetry} variant="secondary">
            Try again
          </Button>
        ) : undefined
      }
    >
      {message}
    </EmptyState>
  );
}

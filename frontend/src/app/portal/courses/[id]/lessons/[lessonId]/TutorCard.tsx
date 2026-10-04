"use client";

import { useState, type FormEvent } from "react";

import { Button } from "@/components/Button";
import { controlClass } from "@/components/Field";
import { Icon } from "@/components/Icon";
import { ApiError, postTutorAsk } from "@/lib/api";

interface Turn {
  question: string;
  reply: string;
}

/**
 * "Ask a question" card. The helper only answers about this lesson;
 * safety checks run on the server before and after every reply.
 */
export function TutorCard({ lessonId }: { lessonId: string }) {
  const [question, setQuestion] = useState("");
  const [asking, setAsking] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [turns, setTurns] = useState<Turn[]>([]);

  async function onAsk(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const q = question.trim();
    if (!q) return;
    setAsking(true);
    setError(null);
    try {
      const res = await postTutorAsk({ lesson_id: lessonId, question: q });
      setTurns((t) => [...t, { question: q, reply: res.reply }]);
      setQuestion("");
    } catch (err) {
      if (err instanceof ApiError && err.status === 503) {
        setError("The helper is resting right now. Please try again soon.");
      } else if (err instanceof ApiError && err.status === 429) {
        setError("Lots of questions! Wait a minute, then ask again.");
      } else {
        setError("That question did not send. Please try again.");
      }
    } finally {
      setAsking(false);
    }
  }

  return (
    <section
      aria-labelledby="tutor-title"
      className="rounded-card border border-line bg-card p-5 shadow-s"
    >
      <div className="mb-3 flex items-center gap-3">
        <span className="grid h-12 w-12 place-items-center rounded-full bg-gold-soft text-gold-text">
          <Icon name="sparkle" />
        </span>
        <h2 id="tutor-title" className="font-display text-title font-bold text-ink">
          Ask a question
        </h2>
      </div>
      <p className="text-body text-muted">
        Stuck on something? Ask about this lesson and get a simple answer.
      </p>

      {turns.length > 0 && (
        <ol className="mt-4 space-y-3" aria-live="polite">
          {turns.map((t, i) => (
            <li key={i} className="space-y-2">
              <p className="ml-6 rounded-control bg-blue-soft px-3 py-2 text-body text-ink">
                {t.question}
              </p>
              <p className="mr-6 whitespace-pre-line rounded-control bg-gold-soft px-3 py-2 text-body text-ink">
                {t.reply}
              </p>
            </li>
          ))}
        </ol>
      )}

      <form onSubmit={onAsk} className="mt-4 space-y-3">
        <label htmlFor="tutor-q" className="sr-only">
          Your question
        </label>
        <textarea
          id="tutor-q"
          rows={3}
          maxLength={2000}
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="Type your question here"
          className={`${controlClass(false)} resize-none`}
        />
        {error && (
          <p role="alert" className="flex items-start gap-2 text-body text-danger">
            <Icon name="alert" size={20} className="mt-0.5" />
            {error}
          </p>
        )}
        <Button type="submit" variant="secondary" full loading={asking} disabled={!question.trim()}>
          Ask
        </Button>
      </form>
    </section>
  );
}

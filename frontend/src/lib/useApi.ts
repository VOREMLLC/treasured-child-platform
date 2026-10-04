"use client";

import { useCallback, useEffect, useState } from "react";

import { ApiError } from "./api";

export type ApiState<T> =
  | { kind: "loading" }
  | { kind: "signed-out" }
  | { kind: "forbidden" }
  | { kind: "error"; message: string }
  | { kind: "ready"; data: T };

/**
 * Run an API read on mount and map the outcome to a small set of
 * screen states, so every page handles "not signed in" the same way.
 */
export function useApi<T>(
  load: () => Promise<T>,
  deps: ReadonlyArray<unknown>,
): { state: ApiState<T>; setData: (data: T) => void; reload: () => void } {
  const [state, setState] = useState<ApiState<T>>({ kind: "loading" });
  const [tick, setTick] = useState(0);

  useEffect(() => {
    let cancelled = false;
    setState({ kind: "loading" });
    load()
      .then((data) => {
        if (!cancelled) setState({ kind: "ready", data });
      })
      .catch((err: unknown) => {
        if (cancelled) return;
        if (err instanceof ApiError && err.status === 401) {
          setState({ kind: "signed-out" });
        } else if (err instanceof ApiError && (err.status === 403 || err.status === 404)) {
          setState({ kind: "forbidden" });
        } else if (err instanceof ApiError) {
          setState({ kind: "error", message: err.message });
        } else {
          setState({
            kind: "error",
            message: "Something went wrong. Please try again.",
          });
        }
      });
    return () => {
      cancelled = true;
    };
    // `load` is recreated each render, so callers list its real inputs
    // in `deps` instead.
  }, [...deps, tick]);

  const setData = useCallback((data: T) => setState({ kind: "ready", data }), []);
  const reload = useCallback(() => setTick((t) => t + 1), []);

  return { state, setData, reload };
}

/** First word of a name, for friendly greetings. */
export function firstName(name: string): string {
  return name.trim().split(/\s+/)[0] || "there";
}

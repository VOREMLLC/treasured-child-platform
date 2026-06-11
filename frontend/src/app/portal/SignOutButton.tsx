"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";

import { postLogout } from "@/lib/api";

export function SignOutButton() {
  const router = useRouter();
  const [signingOut, setSigningOut] = useState(false);

  async function onClick() {
    setSigningOut(true);
    try {
      await postLogout();
    } catch {
      // Logout is a best-effort clear; even if the request fails the
      // server-side cookies are still cleared on the next response, and
      // the user expects to be signed out either way.
    }
    router.push("/");
    router.refresh();
  }

  return (
    <button
      type="button"
      onClick={onClick}
      disabled={signingOut}
      className="inline-flex items-center px-5 py-3 rounded-pill bg-gradient-to-b from-blue to-blue-deep text-white font-semibold shadow-[0_10px_24px_-10px_rgba(31,99,201,0.55)] hover:from-blue-bright transition disabled:opacity-60 disabled:cursor-not-allowed"
    >
      {signingOut ? "Signing out…" : "Sign out"}
    </button>
  );
}

"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";

import { Button } from "@/components/Button";
import { postLogout } from "@/lib/api";

export function SignOutButton() {
  const router = useRouter();
  const [signingOut, setSigningOut] = useState(false);

  async function onClick() {
    setSigningOut(true);
    try {
      await postLogout();
    } catch {
      // Best effort: the user expects to be signed out either way, and the
      // server clears the session cookies on its next response.
    }
    router.push("/");
    router.refresh();
  }

  return (
    <Button variant="secondary" onClick={onClick} loading={signingOut} full>
      Sign out
    </Button>
  );
}

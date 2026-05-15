"use client";

import { SignInButton, UserButton } from "@clerk/nextjs";

import { Button } from "@/components/ui/button";

type AuthControlsProps = {
  signedIn: boolean;
};

export function AuthControls({ signedIn }: AuthControlsProps) {
  if (signedIn) {
    return <UserButton />;
  }

  return (
    <SignInButton mode="modal">
      <Button>Sign in</Button>
    </SignInButton>
  );
}

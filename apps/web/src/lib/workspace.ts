import "server-only";

import { auth, currentUser } from "@clerk/nextjs/server";

import { internalApiFetch } from "@/lib/api-client";

export type SyncedUserWorkspace = {
  user_id: string;
  clerk_id: string;
  organization_id: string;
  current_project_id: string;
  created: boolean;
};

export class WorkspaceAuthError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "WorkspaceAuthError";
  }
}

export async function getCurrentWorkspace(): Promise<SyncedUserWorkspace> {
  const { userId } = await auth();

  if (!userId) {
    throw new WorkspaceAuthError("Sign in to access your workspace.");
  }

  const user = await currentUser();
  const email = user?.primaryEmailAddress?.emailAddress;

  if (!email) {
    throw new WorkspaceAuthError("Your Clerk session does not have a primary email address.");
  }

  return internalApiFetch<SyncedUserWorkspace>("/v1/internal/sync-user", {
    method: "POST",
    body: JSON.stringify({
      clerk_id: userId,
      email,
      name: user.fullName ?? user.username ?? email.split("@", 1)[0],
    }),
  });
}

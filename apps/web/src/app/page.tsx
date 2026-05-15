import { auth } from "@clerk/nextjs/server";
import { ShieldCheck } from "lucide-react";

import { ApiKeysCard } from "@/components/api-keys-card";
import { AuthControls } from "@/components/auth-controls";
import { UsageCard } from "@/components/usage-card";
import {
  Card,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

export default async function Home() {
  const { userId } = await auth();
  const signedIn = Boolean(userId);

  return (
    <main className="min-h-screen bg-muted/30 px-6 py-8">
      <div className="mx-auto flex max-w-5xl flex-col gap-8">
        <header className="flex items-center justify-between gap-4">
          <div>
            <div className="mb-3 inline-flex items-center gap-2 rounded-full border bg-background px-3 py-1 text-sm text-muted-foreground">
              <ShieldCheck className="size-4" /> Gatekeeper dashboard
            </div>
            <h1 className="text-3xl font-semibold tracking-tight">
              Docu Meter Admin
            </h1>
            <p className="mt-2 max-w-2xl text-muted-foreground">
              Server-rendered dashboard shell. Clerk login provisions a default
              org and project automatically.
            </p>
          </div>
          <AuthControls signedIn={signedIn} />
        </header>

        {!signedIn ? (
          <Card>
            <CardHeader>
              <CardTitle>Session required</CardTitle>
              <CardDescription>
                Sign in with Clerk to auto-create your workspace and view usage.
              </CardDescription>
            </CardHeader>
          </Card>
        ) : (
          <>
            <UsageCard />
            <ApiKeysCard />
          </>
        )}
      </div>
    </main>
  );
}

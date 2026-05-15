"use client";

import { useActionState } from "react";
import { Plus } from "lucide-react";

import { createApiKey, type CreateApiKeyState } from "@/app/actions/api-keys";
import { CopySecret } from "@/components/copy-secret";
import { Button } from "@/components/ui/button";

const initialState: CreateApiKeyState = {
  ok: false,
  message: "",
};

export function CreateApiKeyForm() {
  const [state, formAction, pending] = useActionState(createApiKey, initialState);

  return (
    <div className="space-y-4">
      <form action={formAction} className="flex flex-col gap-3 sm:flex-row">
        <input
          name="name"
          placeholder="Production token"
          className="h-10 flex-1 rounded-md border bg-background px-3 text-sm outline-none ring-offset-background placeholder:text-muted-foreground focus-visible:ring-2 focus-visible:ring-ring"
        />
        <Button type="submit" disabled={pending}>
          <Plus className="size-4" /> {pending ? "Creating..." : "Create key"}
        </Button>
      </form>

      {state.message ? (
        <p className={state.ok ? "text-sm text-emerald-700" : "text-sm text-destructive"}>
          {state.message}
        </p>
      ) : null}

      {state.key ? <CopySecret value={state.key} /> : null}
    </div>
  );
}

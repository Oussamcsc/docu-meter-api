"use client";

import { useState } from "react";
import { Copy } from "lucide-react";

import { Button } from "@/components/ui/button";

type CopySecretProps = {
  value: string;
};

export function CopySecret({ value }: CopySecretProps) {
  const [copied, setCopied] = useState(false);

  async function copy() {
    await navigator.clipboard.writeText(value);
    setCopied(true);
    window.setTimeout(() => setCopied(false), 2000);
  }

  return (
    <div className="rounded-lg border border-amber-300 bg-amber-50 p-4 text-amber-950">
      <p className="font-medium">Copy this token now.</p>
      <p className="mt-1 text-sm">
        This raw secret is shown once. After you leave this state, only the masked token is available.
      </p>
      <div className="mt-3 flex flex-col gap-3 sm:flex-row">
        <code className="min-w-0 flex-1 overflow-x-auto rounded bg-white px-3 py-2 text-sm">
          {value}
        </code>
        <Button type="button" onClick={copy} variant="outline">
          <Copy className="size-4" /> {copied ? "Copied" : "Copy"}
        </Button>
      </div>
    </div>
  );
}

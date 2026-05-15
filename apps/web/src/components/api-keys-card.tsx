import { KeyRound, Trash2 } from "lucide-react";

import { listApiKeys, revokeApiKey } from "@/app/actions/api-keys";
import { CreateApiKeyForm } from "@/components/create-api-key-form";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

export async function ApiKeysCard() {
  const result = await listApiKeys();

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center gap-2">
          <KeyRound className="size-5" />
          <CardTitle>API Keys</CardTitle>
        </div>
        <CardDescription>
          Generate project-scoped bearer tokens for ingestion. Raw tokens are shown once.
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        <CreateApiKeyForm />

        {!result.ok ? (
          <p className="text-sm text-destructive">{result.message}</p>
        ) : result.keys.length === 0 ? (
          <div className="rounded-lg border border-dashed p-6 text-sm text-muted-foreground">
            No API keys yet. Create one to start sending usage events.
          </div>
        ) : (
          <div className="overflow-hidden rounded-lg border">
            <table className="w-full text-sm">
              <thead className="bg-muted/60 text-left">
                <tr>
                  <th className="px-4 py-3 font-medium">Name</th>
                  <th className="px-4 py-3 font-medium">Token</th>
                  <th className="px-4 py-3 font-medium">Status</th>
                  <th className="px-4 py-3 text-right font-medium">Action</th>
                </tr>
              </thead>
              <tbody>
                {result.keys.map((apiKey) => (
                  <tr key={apiKey.id} className="border-t">
                    <td className="px-4 py-3">{apiKey.name}</td>
                    <td className="px-4 py-3 font-mono text-xs">{apiKey.masked_token}</td>
                    <td className="px-4 py-3">
                      <Badge variant={apiKey.is_active ? "default" : "secondary"}>
                        {apiKey.is_active ? "Active" : "Revoked"}
                      </Badge>
                    </td>
                    <td className="px-4 py-3 text-right">
                      <form action={revokeApiKey}>
                        <input type="hidden" name="apiKeyId" value={apiKey.id} />
                        <Button
                          type="submit"
                          size="sm"
                          variant="outline"
                          disabled={!apiKey.is_active}
                        >
                          <Trash2 className="size-4" /> Revoke
                        </Button>
                      </form>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

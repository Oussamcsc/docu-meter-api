"use server";

import { revalidatePath } from "next/cache";

import { InternalApiError, internalApiFetch } from "@/lib/api-client";
import { getCurrentWorkspace, WorkspaceAuthError } from "@/lib/workspace";

export type DashboardApiKey = {
  id: string;
  project_id: string;
  name: string;
  key_prefix: string;
  masked_token: string;
  is_active: boolean;
};

export type ApiKeyListResult =
  | { ok: true; keys: DashboardApiKey[] }
  | { ok: false; message: string };

export type CreateApiKeyState = {
  ok: boolean;
  message: string;
  key?: string;
};

function actionErrorMessage(error: unknown): string {
  if (error instanceof WorkspaceAuthError || error instanceof InternalApiError) {
    return error.message;
  }
  return "Unexpected API key action failure.";
}

export async function listApiKeys(): Promise<ApiKeyListResult> {
  try {
    const workspace = await getCurrentWorkspace();
    const query = new URLSearchParams({ project_id: workspace.current_project_id });
    const response = await internalApiFetch<{ keys: DashboardApiKey[] }>(`/v1/keys?${query}`);
    return { ok: true, keys: response.keys };
  } catch (error) {
    return { ok: false, message: actionErrorMessage(error) };
  }
}

export async function createApiKey(
  _previousState: CreateApiKeyState,
  formData: FormData,
): Promise<CreateApiKeyState> {
  const name = String(formData.get("name") ?? "").trim() || "Default API key";

  try {
    const workspace = await getCurrentWorkspace();
    const created = await internalApiFetch<{ key: string }>(
      `/v1/projects/${workspace.current_project_id}/keys`,
      {
        method: "POST",
        body: JSON.stringify({ name }),
      },
    );
    revalidatePath("/");
    return {
      ok: true,
      message: "API key created. Copy it now — it will not be shown again.",
      key: created.key,
    };
  } catch (error) {
    return { ok: false, message: actionErrorMessage(error) };
  }
}

export async function revokeApiKey(formData: FormData): Promise<void> {
  const apiKeyId = String(formData.get("apiKeyId") ?? "");
  if (!apiKeyId) {
    return;
  }

  const workspace = await getCurrentWorkspace();
  await internalApiFetch(`/v1/projects/${workspace.current_project_id}/keys/${apiKeyId}`, {
    method: "DELETE",
  });
  revalidatePath("/");
}

"use server";

import { InternalApiError, internalApiFetch } from "@/lib/api-client";
import { getCurrentWorkspace, WorkspaceAuthError } from "@/lib/workspace";

export type ProjectTelemetry = {
  project_id: string;
  usage_count: number;
  monthly_quota: number;
  percentage: number;
  reset_date: string;
};

export type ProjectTelemetryResult =
  | { ok: true; data: ProjectTelemetry }
  | { ok: false; status: 401 | 404 | 503 | 500; message: string };

export async function getProjectTelemetry(): Promise<ProjectTelemetryResult> {
  try {
    const workspace = await getCurrentWorkspace();
    const query = new URLSearchParams({
      project_id: workspace.current_project_id,
    });
    const data = await internalApiFetch<ProjectTelemetry>(`/v1/usage?${query}`);
    return { ok: true, data };
  } catch (error) {
    if (error instanceof WorkspaceAuthError) {
      return {
        ok: false,
        status: 401,
        message: error.message,
      };
    }

    if (error instanceof InternalApiError) {
      if (error.status === 404) {
        return {
          ok: false,
          status: 404,
          message: "Project telemetry was not found for this user workspace.",
        };
      }

      if (error.status === 503) {
        return {
          ok: false,
          status: 503,
          message: "Internal admin telemetry is not configured yet.",
        };
      }

      return {
        ok: false,
        status: 500,
        message: error.message,
      };
    }

    return {
      ok: false,
      status: 500,
      message: "Unexpected telemetry fetch failure.",
    };
  }
}

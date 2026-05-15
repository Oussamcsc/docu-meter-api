import "server-only";

type InternalRequestOptions = Omit<RequestInit, "headers"> & {
  headers?: HeadersInit;
};

export class InternalApiError extends Error {
  constructor(
    message: string,
    readonly status: number,
    readonly payload: unknown = null,
  ) {
    super(message);
    this.name = "InternalApiError";
  }
}

function getRequiredServerEnv(name: string): string {
  const value = process.env[name];
  if (!value) {
    throw new InternalApiError(`${name} is not configured`, 503);
  }
  return value;
}

function buildApiUrl(path: string): string {
  const baseUrl = getRequiredServerEnv("DOCU_METER_API_URL").replace(/\/$/, "");
  const normalizedPath = path.startsWith("/") ? path : `/${path}`;
  return `${baseUrl}${normalizedPath}`;
}

export async function internalApiFetch<T>(
  path: string,
  options: InternalRequestOptions = {},
): Promise<T> {
  const adminToken = getRequiredServerEnv("ADMIN_API_TOKEN");
  const headers = new Headers(options.headers);
  headers.set("X-Admin-Token", adminToken);
  headers.set("Accept", "application/json");

  if (options.body && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }

  const response = await fetch(buildApiUrl(path), {
    ...options,
    headers,
    cache: "no-store",
  });

  const contentType = response.headers.get("content-type") ?? "";
  const payload = contentType.includes("application/json")
    ? await response.json()
    : await response.text();

  if (!response.ok) {
    const detail =
      typeof payload === "object" && payload !== null && "detail" in payload
        ? String(payload.detail)
        : `Internal API request failed with ${response.status}`;
    throw new InternalApiError(detail, response.status, payload);
  }

  return payload as T;
}

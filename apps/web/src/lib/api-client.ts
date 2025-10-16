import { buildApiUrl } from "@/lib/utils";

export interface ApiRequestOptions extends RequestInit {
  accessToken?: string | null;
  skipAuth?: boolean;
}

export async function apiFetch<T>(path: string, options: ApiRequestOptions = {}): Promise<T> {
  const { accessToken, skipAuth, headers, body, ...rest } = options;
  const url = buildApiUrl(path);
  const resolvedHeaders = new Headers(headers ?? {});
  if (!skipAuth && accessToken) {
    resolvedHeaders.set("Authorization", `Bearer ${accessToken}`);
  }
  if (body && !(body instanceof FormData) && !resolvedHeaders.has("Content-Type")) {
    resolvedHeaders.set("Content-Type", "application/json");
  }

  const response = await fetch(url, {
    ...rest,
    headers: resolvedHeaders,
    body,
    cache: "no-store",
  });

  if (!response.ok) {
    const errorText = await safeParseError(response);
    throw new Error(errorText);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return (await response.json()) as T;
}

async function safeParseError(response: Response): Promise<string> {
  try {
    const data = await response.json();
    if (typeof data === "string") {
      return data;
    }
    if (data?.message) {
      return data.message;
    }
    return JSON.stringify(data);
  } catch {
    return `${response.status} ${response.statusText}`;
  }
}

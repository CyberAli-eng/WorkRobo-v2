/**
 * Single fetch wrapper for the Django API.
 *
 * - Attaches `Authorization: Bearer <access>` to every request.
 * - On 401, attempts one silent refresh; retries the original request
 *   with the new access token. If the refresh also fails, throws
 *   `ApiError(401)` so callers can redirect to /login.
 *
 * The refresh is single-flight — overlapping 401s share one refresh
 * promise so we don't burn the refresh token on parallel requests.
 */
import {
  clearTokens,
  getAccessToken,
  getRefreshToken,
  setAccessToken,
  setTokens,
} from "./auth";

const API_BASE = "http://localhost:8000";

export class ApiError extends Error {
  status: number;
  body: unknown;
  constructor(status: number, body: unknown, message: string) {
    super(message);
    this.status = status;
    this.body = body;
  }
}

type Method = "GET" | "POST" | "PATCH" | "PUT" | "DELETE";

let inflightRefresh: Promise<string | null> | null = null;

async function refreshAccessToken(): Promise<string | null> {
  if (inflightRefresh) return inflightRefresh;
  inflightRefresh = (async () => {
    const refresh = getRefreshToken();
    if (!refresh) return null;
    const res = await fetch(`${API_BASE}/api/auth/refresh/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ refresh }),
    });
    if (!res.ok) {
      clearTokens();
      return null;
    }
    const data = (await res.json()) as { access: string; refresh?: string };
    if (data.refresh) {
      setTokens({ access: data.access, refresh: data.refresh });
    } else {
      setAccessToken(data.access);
    }
    return data.access;
  })().finally(() => {
    inflightRefresh = null;
  });
  return inflightRefresh;
}

async function request<T>(
  method: Method,
  path: string,
  body?: unknown,
  options: { auth?: boolean } = {},
): Promise<T> {
  const { auth = true } = options;
  const headers: Record<string, string> = { "Content-Type": "application/json" };
  if (auth) {
    const token = getAccessToken();
    if (token) headers.Authorization = `Bearer ${token}`;
  }

  const res = await fetch(`${API_BASE}${path}`, {
    method,
    headers,
    body: body !== undefined ? JSON.stringify(body) : undefined,
  });

  if (res.status === 401 && auth) {
    // Try a silent refresh, then retry once.
    const newAccess = await refreshAccessToken();
    if (newAccess) {
      return request<T>(method, path, body, { auth: false });
    }
    throw new ApiError(401, null, "Unauthorized");
  }

  if (!res.ok) {
    let parsed: unknown = null;
    try {
      parsed = await res.json();
    } catch {
      /* non-JSON body */
    }
    throw new ApiError(res.status, parsed, `Request failed: ${res.status}`);
  }

  if (res.status === 204) return undefined as T;
  return (await res.json()) as T;
}

export const api = {
  get: <T>(path: string) => request<T>("GET", path),
  post: <T>(path: string, body?: unknown) => request<T>("POST", path, body),
  patch: <T>(path: string, body?: unknown) => request<T>("PATCH", path, body),
  put: <T>(path: string, body?: unknown) => request<T>("PUT", path, body),
  delete: <T>(path: string) => request<T>("DELETE", path),
};

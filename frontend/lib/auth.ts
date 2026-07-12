/**
 * Token storage helpers.
 *
 * Tokens are kept in localStorage so the dev experience is simple and
 * fetch can read them to attach Authorization headers. This is
 * fine for local development; for production you would want
 * HttpOnly cookies + a same-origin proxy.
 */
const ACCESS_KEY = "wr.access";
const REFRESH_KEY = "wr.refresh";

export type Tokens = { access: string; refresh: string };

export function setTokens(tokens: Tokens): void {
  localStorage.setItem(ACCESS_KEY, tokens.access);
  localStorage.setItem(REFRESH_KEY, tokens.refresh);
}

export function setAccessToken(access: string): void {
  localStorage.setItem(ACCESS_KEY, access);
}

export function getAccessToken(): string | null {
  return typeof window === "undefined" ? null : localStorage.getItem(ACCESS_KEY);
}

export function getRefreshToken(): string | null {
  return typeof window === "undefined" ? null : localStorage.getItem(REFRESH_KEY);
}

export function clearTokens(): void {
  localStorage.removeItem(ACCESS_KEY);
  localStorage.removeItem(REFRESH_KEY);
}

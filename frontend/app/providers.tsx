"use client";

/**
 * Auth context. Exposes { user, loading, login, signup, logout }.
 *
 * - On mount, calls /api/auth/me/. If a valid access token is in
 *   localStorage, this succeeds; if it 401s the API client will try
 *   a refresh first. If everything fails, user stays null.
 * - login() and signup() store tokens and refetch the user.
 * - logout() calls /api/auth/logout/ and clears tokens.
 */
import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useState,
  type ReactNode,
} from "react";

import { api, ApiError } from "@/lib/api";
import { clearTokens, getAccessToken, setTokens } from "@/lib/auth";

export type User = {
  id: number;
  email: string;
  name: string;
  date_joined: string;
};

type AuthContextValue = {
  user: User | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  signup: (email: string, password: string, name?: string) => Promise<void>;
  logout: () => Promise<void>;
};

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  const fetchMe = useCallback(async (): Promise<User | null> => {
    try {
      return await api.get<User>("/api/auth/me/");
    } catch (err) {
      if (err instanceof ApiError && err.status === 401) return null;
      throw err;
    }
  }, []);

  // On mount: if we have any token, try to fetch the current user.
  useEffect(() => {
    let cancelled = false;
    (async () => {
      if (!getAccessToken()) {
        if (!cancelled) setLoading(false);
        return;
      }
      try {
        const me = await fetchMe();
        if (!cancelled) setUser(me);
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [fetchMe]);

  const login = useCallback<AuthContextValue["login"]>(
    async (email, password) => {
      const data = await api.post<{
        access: string;
        refresh: string;
      }>("/api/auth/login/", { email, password });
      setTokens({ access: data.access, refresh: data.refresh });
      const me = await fetchMe();
      setUser(me);
    },
    [fetchMe],
  );

  const signup = useCallback<AuthContextValue["signup"]>(
    async (email, password, name) => {
      const data = await api.post<{
        access: string;
        refresh: string;
        user: User;
      }>("/api/auth/register/", { email, password, name });
      setTokens({ access: data.access, refresh: data.refresh });
      setUser(data.user);
    },
    [],
  );

  const logout = useCallback<AuthContextValue["logout"]>(async () => {
    try {
      await api.post("/api/auth/logout/");
    } catch {
      /* ignore — local cleanup is what matters */
    }
    clearTokens();
    setUser(null);
  }, []);

  return (
    <AuthContext.Provider value={{ user, loading, login, signup, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used inside <AuthProvider>");
  return ctx;
}

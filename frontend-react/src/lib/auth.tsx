import { createContext, useContext, useEffect, useState, type ReactNode } from "react";
import { api, type UserProfile } from "./api";
import { useUiLang } from "./uiLang";
import type { LangCode } from "./i18n";

interface AuthState {
  token: string | null;
  user: UserProfile | null;
  loading: boolean;
  /**
   * True from the moment logout() is called onward. ProtectedRoute checks
   * this to avoid firing its own redirect-to-/login: React Router can still
   * have the outgoing protected route mounted for a render or two after
   * navigate() already moved the URL elsewhere, and without this guard that
   * stale render's `!user` check races the real navigation and wins.
   */
  isLoggingOut: boolean;
  setSession: (token: string, user: UserProfile) => void;
  updateUser: (user: UserProfile) => void;
  logout: () => void;
}

const AuthContext = createContext<AuthState | null>(null);

const TOKEN_KEY = "janmitra.token";

export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setToken] = useState<string | null>(() => localStorage.getItem(TOKEN_KEY));
  const [user, setUser] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [isLoggingOut, setIsLoggingOut] = useState(false);
  // The account's saved preferred_language is the source of truth for UI language once
  // logged in — synced into uiLang below so dashboards/TopBar/complaint display all follow it
  // automatically, with no separate action needed after logging in or loading a session.
  const { setLang } = useUiLang();

  useEffect(() => {
    if (!token) {
      setLoading(false);
      return;
    }
    api
      .me(token)
      .then((profile) => {
        setUser(profile);
        setLang(profile.preferred_language as LangCode);
      })
      .catch(() => {
        // Stored token is invalid or expired — clear it rather than get stuck.
        localStorage.removeItem(TOKEN_KEY);
        setToken(null);
        setUser(null);
      })
      .finally(() => setLoading(false));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token]);

  function setSession(newToken: string, newUser: UserProfile) {
    localStorage.setItem(TOKEN_KEY, newToken);
    setToken(newToken);
    setUser(newUser);
    setLang(newUser.preferred_language as LangCode);
    setIsLoggingOut(false);
  }

  function updateUser(newUser: UserProfile) {
    setUser(newUser);
  }

  function logout() {
    setIsLoggingOut(true);
    localStorage.removeItem(TOKEN_KEY);
    setToken(null);
    setUser(null);
  }

  return (
    <AuthContext.Provider value={{ token, user, loading, isLoggingOut, setSession, updateUser, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthState {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}

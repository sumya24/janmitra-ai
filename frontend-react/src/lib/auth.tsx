import { createContext, useContext, useEffect, useState, type ReactNode } from "react";
import {
  api,
  clearStoredSession,
  getStoredAccessToken,
  getStoredRefreshToken,
  setSessionHandlers,
  storeSession,
  type UserProfile,
} from "./api";
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
  setSession: (accessToken: string, refreshToken: string, user: UserProfile) => void;
  updateUser: (user: UserProfile) => void;
  logout: () => void;
}

const AuthContext = createContext<AuthState | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setToken] = useState<string | null>(() => getStoredAccessToken());
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
        // Stored token is invalid/expired AND api.ts's own silent-refresh-on-401 (triggered by
        // this exact api.me() call, since it passes a token) already failed too -- there's
        // genuinely no session left; api.ts's onSessionExpired handler below already cleared
        // storage, this just clears the remaining React state to match.
        setToken(null);
        setUser(null);
      })
      .finally(() => setLoading(false));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token]);

  // Registered once -- lets api.ts's module-level silentRefresh() (fired from ANY page's API
  // call, not just this provider's own effect above) keep this context's `token`/`user` in sync
  // with whatever it silently did to localStorage in the background.
  useEffect(() => {
    setSessionHandlers({
      onSessionRefreshed: (accessToken, _refreshToken, refreshedUser) => {
        setToken(accessToken);
        setUser(refreshedUser);
      },
      onSessionExpired: () => {
        setToken(null);
        setUser(null);
      },
    });
  }, []);

  function setSession(accessToken: string, refreshToken: string, newUser: UserProfile) {
    storeSession(accessToken, refreshToken);
    setToken(accessToken);
    setUser(newUser);
    setLang(newUser.preferred_language as LangCode);
    setIsLoggingOut(false);
  }

  function updateUser(newUser: UserProfile) {
    setUser(newUser);
  }

  function logout() {
    setIsLoggingOut(true);
    // Real, server-side revocation now, not just a local clear -- see backend/routes/auth.py's
    // logout docstring. Best-effort: fires and forgets rather than awaiting, so a slow/failed
    // network call never blocks the citizen from actually leaving their session locally; a
    // refresh token that fails to revoke server-side this way still expires naturally within
    // REFRESH_TOKEN_EXPIRE_DAYS regardless.
    const refreshToken = getStoredRefreshToken();
    if (refreshToken) api.logout(refreshToken).catch(() => {});
    clearStoredSession();
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

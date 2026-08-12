import { createContext, useContext, useEffect, useState, type ReactNode } from "react";

export type ThemePref = "light" | "dark" | "system";

const THEME_KEY = "janmitra.theme";

interface ThemeState {
  theme: ThemePref;
  setTheme: (theme: ThemePref) => void;
}

const ThemeContext = createContext<ThemeState | null>(null);

function applyTheme(theme: ThemePref) {
  const root = document.documentElement;
  if (theme === "system") {
    root.removeAttribute("data-theme");
  } else {
    root.setAttribute("data-theme", theme);
  }
}

export function ThemeProvider({ children }: { children: ReactNode }) {
  const [theme, setThemeState] = useState<ThemePref>(
    () => (localStorage.getItem(THEME_KEY) as ThemePref) || "system"
  );

  useEffect(() => {
    applyTheme(theme);
  }, [theme]);

  function setTheme(next: ThemePref) {
    localStorage.setItem(THEME_KEY, next);
    setThemeState(next);
  }

  return <ThemeContext.Provider value={{ theme, setTheme }}>{children}</ThemeContext.Provider>;
}

export function useTheme(): ThemeState {
  const ctx = useContext(ThemeContext);
  if (!ctx) throw new Error("useTheme must be used within ThemeProvider");
  return ctx;
}

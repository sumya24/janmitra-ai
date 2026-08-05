import { useTheme, type ThemePref } from "../lib/theme";

const NEXT: Record<ThemePref, ThemePref> = {
  system: "light",
  light: "dark",
  dark: "system",
};

const LABEL: Record<ThemePref, string> = {
  system: "Theme: matching your device",
  light: "Theme: light",
  dark: "Theme: dark",
};

/** Icon button that cycles System → Light → Dark → System, persisting the choice. */
export default function ThemeToggle({ className = "icon-btn" }: { className?: string }) {
  const { theme, setTheme } = useTheme();

  return (
    <button
      type="button"
      className={className}
      onClick={() => setTheme(NEXT[theme])}
      aria-label={LABEL[theme]}
      title={LABEL[theme]}
    >
      {theme === "light" && (
        <svg width="17" height="17" viewBox="0 0 24 24" fill="none">
          <circle cx="12" cy="12" r="4.5" stroke="currentColor" strokeWidth="1.8" />
          <path
            d="M12 2.5v2.4M12 19.1v2.4M4.6 4.6l1.7 1.7M17.7 17.7l1.7 1.7M2.5 12h2.4M19.1 12h2.4M4.6 19.4l1.7-1.7M17.7 6.3l1.7-1.7"
            stroke="currentColor"
            strokeWidth="1.8"
            strokeLinecap="round"
          />
        </svg>
      )}
      {theme === "dark" && (
        <svg width="17" height="17" viewBox="0 0 24 24" fill="none">
          <path
            d="M20.5 14.8A8.5 8.5 0 0 1 9.2 3.5a8.5 8.5 0 1 0 11.3 11.3Z"
            stroke="currentColor"
            strokeWidth="1.6"
            strokeLinejoin="round"
          />
        </svg>
      )}
      {theme === "system" && (
        <svg width="17" height="17" viewBox="0 0 24 24" fill="none">
          <rect x="3" y="4.5" width="18" height="12" rx="2" stroke="currentColor" strokeWidth="1.6" />
          <path d="M8.5 20h7M12 16.5V20" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" />
        </svg>
      )}
    </button>
  );
}

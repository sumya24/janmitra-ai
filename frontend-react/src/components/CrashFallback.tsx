/** Last-resort fallback for a genuine React render crash (see src/main.tsx's Sentry.ErrorBoundary
 * -- reporting to Sentry when configured is a separate concern from showing this; this always
 * renders on a crash, DSN or not). Without this, a crash anywhere in the tree used to unmount
 * straight to a blank white page with no way back except knowing to hit reload yourself.
 * Deliberately plain, inline-styled markup, not the app's normal component library -- if the
 * crash is severe enough to reach here, it should not depend on any of the same app state/CSS
 * that may have contributed to it. */
export default function CrashFallback() {
  return (
    <div
      style={{
        minHeight: "100dvh",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        gap: 16,
        padding: 24,
        textAlign: "center",
        fontFamily: "system-ui, sans-serif",
        background: "#F8FAFC",
        color: "#0F172A",
      }}
    >
      <h1 style={{ fontSize: 20, margin: 0 }}>Something went wrong</h1>
      <p style={{ margin: 0, color: "#475569", maxWidth: 360 }}>
        JanSarthi AI hit an unexpected error. Reloading the page usually fixes it.
      </p>
      <button
        type="button"
        onClick={() => window.location.reload()}
        style={{
          padding: "10px 20px",
          borderRadius: 8,
          border: "none",
          background: "#0F2D6B",
          color: "#F8FAFC",
          fontWeight: 600,
          cursor: "pointer",
        }}
      >
        Reload page
      </button>
    </div>
  );
}

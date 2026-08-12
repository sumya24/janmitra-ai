import type { ComplaintLifecycleStatus } from "../lib/ragTypes";
import type { ComplaintStatus } from "../lib/api";

/** Accepts either the real API's current 4-value status or the full 8-state lifecycle
 * vocabulary from ragTypes — the real backend only ever sends the former today; the latter
 * exist so this component (icon + color + CSS class) is ready the moment a backend adds
 * REJECTED/ESCALATED/CANCELLED as real, persisted states, without a rewrite. */
type AnyStatus = ComplaintStatus | ComplaintLifecycleStatus;

const NORMALIZED: Record<string, { cssClass: string; icon: string }> = {
  pending: { cssClass: "pending", icon: "circle" },
  submitted: { cssClass: "pending", icon: "circle" },
  assigned: { cssClass: "assigned", icon: "arrow" },
  accepted: { cssClass: "accepted", icon: "check" },
  in_progress: { cssClass: "accepted", icon: "gear" },
  resolved: { cssClass: "resolved", icon: "check-filled" },
  rejected: { cssClass: "critical", icon: "x" },
  escalated: { cssClass: "critical", icon: "arrow-up" },
  cancelled: { cssClass: "muted", icon: "x-muted" },
};

const ICONS: Record<string, React.ReactNode> = {
  circle: <circle cx="6" cy="6" r="3" fill="currentColor" />,
  arrow: (
    <path d="M2.5 6h7M6 2.5 9.5 6 6 9.5" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" fill="none" />
  ),
  check: <path d="M2.5 6.2 4.8 8.5 9.5 3.5" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round" fill="none" />,
  gear: <circle cx="6" cy="6" r="3.2" stroke="currentColor" strokeWidth="1.6" fill="none" />,
  "check-filled": (
    <>
      <circle cx="6" cy="6" r="5.2" fill="currentColor" opacity="0.18" />
      <path d="M3 6.2 5.2 8.4 9 3.6" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round" fill="none" />
    </>
  ),
  x: <path d="M3 3l6 6M9 3 3 9" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" fill="none" />,
  "arrow-up": <path d="M6 9.5v-7M2.8 5.3 6 2l3.2 3.3" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round" fill="none" />,
  "x-muted": <path d="M3.5 3.5l5 5M8.5 3.5l-5 5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" fill="none" />,
};

/** A status pill communicating through color + icon + text together — never color alone, so
 * it stays legible for color-blind users. `status` drives the icon/color; `label` is the
 * already-translated, already-role-specific text (citizen and worker see different phrasing
 * for the same underlying status today — see STATUS_LABEL_KEY in each dashboard — this
 * component doesn't own that copy, just the visual language around it). */
export default function StatusBadge({ status, label }: { status: AnyStatus; label: string }) {
  const key = status.toLowerCase();
  const cfg = NORMALIZED[key] ?? { cssClass: "pending", icon: "circle" };
  return (
    <span className={`status-badge ${cfg.cssClass}`}>
      <svg width="12" height="12" viewBox="0 0 12 12" aria-hidden="true">
        {ICONS[cfg.icon]}
      </svg>
      {label}
    </span>
  );
}

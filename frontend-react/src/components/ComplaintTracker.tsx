import { t, type LangCode } from "../lib/i18n";
import type { ComplaintStatus } from "../lib/api";

/** Horizontal step tracker (submitted → assigned → in progress → resolved), the same shape as
 * a delivery-tracking timeline. A "searching for another worker" state (after a rejection, before
 * reassignment lands) shows as a distinct amber pulsing dot on the "assigned" step rather than
 * either a plain future step or a false "assigned" — it's neither, it's actively in motion. */
export default function ComplaintTracker({
  status,
  rejectionCount,
  lang,
}: {
  status: ComplaintStatus;
  rejectionCount: number;
  lang: LangCode;
}) {
  const isSearching = status === "pending" && rejectionCount > 0;

  // 0 = only "submitted" is done, 1 = assigned, 2 = accepted/in_progress, 3 = resolved.
  // "in_progress" reuses step 2 ("In Progress") alongside "accepted" -- without this, a
  // complaint that has actually moved further along than "assigned" would render as if it had
  // reset back to step 0, since neither "accepted" nor "assigned" would match.
  const currentIndex =
    status === "resolved" ? 3 : status === "accepted" || status === "in_progress" ? 2 : status === "assigned" ? 1 : 0;

  const steps = [
    { label: t(lang, "citizen.trackSubmitted") },
    { label: t(lang, "citizen.trackAssigned") },
    { label: t(lang, "citizen.trackInProgress") },
    { label: t(lang, "citizen.statusResolved") },
  ];

  return (
    <div style={{ display: "flex", alignItems: "flex-start", margin: "12px 0 4px" }}>
      {steps.map((step, i) => {
        const done = i <= currentIndex && !(i === 1 && isSearching);
        const active = i === 1 && isSearching;
        const isLast = i === steps.length - 1;
        return (
          <div key={step.label} style={{ display: "flex", alignItems: "flex-start", flex: isLast ? "0 0 auto" : 1 }}>
            <div style={{ display: "flex", flexDirection: "column", alignItems: "center", width: 64 }}>
              <div
                className={active ? "tracker-dot-active" : undefined}
                style={{
                  width: 22,
                  height: 22,
                  borderRadius: "50%",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  fontSize: 12,
                  fontWeight: 700,
                  background: done
                    ? (i === 3 ? "var(--status-resolved)" : "var(--primary)")
                    : active
                    ? "var(--status-open)"
                    : "var(--surface-2)",
                  color: done || active ? "var(--primary-ink)" : "var(--ink-3)",
                  border: done || active ? "none" : "1.5px solid var(--line)",
                }}
              >
                {i === 3 && done ? "✓" : ""}
              </div>
              <div
                style={{
                  fontSize: 10.5,
                  marginTop: 4,
                  textAlign: "center",
                  color: done || active ? "var(--ink)" : "var(--ink-3)",
                  fontWeight: done || active ? 700 : 500,
                }}
              >
                {step.label}
              </div>
            </div>
            {!isLast && (
              <div
                style={{
                  flex: 1,
                  height: 2,
                  marginTop: 10,
                  background: i < currentIndex && !(i === 1 && isSearching) ? "var(--primary)" : "var(--line)",
                }}
              />
            )}
          </div>
        );
      })}
    </div>
  );
}

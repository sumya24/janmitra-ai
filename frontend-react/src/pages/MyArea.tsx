import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import TopBar from "../components/TopBar";
import StatusBadge from "../components/StatusBadge";
import { useAuth } from "../lib/auth";
import { useUiLang } from "../lib/uiLang";
import { t } from "../lib/i18n";
import { api, ApiError, type AreaSummary } from "../lib/api";
import { SERVICE_CATEGORY_DEFS } from "../lib/serviceCategories";
import "../styles/dashboard.css";

const STATUS_LABEL_KEY = {
  pending: "citizen.statusPending",
  assigned: "citizen.statusAssigned",
  accepted: "citizen.statusAccepted",
  // Reuses the citizen-facing tracker's own existing "In progress" label rather than adding a
  // near-duplicate string for the same status.
  in_progress: "citizen.trackInProgress",
  resolved: "citizen.statusResolved",
} as const;

// The most recent 15 -- a ward's total complaint history could grow large; "My Area" is meant
// to be a quick, scannable neighborhood snapshot, not a full searchable archive (that already
// exists, scoped to the citizen's own complaints, on "My Complaints").
const MAX_LISTED = 15;

/**
 * My Area (P1, Task 10, extended): a ward-wide neighborhood dashboard -- every complaint filed
 * in the citizen's own ward, not just their own, backed by the real GET /complaints/area-summary
 * endpoint (see backend/routes/complaints.py's AreaSummaryResponse docstring). Deliberately
 * anonymized: the backend response never includes citizen_id or any complainant-identifying
 * field at all, so there's nothing here to accidentally render even if this component tried to
 * -- the "who filed it" question has no answer available client-side, by construction.
 *
 * Stat cards use the same .stat-card convention as Admin/WorkerDashboard (styles/dashboard.css)
 * for a consistent "pending / in progress / resolved" glance, then a scannable list of the ward's
 * own recent complaints, each showing its current status and the date that status was reached
 * (filed / started / completed) rather than one flat "filed on" date regardless of where it is
 * in its lifecycle.
 */
export default function MyArea() {
  const { token, user } = useAuth();
  const { lang } = useUiLang();
  const [summary, setSummary] = useState<AreaSummary | null>(null);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  const ward = user?.ward ?? null;

  useEffect(() => {
    if (!token || !ward) {
      setLoading(false);
      return;
    }
    setLoading(true);
    setLoadError(null);
    api
      .getAreaSummary(token, lang)
      .then(setSummary)
      .catch((err) => setLoadError(err instanceof ApiError ? err.message : t(lang, "area.emptyNoWard")))
      .finally(() => setLoading(false));
  }, [token, lang, ward]);

  function statusDateLabel(status: string): string {
    if (status === "resolved") return t(lang, "area.completedOn");
    if (status === "in_progress") return t(lang, "area.startedOn");
    return t(lang, "area.filedOn");
  }

  return (
    <div>
      <TopBar />
      <div className="page" id="main-content">
        <div className="page-head">
          <div>
            <h1 className="page-title display">{t(lang, "area.title")}</h1>
            <p className="page-sub">{ward ? ward : t(lang, "area.noWardSet")}</p>
          </div>
        </div>

        {ward && !loading && !loadError && summary && (
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(150px, 1fr))", gap: 12, marginBottom: 30 }}>
            <div className="surface-card hoverable stat-card">
              <div className="stat-label">{t(lang, "admin.pendingStat")}</div>
              <div className="display stat-value" style={{ color: "var(--status-critical)" }}>{summary.pending_count}</div>
            </div>
            <div className="surface-card hoverable stat-card">
              <div className="stat-label">{t(lang, "worker.filterInProgress")}</div>
              <div className="display stat-value" style={{ color: "var(--status-open)" }}>{summary.in_progress_count}</div>
            </div>
            <div className="surface-card hoverable stat-card">
              <div className="stat-label">{t(lang, "citizen.resolved")}</div>
              <div className="display stat-value" style={{ color: "var(--status-resolved)" }}>{summary.resolved_count}</div>
            </div>
          </div>
        )}

        <div className="section-label" style={{ marginTop: 0 }}>{t(lang, "area.servicesLabel")}</div>
        <div className="service-grid" style={{ marginBottom: 30 }}>
          {SERVICE_CATEGORY_DEFS.map((def) => (
            <Link key={def.id} to={`/citizen/report?service=${def.id}`} className={`service-card service-card-${def.color} surface-card hoverable`}>
              <div className="service-card-icon">{def.icon}</div>
              <h3>{t(lang, def.titleKey)}</h3>
              <p>{t(lang, def.descriptionKey)}</p>
            </Link>
          ))}
        </div>

        <div className="section-label">{t(lang, "area.recentLabel")}</div>
        {loading && (
          <div className="surface-card" style={{ padding: "14px 16px" }}>
            <div className="skeleton" style={{ width: "60%", height: 14 }} />
          </div>
        )}
        {!loading && !ward && (
          <div className="surface-card" style={{ padding: 20, color: "var(--ink-2)", fontSize: 13 }}>
            {t(lang, "area.emptyNoWard")}
          </div>
        )}
        {!loading && ward && loadError && <div className="banner-error">{loadError}</div>}
        {!loading && ward && !loadError && summary && summary.complaints.length === 0 && (
          <div className="surface-card" style={{ padding: 20, color: "var(--ink-2)", fontSize: 13 }}>
            {t(lang, "area.emptyNoComplaints")}
          </div>
        )}
        {!loading && ward && !loadError && summary && summary.complaints.length > 0 && (
          <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
            {summary.complaints.slice(0, MAX_LISTED).map((c) => (
              <div key={c.id} className="surface-card" style={{ padding: "12px 16px", display: "flex", justifyContent: "space-between", gap: 10, alignItems: "center", flexWrap: "wrap" }}>
                <div>
                  <div className="mono" style={{ fontSize: 11, color: "var(--ink-3)" }}>JM-{String(c.id).padStart(5, "0")}</div>
                  <div style={{ fontSize: 13, fontWeight: 600 }}>{c.display_text}</div>
                  <div style={{ fontSize: 11, color: "var(--ink-3)", marginTop: 2 }}>
                    {statusDateLabel(c.status)} {new Date(c.status_updated_at).toLocaleDateString()}
                  </div>
                </div>
                <StatusBadge status={c.status} label={t(lang, STATUS_LABEL_KEY[c.status])} />
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

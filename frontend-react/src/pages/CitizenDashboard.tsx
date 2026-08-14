import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import TopBar from "../components/TopBar";
import ComplaintTracker from "../components/ComplaintTracker";
import StatusBadge from "../components/StatusBadge";
import ComplaintUpdatesTimeline from "../components/ComplaintUpdatesTimeline";
import ReportModal from "../components/ReportModal";
import SummaryModal from "../components/SummaryModal";
import DownloadReportButton from "../components/DownloadReportButton";
import FeedbackForm from "../components/FeedbackForm";
import { useAuth } from "../lib/auth";
import { useUiLang } from "../lib/uiLang";
import { t } from "../lib/i18n";
import { api, ApiError, type Complaint, type ComplaintUpdateEntry } from "../lib/api";

const STATUS_LABEL_KEY = {
  pending: "citizen.statusPending",
  assigned: "citizen.statusAssigned",
  accepted: "citizen.statusAccepted",
  // Reuses the citizen-facing tracker's own existing "In progress" label rather than adding a
  // near-duplicate string for the same status.
  in_progress: "citizen.trackInProgress",
  resolved: "citizen.statusResolved",
} as const;

// Polling interval for "live" tracking updates (accept/reject/reassignment/resolve) while
// anything is still in flight — this app has no websockets/SSE, so a short poll is the fast,
// simple way to make status changes show up without the citizen having to manually refresh.
const LIVE_POLL_MS = 8000;

export default function CitizenDashboard() {
  const { token } = useAuth();
  const navigate = useNavigate();
  // Single source of language for this whole page: the account's preferred language (kept in
  // sync with uiLang — see auth.tsx/SettingsModal). It drives both what language the complaint
  // list displays in *and* what language a new complaint is submitted as — no separate "what
  // language is this complaint in" picker; Settings is the one place to change either.
  const { lang } = useUiLang();
  const [complaints, setComplaints] = useState<Complaint[]>([]);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  // Worker-authored updates (initial assessment / progress updates / completion status) --
  // lazily fetched per complaint only when the citizen actually expands that card, not eagerly
  // for the whole list (list load stays a cheap query -- see backend/routes/complaints.py's
  // ComplaintDetailResponse docstring).
  const [expandedId, setExpandedId] = useState<number | null>(null);
  const [updatesById, setUpdatesById] = useState<Record<number, ComplaintUpdateEntry[]>>({});
  const [updatesLoadingId, setUpdatesLoadingId] = useState<number | null>(null);
  const [updatesError, setUpdatesError] = useState<Record<number, string>>({});
  const [reportModalId, setReportModalId] = useState<number | null>(null);
  const [summaryComplaint, setSummaryComplaint] = useState<Complaint | null>(null);

  async function toggleUpdates(id: number) {
    if (expandedId === id) {
      setExpandedId(null);
      return;
    }
    setExpandedId(id);
    if (!updatesById[id] && token) {
      setUpdatesLoadingId(id);
      try {
        const detail = await api.getComplaint(token, id, lang);
        setUpdatesById((prev) => ({ ...prev, [id]: detail.updates }));
      } catch (err) {
        setUpdatesError((prev) => ({ ...prev, [id]: err instanceof ApiError ? err.message : t(lang, "updates.errLoadFailed") }));
      } finally {
        setUpdatesLoadingId(null);
      }
    }
  }

  async function loadComplaints() {
    if (!token) return;
    setLoadError(null);
    try {
      const data = await api.listComplaints(token, lang);
      setComplaints(data);
    } catch (err) {
      setLoadError(err instanceof ApiError ? err.message : t(lang, "citizen.errLoadFailed"));
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    setLoading(true);
    loadComplaints();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token, lang]);

  // Live tracking: while anything is still moving through the pipeline (not resolved), poll
  // for updates so an accept/reject/reassignment shows up without a manual refresh.
  useEffect(() => {
    if (!token) return;
    const hasActiveComplaint = complaints.some((c) => c.status !== "resolved");
    if (!hasActiveComplaint) return;
    const interval = setInterval(loadComplaints, LIVE_POLL_MS);
    return () => clearInterval(interval);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token, lang, complaints]);

  const openCount = complaints.filter((c) => c.status !== "resolved").length;
  const resolvedCount = complaints.filter((c) => c.status === "resolved").length;

  return (
    <div>
      <TopBar />
      <div className="page" id="main-content">
        <div className="page-head">
          <div>
            <h1 className="page-title display">{t(lang, "citizen.myComplaintsTitle")}</h1>
            <p className="page-sub">{t(lang, "citizen.myComplaintsSubtitle")}</p>
          </div>
          <Link to="/citizen/report" className="btn btn-primary">
            {t(lang, "home.hero.reportCta")}
          </Link>
        </div>

        {loadError && <div className="banner-error">{loadError}</div>}

        <div className="statstrip" style={{ display: "flex", gap: 10, marginBottom: 26 }}>
          <div className="surface-card hoverable" style={{ padding: "10px 16px", flex: 1 }}>
            <div className="display" style={{ fontSize: 26, color: "var(--status-open)" }}>{openCount}</div>
            <div style={{ fontSize: 11, color: "var(--ink-2)" }}>{t(lang, "citizen.open")}</div>
          </div>
          <div className="surface-card hoverable" style={{ padding: "10px 16px", flex: 1 }}>
            <div className="display" style={{ fontSize: 26, color: "var(--status-resolved)" }}>{resolvedCount}</div>
            <div style={{ fontSize: 11, color: "var(--ink-2)" }}>{t(lang, "citizen.resolved")}</div>
          </div>
        </div>

        <div className="section-label" style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <span>{t(lang, "citizen.yourComplaints")}</span>
        </div>

        {loading && (
          <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
            {[0, 1].map((i) => (
              <div key={i} className="surface-card" style={{ padding: "14px 16px" }}>
                <div className="skeleton" style={{ width: "70%", height: 15, marginBottom: 10 }} />
                <div className="skeleton" style={{ width: "40%", height: 12, marginBottom: 14 }} />
                <div className="skeleton" style={{ width: "100%", height: 30 }} />
              </div>
            ))}
          </div>
        )}
        {!loading && complaints.length === 0 && <p style={{ color: "var(--ink-2)" }}>{t(lang, "citizen.noComplaints")}</p>}

        <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
          {complaints.map((c, i) => (
            <div key={c.id} className="surface-card hoverable enter" style={{ padding: "14px 16px", "--stagger": Math.min(i, 6) } as React.CSSProperties}>
              {/* Same click-to-detail pattern as WorkerDashboard.tsx's queue cards -- only the
                  summary row navigates (cursor:pointer), everything below (tracker, updates
                  toggle, report/download, feedback) stays outside it, so those controls don't
                  need stopPropagation. */}
              <div
                style={{ display: "flex", justifyContent: "space-between", gap: 12, flexWrap: "wrap", cursor: "pointer" }}
                onClick={() => navigate(`/citizen/complaints/${c.id}`)}
              >
                <div>
                  <div className="mono" style={{ fontSize: 11, color: "var(--ink-3)" }}>JM-{String(c.id).padStart(5, "0")}</div>
                  <div style={{ fontWeight: 600, margin: "3px 0" }}>{c.display_text}</div>
                  <div style={{ fontSize: 12, color: "var(--ink-2)" }}>{c.display_summary}</div>
                </div>
                <div style={{ textAlign: "right" }}>
                  <StatusBadge status={c.status} label={t(lang, STATUS_LABEL_KEY[c.status])} />
                  <div style={{ fontSize: 11, color: "var(--ink-3)", marginTop: 6 }}>{new Date(c.created_at).toLocaleString()}</div>
                </div>
              </div>

              <ComplaintTracker status={c.status} rejectionCount={c.rejection_count} lang={lang} />

              {/* Tracking details: who it's with, live reassignment status, contact once accepted. */}
              {c.status === "pending" && c.rejection_count > 0 && (
                <div style={{ fontSize: 12, color: "var(--status-open)", marginTop: 8 }}>
                  {t(lang, "citizen.searchingNextWorker")}
                </div>
              )}
              {c.assigned_worker_name && (
                <div style={{ fontSize: 12, color: "var(--ink-2)", marginTop: 8 }}>
                  {t(lang, "citizen.assignedTo")}: <strong style={{ color: "var(--ink)" }}>{c.assigned_worker_name}</strong>
                  {c.assigned_worker_phone && (
                    <>
                      {" · "}
                      {t(lang, "citizen.workerPhone")}:{" "}
                      <a href={`tel:${c.assigned_worker_phone}`} className="mono">{c.assigned_worker_phone}</a>
                    </>
                  )}
                </div>
              )}

              {c.photo_path && (
                <img src={api.photoUrl(c.photo_path)} alt={t(lang, "citizen.attached")} style={{ marginTop: 10, maxWidth: 160, borderRadius: 8, border: "1px solid var(--line)" }} />
              )}

              {/* Worker-authored updates -- initial assessment / optional progress updates /
                  completion status. Only worth offering to expand once there's a chance
                  something exists (in_progress or resolved); never internal-only info (no
                  rejection reasons, no admin notes -- see ComplaintUpdatesTimeline, which only
                  ever renders the three citizen-visible update types). */}
              {(c.status === "in_progress" || c.status === "resolved") && (
                <div style={{ marginTop: 10, paddingTop: 10, borderTop: "1px solid var(--line)" }}>
                  <button type="button" className="btn btn-ghost btn-sm" onClick={() => toggleUpdates(c.id)}>
                    {expandedId === c.id ? t(lang, "updates.hide") : t(lang, "updates.view")}
                  </button>
                  {expandedId === c.id && (
                    <div style={{ marginTop: 10 }}>
                      {updatesLoadingId === c.id && <p style={{ color: "var(--ink-2)", fontSize: 13 }}>{t(lang, "common.loading")}</p>}
                      {updatesError[c.id] && <div className="banner-error">{updatesError[c.id]}</div>}
                      {updatesById[c.id] && <ComplaintUpdatesTimeline updates={updatesById[c.id]} />}
                    </div>
                  )}
                </div>
              )}

              {c.status === "resolved" && (
                <div style={{ marginTop: 10, display: "flex", gap: 6 }}>
                  <button type="button" className="btn btn-ghost btn-sm" onClick={() => setSummaryComplaint(c)}>
                    {t(lang, "worker.viewSummary")}
                  </button>
                  <button type="button" className="btn btn-ghost btn-sm" onClick={() => setReportModalId(c.id)}>
                    {t(lang, "worker.viewReport")}
                  </button>
                  <DownloadReportButton complaintId={c.id} />
                </div>
              )}

              {c.status === "resolved" && token && (
                c.feedback_rating ? (
                  <div style={{ marginTop: 10, paddingTop: 10, borderTop: "1px solid var(--line)", fontSize: 12, color: "var(--ink-2)" }}>
                    {t(lang, "citizen.feedbackSubmitted")} {"★".repeat(c.feedback_rating)}
                    {c.feedback_comment && <div style={{ marginTop: 4 }}>{c.feedback_comment}</div>}
                  </div>
                ) : (
                  <FeedbackForm complaintId={c.id} lang={lang} token={token} onSubmitted={loadComplaints} />
                )
              )}
            </div>
          ))}
        </div>
      </div>
      {reportModalId !== null && <ReportModal complaintId={reportModalId} onClose={() => setReportModalId(null)} />}
      {summaryComplaint && (
        <SummaryModal
          complaint={summaryComplaint}
          statusLabel={t(lang, STATUS_LABEL_KEY[summaryComplaint.status])}
          onClose={() => setSummaryComplaint(null)}
        />
      )}
    </div>
  );
}

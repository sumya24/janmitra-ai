import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import TopBar from "../components/TopBar";
import StatusBadge from "../components/StatusBadge";
import RejectComplaintModal from "../components/RejectComplaintModal";
import StartWorkModal from "../components/StartWorkModal";
import ProgressUpdateModal from "../components/ProgressUpdateModal";
import CompleteComplaintModal from "../components/CompleteComplaintModal";
import ReportModal from "../components/ReportModal";
import SummaryModal from "../components/SummaryModal";
import DownloadReportButton from "../components/DownloadReportButton";
import { useAuth } from "../lib/auth";
import { useUiLang } from "../lib/uiLang";
import { t } from "../lib/i18n";
import { api, ApiError, type Complaint } from "../lib/api";
import { useToast } from "../lib/toast";
import "../styles/dashboard.css";

const STATUS_LABEL_KEY = {
  // Same reasoning as "pending" below -- a worker shouldn't normally see a complaint still
  // sitting at "open" either, but without an explicit entry StatusBadge rendered no label text
  // at all (just its icon) on the rare complaint that does.
  open: "worker.filterAssigned",
  pending: "worker.filterAssigned", // a worker never actually sees "pending" (unassigned) items
  assigned: "worker.statusAssigned",
  accepted: "worker.statusAccepted",
  // Reuses the same "In progress" wording already shown for "accepted" -- both read as "work is
  // happening" from the worker's own point of view.
  in_progress: "worker.statusAccepted",
  resolved: "worker.resolved",
} as const;

type ActionModal = "reject" | "start" | "update" | "complete" | "report" | "summary" | null;

export default function WorkerDashboard() {
  const { user, token } = useAuth();
  const { lang } = useUiLang();
  const navigate = useNavigate();
  const [complaints, setComplaints] = useState<Complaint[]>([]);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const toast = useToast();
  const [actingId, setActingId] = useState<number | null>(null);
  // Defaults to "all", not "assigned" — accepting a complaint moves it to "accepted", which
  // would otherwise make it silently vanish from a narrower default filter right after acting
  // on it (confusing: "where did it go?"). The worker can still narrow down manually.
  const [filter, setFilter] = useState<"all" | "assigned" | "accepted" | "in_progress" | "resolved">("all");

  // Which complaint has an action modal open, and which modal -- one at a time, keyed by
  // complaint id so a re-render of the list (e.g. after a poll/reload) doesn't lose track of
  // which card's modal is showing.
  const [modalFor, setModalFor] = useState<{ id: number; type: ActionModal } | null>(null);

  async function load() {
    if (!token) return;
    setLoading(true);
    setLoadError(null);
    try {
      setComplaints(await api.listComplaints(token, lang));
    } catch (err) {
      setLoadError(err instanceof ApiError ? err.message : t(lang, "worker.errLoadFailed"));
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token, lang]);

  async function accept(id: number) {
    if (!token) return;
    setActingId(id);
    try {
      await api.acceptComplaint(token, id);
      toast.success(t(lang, "worker.acceptedToast"));
      await load();
    } catch (err) {
      toast.error(err instanceof ApiError ? err.message : t(lang, "worker.errAcceptFailed"));
    } finally {
      setActingId(null);
    }
  }

  function closeModal() {
    setModalFor(null);
  }

  // A worker's queue only ever contains complaints currently assigned to them (see
  // backend/routes/complaints.py) — so "open" here means everything short of resolved.
  const openCount = complaints.filter((c) => c.status !== "resolved").length;
  const resolvedCount = complaints.filter((c) => c.status === "resolved").length;
  const visible = complaints.filter((c) => filter === "all" || c.status === filter);

  return (
    <div>
      <TopBar />
      <div className="page" id="main-content">
        <div className="page-head">
          <div>
            <h1 className="page-title display">{t(lang, "worker.title")}</h1>
            <p className="page-sub">{user?.ward ? `${t(lang, "worker.wardPrefix")}: ${user.ward}` : t(lang, "worker.noWard")}</p>
          </div>
        </div>

        <div style={{ display: "flex", gap: 10, marginBottom: 20 }}>
          <div className="surface-card hoverable stat-card" style={{ flex: 1 }}>
            <div className="stat-label">{t(lang, "worker.open")}</div>
            <div className="display stat-value" style={{ color: "var(--status-open)" }}>{openCount}</div>
          </div>
          <div className="surface-card hoverable stat-card" style={{ flex: 1 }}>
            <div className="stat-label">{t(lang, "worker.resolved")}</div>
            <div className="display stat-value" style={{ color: "var(--status-resolved)" }}>{resolvedCount}</div>
          </div>
        </div>

        <div style={{ display: "flex", gap: 6, marginBottom: 16, flexWrap: "wrap" }}>
          {(["all", "assigned", "accepted", "in_progress", "resolved"] as const).map((f) => (
            <button
              key={f}
              onClick={() => setFilter(f)}
              style={{
                background: filter === f ? "var(--ink)" : "var(--surface)",
                color: filter === f ? "var(--paper)" : "var(--ink-2)",
                border: "1px solid var(--line)", borderRadius: 20, padding: "7px 14px", fontSize: 12.5, fontWeight: 600,
              }}
            >
              {f === "all" ? t(lang, "worker.filterAll")
                : f === "assigned" ? t(lang, "worker.filterAssigned")
                : f === "accepted" ? t(lang, "worker.filterAccepted")
                : f === "in_progress" ? t(lang, "worker.filterInProgress")
                : t(lang, "worker.filterResolved")}
            </button>
          ))}
        </div>

        {loadError && <div className="banner-error">{loadError}</div>}
        {loading && (
          <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
            {[0, 1, 2].map((i) => (
              <div key={i} className="surface-card" style={{ padding: "14px 16px" }}>
                <div className="skeleton" style={{ width: "60%", height: 15, marginBottom: 10 }} />
                <div className="skeleton" style={{ width: "35%", height: 12 }} />
              </div>
            ))}
          </div>
        )}
        {!loading && visible.length === 0 && <p style={{ color: "var(--ink-2)" }}>{t(lang, "worker.nothingHere")}</p>}

        <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
          {visible.map((c, i) => (
            <div key={c.id} className="surface-card hoverable enter" style={{ padding: "14px 16px", "--stagger": Math.min(i, 6) } as React.CSSProperties}>
              <div
                style={{ display: "flex", justifyContent: "space-between", gap: 16, flexWrap: "wrap", cursor: "pointer" }}
                onClick={() => navigate(`/worker/complaints/${c.id}`)}
              >
                <div>
                  <div className="mono" style={{ fontSize: 11, color: "var(--ink-3)" }}>JM-{String(c.id).padStart(5, "0")}</div>
                  <div style={{ fontWeight: 600, margin: "3px 0" }}>{c.display_text}</div>
                  <div style={{ fontSize: 12, color: "var(--ink-2)" }}>{c.display_summary}</div>
                </div>
                <div style={{ display: "flex", flexDirection: "column", alignItems: "flex-end", gap: 8 }} onClick={(e) => e.stopPropagation()}>
                  <StatusBadge status={c.status} label={t(lang, STATUS_LABEL_KEY[c.status])} />

                  {/* Per-status action rules -- exactly one of these blocks renders per card, no
                      irrelevant actions for the current status:
                        ASSIGNED    -> [Reject] [Accept]
                        ACCEPTED    -> [Start Work]
                        IN_PROGRESS -> [Add Update] [Complete Complaint]
                        RESOLVED    -> [View Report] [Download Report]
                      See also WorkerComplaintDetail.tsx, which applies the identical rules. */}
                  {c.status === "assigned" && (
                    <div style={{ display: "flex", gap: 6 }}>
                      <button className="btn btn-ghost btn-sm" onClick={() => setModalFor({ id: c.id, type: "reject" })} disabled={actingId === c.id}>
                        {t(lang, "worker.reject")}
                      </button>
                      <button className="btn btn-primary btn-sm" onClick={() => accept(c.id)} disabled={actingId === c.id}>
                        {actingId === c.id ? t(lang, "worker.accepting") : t(lang, "worker.accept")}
                      </button>
                    </div>
                  )}
                  {c.status === "accepted" && (
                    <button className="btn btn-primary btn-sm" onClick={() => setModalFor({ id: c.id, type: "start" })}>
                      {t(lang, "worker.startWork")}
                    </button>
                  )}
                  {c.status === "in_progress" && (
                    <div style={{ display: "flex", gap: 6 }}>
                      <button className="btn btn-ghost btn-sm" onClick={() => setModalFor({ id: c.id, type: "update" })}>
                        {t(lang, "worker.addUpdate")}
                      </button>
                      <button className="btn btn-primary btn-sm" onClick={() => setModalFor({ id: c.id, type: "complete" })}>
                        {t(lang, "worker.completeComplaint")}
                      </button>
                    </div>
                  )}
                  {c.status === "resolved" && (
                    <div style={{ display: "flex", gap: 6 }}>
                      <button className="btn btn-ghost btn-sm" onClick={() => setModalFor({ id: c.id, type: "summary" })}>
                        {t(lang, "worker.viewSummary")}
                      </button>
                      <button className="btn btn-ghost btn-sm" onClick={() => setModalFor({ id: c.id, type: "report" })}>
                        {t(lang, "worker.viewReport")}
                      </button>
                      <DownloadReportButton complaintId={c.id} />
                    </div>
                  )}
                </div>
              </div>
              {c.photo_path && (
                <img
                  src={api.photoUrl(c.photo_path)}
                  alt={t(lang, "worker.attached")}
                  style={{ marginTop: 10, maxWidth: 160, borderRadius: 8, border: "1px solid var(--line)" }}
                  onClick={(e) => e.stopPropagation()}
                />
              )}
            </div>
          ))}
        </div>
      </div>

      {modalFor?.type === "reject" && (
        <RejectComplaintModal
          complaintId={modalFor.id}
          onClose={closeModal}
          onRejected={() => { toast.success(t(lang, "worker.rejectedConfirm")); load(); }}
        />
      )}
      {modalFor?.type === "start" && (
        <StartWorkModal
          complaintId={modalFor.id}
          onClose={closeModal}
          onStarted={() => { toast.success(t(lang, "worker.start.startedToast")); load(); }}
        />
      )}
      {modalFor?.type === "update" && (
        <ProgressUpdateModal
          complaintId={modalFor.id}
          onClose={closeModal}
          onAdded={() => { toast.success(t(lang, "worker.update.addedToast")); load(); }}
        />
      )}
      {modalFor?.type === "complete" && (
        <CompleteComplaintModal
          complaintId={modalFor.id}
          onClose={closeModal}
          onResolved={() => { toast.success(t(lang, "worker.resolvedToast")); load(); }}
        />
      )}
      {modalFor?.type === "report" && <ReportModal complaintId={modalFor.id} onClose={closeModal} />}
      {modalFor?.type === "summary" && (() => {
        const target = complaints.find((c) => c.id === modalFor.id);
        return target ? (
          <SummaryModal complaint={target} statusLabel={t(lang, STATUS_LABEL_KEY[target.status])} onClose={closeModal} />
        ) : null;
      })()}
    </div>
  );
}

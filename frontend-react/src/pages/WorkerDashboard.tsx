import { useEffect, useState } from "react";
import TopBar from "../components/TopBar";
import { useAuth } from "../lib/auth";
import { useUiLang } from "../lib/uiLang";
import { t } from "../lib/i18n";
import { api, ApiError, type Complaint } from "../lib/api";

const STATUS_LABEL_KEY = {
  pending: "worker.filterAssigned", // a worker never actually sees "pending" (unassigned) items
  assigned: "worker.statusAssigned",
  accepted: "worker.statusAccepted",
  resolved: "worker.resolved",
} as const;

export default function WorkerDashboard() {
  const { user, token } = useAuth();
  const { lang } = useUiLang();
  const [complaints, setComplaints] = useState<Complaint[]>([]);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [actionError, setActionError] = useState<string | null>(null);
  const [rejectConfirmId, setRejectConfirmId] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);
  const [actingId, setActingId] = useState<number | null>(null);
  // Defaults to "all", not "assigned" — accepting a complaint moves it to "accepted", which
  // would otherwise make it silently vanish from a narrower default filter right after acting
  // on it (confusing: "where did it go?"). The worker can still narrow down manually.
  const [filter, setFilter] = useState<"all" | "assigned" | "accepted" | "resolved">("all");

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
    setActionError(null);
    setActingId(id);
    try {
      await api.acceptComplaint(token, id);
      await load();
    } catch (err) {
      setActionError(err instanceof ApiError ? err.message : t(lang, "worker.errAcceptFailed"));
    } finally {
      setActingId(null);
    }
  }

  async function reject(id: number) {
    if (!token) return;
    setActionError(null);
    setRejectConfirmId(null);
    setActingId(id);
    try {
      await api.rejectComplaint(token, id);
      // The item leaves this worker's queue immediately (reassigned elsewhere) — without an
      // explicit confirmation it would just silently vanish, leaving no record for the worker
      // that the reject actually went through rather than, say, failing invisibly.
      setRejectConfirmId(id);
      await load();
    } catch (err) {
      setActionError(err instanceof ApiError ? err.message : t(lang, "worker.errRejectFailed"));
    } finally {
      setActingId(null);
    }
  }

  async function resolve(id: number) {
    if (!token) return;
    setActionError(null);
    setActingId(id);
    try {
      await api.resolveComplaint(token, id);
      await load();
    } catch (err) {
      setActionError(err instanceof ApiError ? err.message : t(lang, "worker.errResolveFailed"));
    } finally {
      setActingId(null);
    }
  }

  // A worker's queue only ever contains complaints currently assigned to them (see
  // backend/routes/complaints.py) — so "open" here means "assigned or accepted", not resolved.
  const openCount = complaints.filter((c) => c.status === "assigned" || c.status === "accepted").length;
  const resolvedCount = complaints.filter((c) => c.status === "resolved").length;
  const visible = complaints.filter((c) => filter === "all" || c.status === filter);

  return (
    <div>
      <TopBar />
      <div className="page">
        <div className="page-head">
          <div>
            <h1 className="page-title display">{t(lang, "worker.title")}</h1>
            <p className="page-sub">{user?.ward ? `${t(lang, "worker.wardPrefix")}: ${user.ward}` : t(lang, "worker.noWard")}</p>
          </div>
        </div>

        <div style={{ display: "flex", gap: 10, marginBottom: 20 }}>
          <div style={{ background: "var(--surface)", border: "1px solid var(--line)", borderRadius: 10, padding: "10px 16px", flex: 1 }}>
            <div className="display" style={{ fontSize: 26, color: "var(--status-open)" }}>{openCount}</div>
            <div style={{ fontSize: 11, color: "var(--ink-2)" }}>{t(lang, "worker.open")}</div>
          </div>
          <div style={{ background: "var(--surface)", border: "1px solid var(--line)", borderRadius: 10, padding: "10px 16px", flex: 1 }}>
            <div className="display" style={{ fontSize: 26, color: "var(--status-resolved)" }}>{resolvedCount}</div>
            <div style={{ fontSize: 11, color: "var(--ink-2)" }}>{t(lang, "worker.resolved")}</div>
          </div>
        </div>

        <div style={{ display: "flex", gap: 6, marginBottom: 16, flexWrap: "wrap" }}>
          {(["all", "assigned", "accepted", "resolved"] as const).map((f) => (
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
                : t(lang, "worker.filterResolved")}
            </button>
          ))}
        </div>

        {loadError && <div className="banner-error">{loadError}</div>}
        {actionError && <div className="banner-error">{actionError}</div>}
        {rejectConfirmId !== null && (
          <div style={{ background: "var(--status-open-bg)", color: "var(--status-open)", borderRadius: 8, padding: "10px 14px", fontSize: 13, marginBottom: 14 }}>
            {t(lang, "worker.rejectedConfirm")}
          </div>
        )}
        {loading && <p style={{ color: "var(--ink-2)" }}>{t(lang, "common.loading")}</p>}
        {!loading && visible.length === 0 && <p style={{ color: "var(--ink-2)" }}>{t(lang, "worker.nothingHere")}</p>}

        <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
          {visible.map((c) => (
            <div key={c.id} style={{ background: "var(--surface)", border: "1px solid var(--line)", borderRadius: 12, padding: "14px 16px" }}>
              <div style={{ display: "flex", justifyContent: "space-between", gap: 16, flexWrap: "wrap" }}>
                <div>
                  <div className="mono" style={{ fontSize: 11, color: "var(--ink-3)" }}>JM-{String(c.id).padStart(5, "0")}</div>
                  <div style={{ fontWeight: 600, margin: "3px 0" }}>{c.display_text}</div>
                  <div style={{ fontSize: 12, color: "var(--ink-2)" }}>{c.display_summary}</div>
                </div>
                <div style={{ display: "flex", flexDirection: "column", alignItems: "flex-end", gap: 8 }}>
                  <span className={`status ${c.status}`}>{t(lang, STATUS_LABEL_KEY[c.status])}</span>
                  {c.status === "assigned" && (
                    <div style={{ display: "flex", gap: 6 }}>
                      <button className="btn btn-ghost btn-sm" onClick={() => reject(c.id)} disabled={actingId === c.id}>
                        {actingId === c.id ? t(lang, "worker.rejecting") : t(lang, "worker.reject")}
                      </button>
                      <button className="btn btn-primary btn-sm" onClick={() => accept(c.id)} disabled={actingId === c.id}>
                        {actingId === c.id ? t(lang, "worker.accepting") : t(lang, "worker.accept")}
                      </button>
                    </div>
                  )}
                  {c.status === "accepted" && (
                    <button className="btn btn-primary btn-sm" onClick={() => resolve(c.id)} disabled={actingId === c.id}>
                      {actingId === c.id ? "…" : t(lang, "worker.markResolved")}
                    </button>
                  )}
                </div>
              </div>
              {c.photo_path && (
                <img src={api.photoUrl(c.photo_path)} alt={t(lang, "worker.attached")} style={{ marginTop: 10, maxWidth: 160, borderRadius: 8, border: "1px solid var(--line)" }} />
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

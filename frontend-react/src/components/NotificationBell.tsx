import { useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../lib/auth";
import { useUiLang } from "../lib/uiLang";
import { t } from "../lib/i18n";
import { api, ApiError, type AppNotification } from "../lib/api";

// Polling interval for the unread badge -- this app has no websockets/SSE (see
// CitizenDashboard's own LIVE_POLL_MS precedent), so a short poll keeps "New complaint
// assigned" showing up without the worker needing to open the panel first.
const POLL_MS = 15000;

/** Notification bell + dropdown panel -- shown for workers (assignment/update notifications) and
 * admins (AI-monitoring alerts, see AppNotification's docstring in lib/api.ts). Clicking a
 * notification that's about a specific complaint opens it (never a dead end); an AI_ALERT has no
 * complaint_id, so clicking one just marks it read and closes the panel. Opening the panel itself
 * never marks anything read (see this phase's spec). */
export default function NotificationBell() {
  const { token, user } = useAuth();
  const { lang } = useUiLang();
  const navigate = useNavigate();
  const [open, setOpen] = useState(false);
  const [notifications, setNotifications] = useState<AppNotification[]>([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  async function load() {
    if (!token) return;
    setLoading(true);
    setError(null);
    try {
      const data = await api.listNotifications(token);
      setNotifications(data.notifications);
      setUnreadCount(data.unread_count);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : t(lang, "notifications.errLoadFailed"));
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
    const interval = setInterval(load, POLL_MS);
    return () => clearInterval(interval);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token]);

  useEffect(() => {
    function handleClickOutside(e: MouseEvent) {
      if (containerRef.current && !containerRef.current.contains(e.target as Node)) setOpen(false);
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  async function handleSelect(n: AppNotification) {
    setOpen(false);
    if (!n.read_at && token) {
      try {
        await api.markNotificationRead(token, n.id);
        setNotifications((prev) => prev.map((x) => (x.id === n.id ? { ...x, read_at: new Date().toISOString() } : x)));
        setUnreadCount((c) => Math.max(0, c - 1));
      } catch {
        /* best-effort -- navigation still proceeds even if marking read failed */
      }
    }
    // Role-aware -- a citizen's own complaint notifications (COMPLAINT_ACCEPTED/STARTED/
    // RESOLVED, see backend/routes/complaints.py) must open their own detail page, an admin's
    // (none carry a complaint_id today -- AI_ALERT doesn't) would open the admin's read-only
    // detail page (see AdminComplaintDetail.tsx), and everyone else falls back to the worker
    // route rather than silently doing nothing.
    if (n.complaint_id) {
      const base = user?.role === "citizen" ? "citizen" : user?.role === "admin" ? "admin" : "worker";
      navigate(`/${base}/complaints/${n.complaint_id}`);
    }
  }

  return (
    <div ref={containerRef} style={{ position: "relative" }}>
      <button
        type="button"
        className="icon-btn"
        aria-label={t(lang, "notifications.bellAria")}
        onClick={() => setOpen((o) => !o)}
        style={{ position: "relative" }}
      >
        <svg width="17" height="17" viewBox="0 0 24 24" fill="none">
          <path
            d="M6 10a6 6 0 1 1 12 0v4.5l1.6 2.4a1 1 0 0 1-.8 1.6H5.2a1 1 0 0 1-.8-1.6L6 14.5V10Z"
            stroke="currentColor"
            strokeWidth="1.6"
            strokeLinejoin="round"
          />
          <path d="M9.5 20a2.5 2.5 0 0 0 5 0" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" />
        </svg>
        {unreadCount > 0 && <span className="notif-badge">{unreadCount > 9 ? "9+" : unreadCount}</span>}
      </button>

      {open && (
        <div className="notif-panel">
          <div className="notif-panel-head">{t(lang, "notifications.title")}</div>
          {error && <div className="banner-error" style={{ margin: 10 }}>{error}</div>}
          {loading && notifications.length === 0 && <div className="notif-empty">{t(lang, "common.loading")}</div>}
          {!loading && notifications.length === 0 && !error && <div className="notif-empty">{t(lang, "notifications.empty")}</div>}
          {notifications.map((n) => (
            <button key={n.id} type="button" className={`notif-item${n.read_at ? "" : " unread"}`} onClick={() => handleSelect(n)}>
              <div className="notif-item-title">{n.title}</div>
              <div className="notif-item-message">{n.message}</div>
              <div className="notif-item-meta">{new Date(n.created_at).toLocaleString()}</div>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}

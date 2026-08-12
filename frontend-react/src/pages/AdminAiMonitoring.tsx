import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import TopBar from "../components/TopBar";
import { useAuth } from "../lib/auth";
import { useUiLang } from "../lib/uiLang";
import { t } from "../lib/i18n";
import { api, ApiError, type AiMonitoringSummary, type AiRequestLogEntry } from "../lib/api";
import "../styles/dashboard.css";

/** Its own page (not a section of AdminDashboard) so the worker-management view and the AI
 * observability view don't compete for space/scroll -- reached via the "AI Monitoring" button on
 * AdminDashboard. See docs/ask_janmitra_langsmith_observability.md for what's shown here and
 * where the numbers come from (the app's own `ai_request_logs` table, never a live LangSmith
 * call -- see that doc's "Admin Monitoring" section for why). */
export default function AdminAiMonitoring() {
  const { token } = useAuth();
  const { lang } = useUiLang();

  const [summary, setSummary] = useState<AiMonitoringSummary | null>(null);
  const [requests, setRequests] = useState<AiRequestLogEntry[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  async function load() {
    if (!token) return;
    setLoading(true);
    setError(null);
    try {
      const [summaryResult, requestsResult] = await Promise.all([
        api.aiMonitoringSummary(token),
        api.aiMonitoringRequests(token, 20),
      ]);
      setSummary(summaryResult);
      setRequests(requestsResult);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : t(lang, "admin.aiErrLoadFailed"));
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token]);

  return (
    <div>
      <TopBar />
      <div className="page-admin">
        <div className="page-head">
          <div>
            <Link to="/admin" style={{ fontSize: 12.5, color: "var(--ink-2)", display: "inline-block", marginBottom: 8 }}>
              {t(lang, "admin.backToDashboard")}
            </Link>
            <h1 className="page-title display">{t(lang, "admin.aiSection")}</h1>
            <p className="page-sub">{t(lang, "admin.aiSubtitle")}</p>
          </div>
        </div>

        {error && <div className="banner-error">{error}</div>}
        {loading && (
          <div className="surface-card" style={{ padding: 18 }}>
            {[0, 1].map((i) => (
              <div key={i} className="skeleton" style={{ width: "100%", height: 18, marginBottom: i < 1 ? 14 : 0 }} />
            ))}
          </div>
        )}

        {!loading && summary && (
          <>
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(150px, 1fr))", gap: 12, marginBottom: 12 }}>
              <div className="surface-card hoverable stat-card">
                <div className="stat-label">{t(lang, "admin.aiTotalRequests")}</div>
                <div className="display stat-value">{summary.total_requests}</div>
              </div>
              <div className="surface-card hoverable stat-card">
                <div className="stat-label">{t(lang, "admin.aiSuccessful")}</div>
                <div className="display stat-value" style={{ color: "var(--status-resolved)" }}>{summary.successful_requests}</div>
              </div>
              <div className="surface-card hoverable stat-card">
                <div className="stat-label">{t(lang, "admin.aiFailed")}</div>
                <div className="display stat-value" style={{ color: "var(--status-critical)" }}>{summary.failed_requests}</div>
              </div>
              <div className="surface-card hoverable stat-card">
                <div className="stat-label">{t(lang, "admin.aiErrorRate")}</div>
                <div className="display stat-value">{(summary.error_rate * 100).toFixed(1)}%</div>
              </div>
              <div className="surface-card hoverable stat-card">
                <div className="stat-label">{t(lang, "admin.aiAvgLatency")}</div>
                <div className="display stat-value">{Math.round(summary.average_latency_ms)}ms</div>
              </div>
            </div>

            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(120px, 1fr))", gap: 10, marginBottom: 30 }}>
              {[
                [t(lang, "admin.aiRag"), summary.rag_requests],
                [t(lang, "admin.aiComplaints"), summary.complaint_requests],
                [t(lang, "admin.aiStatus"), summary.status_requests],
                [t(lang, "admin.aiOutOfScope"), summary.out_of_scope_requests],
                [t(lang, "admin.aiClarification"), summary.clarification_requests],
              ].map(([label, value]) => (
                <div key={label as string} className="surface-card" style={{ padding: "10px 14px" }}>
                  <div style={{ fontSize: 10.5, color: "var(--ink-2)", textTransform: "uppercase", fontWeight: 700 }}>{label}</div>
                  <div className="mono" style={{ fontSize: 18, marginTop: 4 }}>{value}</div>
                </div>
              ))}
            </div>
          </>
        )}

        <div className="section-label">
          <span>{t(lang, "admin.aiRecentRequests")}</span>
        </div>

        {!loading && requests.length === 0 && <p style={{ color: "var(--ink-2)" }}>{t(lang, "admin.aiEmpty")}</p>}

        {!loading && requests.length > 0 && (
          <div className="surface-card" style={{ overflowX: "auto" }}>
            <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 13, minWidth: 640 }}>
              <thead>
                <tr>
                  {[
                    t(lang, "admin.aiColTime"),
                    t(lang, "admin.aiColRoute"),
                    t(lang, "admin.aiColIntent"),
                    t(lang, "admin.aiColLatency"),
                    t(lang, "admin.aiColStatus"),
                    t(lang, "admin.aiColTrace"),
                  ].map((h) => (
                    <th key={h} style={{ textAlign: "left", fontSize: 10.5, textTransform: "uppercase", color: "var(--ink-3)", fontWeight: 700, padding: "12px 16px", borderBottom: "1px solid var(--line)" }}>
                      {h}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {requests.map((r, i) => (
                  <tr key={r.id} className="table-row-hover enter" style={{ "--stagger": Math.min(i, 6) } as React.CSSProperties}>
                    <td style={{ padding: "12px 16px", borderBottom: "1px solid var(--line)", color: "var(--ink-2)" }}>
                      {new Date(r.created_at).toLocaleString()}
                    </td>
                    <td className="mono" style={{ padding: "12px 16px", borderBottom: "1px solid var(--line)" }}>{r.routed_to}</td>
                    <td style={{ padding: "12px 16px", borderBottom: "1px solid var(--line)", color: "var(--ink-2)" }}>{r.intent ?? "—"}</td>
                    <td className="mono" style={{ padding: "12px 16px", borderBottom: "1px solid var(--line)" }}>{Math.round(r.latency_ms)}ms</td>
                    <td style={{ padding: "12px 16px", borderBottom: "1px solid var(--line)", color: r.success ? "var(--status-resolved)" : "var(--status-critical)" }}>
                      {r.success ? t(lang, "admin.aiStatusOk") : t(lang, "admin.aiStatusFailed")}
                    </td>
                    <td style={{ padding: "12px 16px", borderBottom: "1px solid var(--line)" }}>
                      {r.trace_url ? (
                        <a href={r.trace_url} target="_blank" rel="noopener noreferrer">
                          {t(lang, "admin.aiViewTrace")}
                        </a>
                      ) : (
                        <span style={{ color: "var(--ink-3)" }}>{t(lang, "admin.aiNoTraceLink")}</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}

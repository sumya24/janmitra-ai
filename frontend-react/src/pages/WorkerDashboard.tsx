import { useEffect, useState } from "react";
import TopBar from "../components/TopBar";
import { useAuth } from "../lib/auth";
import { SUPPORTED_LANGUAGES, type LangCode } from "../lib/i18n";
import { api, ApiError, type Complaint } from "../lib/api";

export default function WorkerDashboard() {
  const { user, token } = useAuth();
  const [viewLang, setViewLang] = useState<LangCode>((user?.preferred_language as LangCode) || "en");
  const [complaints, setComplaints] = useState<Complaint[]>([]);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [actionError, setActionError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [resolvingId, setResolvingId] = useState<number | null>(null);
  const [filter, setFilter] = useState<"all" | "open" | "resolved">("open");

  async function load() {
    if (!token) return;
    setLoading(true);
    setLoadError(null);
    try {
      setComplaints(await api.listComplaints(token, viewLang));
    } catch (err) {
      setLoadError(err instanceof ApiError ? err.message : "Could not load your queue.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token, viewLang]);

  async function resolve(id: number) {
    if (!token) return;
    setActionError(null);
    setResolvingId(id);
    try {
      await api.updateComplaintStatus(token, id, "resolved");
      await load();
    } catch (err) {
      setActionError(err instanceof ApiError ? err.message : "Could not update this complaint.");
    } finally {
      setResolvingId(null);
    }
  }

  const openCount = complaints.filter((c) => c.status === "open").length;
  const resolvedCount = complaints.filter((c) => c.status === "resolved").length;
  const visible = complaints.filter((c) => filter === "all" || c.status === filter);

  return (
    <div>
      <TopBar />
      <div className="page">
        <div className="page-head">
          <div>
            <h1 className="page-title display">Your queue</h1>
            <p className="page-sub">{user?.ward ? `Ward: ${user.ward}` : "No ward assigned yet"}</p>
          </div>
          <div className="langpills">
            {(Object.keys(SUPPORTED_LANGUAGES) as LangCode[]).map((code) => (
              <button key={code} className={`langpill ${viewLang === code ? "active" : ""}`} onClick={() => setViewLang(code)}>
                {SUPPORTED_LANGUAGES[code].name}
              </button>
            ))}
          </div>
        </div>

        <div style={{ display: "flex", gap: 10, marginBottom: 20 }}>
          <div style={{ background: "var(--surface)", border: "1px solid var(--line)", borderRadius: 10, padding: "10px 16px", flex: 1 }}>
            <div className="display" style={{ fontSize: 26, color: "var(--status-open)" }}>{openCount}</div>
            <div style={{ fontSize: 11, color: "var(--ink-2)" }}>Open</div>
          </div>
          <div style={{ background: "var(--surface)", border: "1px solid var(--line)", borderRadius: 10, padding: "10px 16px", flex: 1 }}>
            <div className="display" style={{ fontSize: 26, color: "var(--status-resolved)" }}>{resolvedCount}</div>
            <div style={{ fontSize: 11, color: "var(--ink-2)" }}>Resolved</div>
          </div>
        </div>

        <div style={{ display: "flex", gap: 6, marginBottom: 16 }}>
          {(["all", "open", "resolved"] as const).map((f) => (
            <button
              key={f}
              onClick={() => setFilter(f)}
              style={{
                background: filter === f ? "var(--ink)" : "var(--surface)",
                color: filter === f ? "var(--paper)" : "var(--ink-2)",
                border: "1px solid var(--line)", borderRadius: 20, padding: "7px 14px", fontSize: 12.5, fontWeight: 600,
              }}
            >
              {f === "all" ? "All" : f === "open" ? "Open" : "Resolved"}
            </button>
          ))}
        </div>

        {loadError && <div className="banner-error">{loadError}</div>}
        {actionError && <div className="banner-error">{actionError}</div>}
        {loading && <p style={{ color: "var(--ink-2)" }}>Loading…</p>}
        {!loading && visible.length === 0 && <p style={{ color: "var(--ink-2)" }}>Nothing here.</p>}

        <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
          {visible.map((c) => (
            <div key={c.id} style={{ background: "var(--surface)", border: "1px solid var(--line)", borderRadius: 12, padding: "14px 16px" }}>
              <div style={{ display: "flex", justifyContent: "space-between", gap: 16, flexWrap: "wrap" }}>
                <div>
                  <div className="mono" style={{ fontSize: 11, color: "var(--ink-3)" }}>JM-{String(c.id).padStart(5, "0")}</div>
                  <div style={{ fontWeight: 600, margin: "3px 0" }}>{c.display_text}</div>
                  <div style={{ fontSize: 12, color: "var(--ink-2)" }}>{c.summary}</div>
                </div>
                <div style={{ display: "flex", flexDirection: "column", alignItems: "flex-end", gap: 8 }}>
                  <span className={`status ${c.status}`}>{c.status === "resolved" ? "Resolved" : "Open"}</span>
                  {c.status === "open" && (
                    <button className="btn btn-primary btn-sm" onClick={() => resolve(c.id)} disabled={resolvingId === c.id}>
                      {resolvingId === c.id ? "…" : "Mark Resolved"}
                    </button>
                  )}
                </div>
              </div>
              {c.photo_path && (
                <img src={api.photoUrl(c.photo_path)} alt="Attached" style={{ marginTop: 10, maxWidth: 160, borderRadius: 8, border: "1px solid var(--line)" }} />
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

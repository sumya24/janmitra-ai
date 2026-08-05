import { useEffect, useState } from "react";
import TopBar from "../components/TopBar";
import AddWorkerModal from "../components/AddWorkerModal";
import { useAuth } from "../lib/auth";
import { api, ApiError, type WorkerSummary } from "../lib/api";

export default function AdminDashboard() {
  const { token } = useAuth();
  const [workers, setWorkers] = useState<WorkerSummary[]>([]);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [showAddWorker, setShowAddWorker] = useState(false);

  async function load() {
    if (!token) return;
    setLoading(true);
    setLoadError(null);
    try {
      setWorkers(await api.listWorkers(token));
    } catch (err) {
      setLoadError(err instanceof ApiError ? err.message : "Could not load workers.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token]);

  const totalOpen = workers.reduce((sum, w) => sum + w.open_complaints, 0);
  const totalResolved = workers.reduce((sum, w) => sum + w.resolved_complaints, 0);

  return (
    <div>
      <TopBar />
      <div className="page">
        <div className="page-head">
          <div>
            <h1 className="page-title display">Municipal Oversight</h1>
            <p className="page-sub">All wards</p>
          </div>
        </div>

        <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 12, marginBottom: 30 }}>
          <div style={{ background: "var(--surface)", border: "1px solid var(--line)", borderRadius: 12, padding: "16px 18px" }}>
            <div style={{ fontSize: 11, color: "var(--ink-2)", textTransform: "uppercase", fontWeight: 700 }}>Workers</div>
            <div className="display" style={{ fontSize: 32, marginTop: 8 }}>{workers.length}</div>
          </div>
          <div style={{ background: "var(--surface)", border: "1px solid var(--line)", borderRadius: 12, padding: "16px 18px" }}>
            <div style={{ fontSize: 11, color: "var(--ink-2)", textTransform: "uppercase", fontWeight: 700 }}>Open complaints</div>
            <div className="display" style={{ fontSize: 32, marginTop: 8, color: "var(--status-open)" }}>{totalOpen}</div>
          </div>
          <div style={{ background: "var(--surface)", border: "1px solid var(--line)", borderRadius: 12, padding: "16px 18px" }}>
            <div style={{ fontSize: 11, color: "var(--ink-2)", textTransform: "uppercase", fontWeight: 700 }}>Resolved</div>
            <div className="display" style={{ fontSize: 32, marginTop: 8, color: "var(--status-resolved)" }}>{totalResolved}</div>
          </div>
        </div>

        <div className="section-label" style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <span>Workers</span>
          <button className="btn btn-primary btn-sm" onClick={() => setShowAddWorker(true)}>
            + Add worker
          </button>
        </div>
        <p style={{ fontSize: 12, color: "var(--ink-2)", marginTop: -4, marginBottom: 12 }}>
          Worker accounts can only be created here by a Super Admin — there's no public sign-up for workers.
        </p>

        {loadError && <div className="banner-error">{loadError}</div>}
        {loading && <p style={{ color: "var(--ink-2)" }}>Loading…</p>}
        {!loading && workers.length === 0 && <p style={{ color: "var(--ink-2)" }}>No workers yet — add the first one.</p>}

        {!loading && workers.length > 0 && (
          <div style={{ overflowX: "auto", border: "1px solid var(--line)", borderRadius: 12, background: "var(--surface)" }}>
            <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 13, minWidth: 480 }}>
              <thead>
                <tr>
                  {["Worker", "Ward", "Open", "Resolved", "Language"].map((h) => (
                    <th key={h} style={{ textAlign: "left", fontSize: 10.5, textTransform: "uppercase", color: "var(--ink-3)", fontWeight: 700, padding: "12px 16px", borderBottom: "1px solid var(--line)" }}>
                      {h}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {workers.map((w) => (
                  <tr key={w.id}>
                    <td style={{ padding: "12px 16px", borderBottom: "1px solid var(--line)", fontWeight: 700 }}>{w.full_name}</td>
                    <td style={{ padding: "12px 16px", borderBottom: "1px solid var(--line)", color: "var(--ink-2)" }}>{w.ward}</td>
                    <td className="mono" style={{ padding: "12px 16px", borderBottom: "1px solid var(--line)" }}>{w.open_complaints}</td>
                    <td className="mono" style={{ padding: "12px 16px", borderBottom: "1px solid var(--line)" }}>{w.resolved_complaints}</td>
                    <td style={{ padding: "12px 16px", borderBottom: "1px solid var(--line)", color: "var(--ink-2)" }}>{w.preferred_language}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {showAddWorker && (
        <AddWorkerModal
          onClose={() => setShowAddWorker(false)}
          onCreated={load}
        />
      )}
    </div>
  );
}

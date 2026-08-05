import { useEffect, useState, type FormEvent } from "react";
import TopBar from "../components/TopBar";
import { useAuth } from "../lib/auth";
import { SUPPORTED_LANGUAGES, type LangCode } from "../lib/i18n";
import { api, ApiError, type Complaint } from "../lib/api";

export default function CitizenDashboard() {
  const { user, token } = useAuth();
  const [viewLang, setViewLang] = useState<LangCode>((user?.preferred_language as LangCode) || "en");
  const [complaints, setComplaints] = useState<Complaint[]>([]);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  const [language, setLanguage] = useState<LangCode>((user?.preferred_language as LangCode) || "en");
  const [text, setText] = useState("");
  const [ward, setWard] = useState("");
  const [photo, setPhoto] = useState<File | null>(null);
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [submitSuccess, setSubmitSuccess] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  async function loadComplaints() {
    if (!token) return;
    setLoading(true);
    setLoadError(null);
    try {
      const data = await api.listComplaints(token, viewLang);
      setComplaints(data);
    } catch (err) {
      setLoadError(err instanceof ApiError ? err.message : "Could not load your complaints.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadComplaints();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token, viewLang]);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setSubmitError(null);
    setSubmitSuccess(false);
    if (!text.trim()) {
      setSubmitError("Please describe the problem before submitting.");
      return;
    }
    if (!token) return;

    const form = new FormData();
    form.append("language", language);
    form.append("text", text.trim());
    if (ward.trim()) form.append("ward", ward.trim());
    if (photo) form.append("photo", photo);

    setSubmitting(true);
    try {
      await api.createComplaint(token, form);
      setText("");
      setWard("");
      setPhoto(null);
      setSubmitSuccess(true);
      await loadComplaints();
    } catch (err) {
      setSubmitError(err instanceof ApiError ? err.message : "Could not submit complaint. Please try again.");
    } finally {
      setSubmitting(false);
    }
  }

  const openCount = complaints.filter((c) => c.status === "open").length;
  const resolvedCount = complaints.filter((c) => c.status === "resolved").length;

  return (
    <div>
      <TopBar />
      <div className="page">
        <div className="page-head">
          <div>
            <h1 className="page-title display">Report a problem</h1>
            <p className="page-sub">Speak or type in your own language — we'll take it from there.</p>
          </div>
        </div>

        {submitError && <div className="banner-error">{submitError}</div>}
        {submitSuccess && (
          <div style={{ background: "var(--status-resolved-bg)", color: "var(--status-resolved)", borderRadius: 8, padding: "10px 14px", fontSize: 13, marginBottom: 14 }}>
            Complaint submitted successfully.
          </div>
        )}

        <form onSubmit={handleSubmit} style={{ background: "var(--surface)", border: "1px solid var(--line)", borderRadius: 12, padding: 20, marginBottom: 30 }}>
          <div className="field">
            <label htmlFor="complaint-language">Language</label>
            <select id="complaint-language" value={language} onChange={(e) => setLanguage(e.target.value as LangCode)}>
              {(Object.keys(SUPPORTED_LANGUAGES) as LangCode[]).map((code) => (
                <option key={code} value={code}>
                  {SUPPORTED_LANGUAGES[code].name}
                </option>
              ))}
            </select>
          </div>
          <div className="field">
            <label htmlFor="complaint-text">Describe the problem</label>
            <textarea id="complaint-text" rows={3} value={text} onChange={(e) => setText(e.target.value)} placeholder="e.g. Garbage not collected near my house for 3 days" />
          </div>
          <div className="field">
            <label htmlFor="complaint-ward">Area / ward (optional)</label>
            <input id="complaint-ward" type="text" value={ward} onChange={(e) => setWard(e.target.value)} placeholder="e.g. Ward 14 — Rukadi Road" />
          </div>
          <div className="field">
            <label htmlFor="complaint-photo">Attach a photo (optional)</label>
            <input id="complaint-photo" type="file" accept="image/jpeg,image/png" onChange={(e) => setPhoto(e.target.files?.[0] ?? null)} />
          </div>
          <button type="submit" className="btn btn-primary" disabled={submitting}>
            {submitting ? "Submitting…" : "Submit complaint"}
          </button>
        </form>

        <div className="statstrip" style={{ display: "flex", gap: 10, marginBottom: 26 }}>
          <div className="statchip" style={{ background: "var(--surface)", border: "1px solid var(--line)", borderRadius: 10, padding: "10px 16px", flex: 1 }}>
            <div className="display" style={{ fontSize: 26, color: "var(--status-open)" }}>{openCount}</div>
            <div style={{ fontSize: 11, color: "var(--ink-2)" }}>Open</div>
          </div>
          <div className="statchip" style={{ background: "var(--surface)", border: "1px solid var(--line)", borderRadius: 10, padding: "10px 16px", flex: 1 }}>
            <div className="display" style={{ fontSize: 26, color: "var(--status-resolved)" }}>{resolvedCount}</div>
            <div style={{ fontSize: 11, color: "var(--ink-2)" }}>Resolved</div>
          </div>
        </div>

        <div className="section-label" style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <span>Your complaints</span>
          <div className="langpills">
            {(Object.keys(SUPPORTED_LANGUAGES) as LangCode[]).map((code) => (
              <button key={code} className={`langpill ${viewLang === code ? "active" : ""}`} onClick={() => setViewLang(code)}>
                {SUPPORTED_LANGUAGES[code].name}
              </button>
            ))}
          </div>
        </div>

        {loadError && <div className="banner-error">{loadError}</div>}
        {loading && <p style={{ color: "var(--ink-2)" }}>Loading…</p>}
        {!loading && complaints.length === 0 && <p style={{ color: "var(--ink-2)" }}>You haven't submitted any complaints yet.</p>}

        <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
          {complaints.map((c) => (
            <div key={c.id} style={{ background: "var(--surface)", border: "1px solid var(--line)", borderRadius: 12, padding: "14px 16px" }}>
              <div style={{ display: "flex", justifyContent: "space-between", gap: 12, flexWrap: "wrap" }}>
                <div>
                  <div className="mono" style={{ fontSize: 11, color: "var(--ink-3)" }}>JM-{String(c.id).padStart(5, "0")}</div>
                  <div style={{ fontWeight: 600, margin: "3px 0" }}>{c.display_text}</div>
                  <div style={{ fontSize: 12, color: "var(--ink-2)" }}>{c.summary}</div>
                </div>
                <div style={{ textAlign: "right" }}>
                  <span className={`status ${c.status}`}>{c.status === "resolved" ? "Resolved" : "Open"}</span>
                  <div style={{ fontSize: 11, color: "var(--ink-3)", marginTop: 6 }}>{new Date(c.created_at).toLocaleString()}</div>
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

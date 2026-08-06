import { useEffect, useState, type FormEvent } from "react";
import TopBar from "../components/TopBar";
import { useAuth } from "../lib/auth";
import { SUPPORTED_LANGUAGES, type LangCode } from "../lib/i18n";
import { api, ApiError, type Complaint } from "../lib/api";
import { useAudioRecorder } from "../lib/useAudioRecorder";

export default function CitizenDashboard() {
  const { user, token } = useAuth();
  const [viewLang, setViewLang] = useState<LangCode>((user?.preferred_language as LangCode) || "en");
  const [complaints, setComplaints] = useState<Complaint[]>([]);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  const [inputMode, setInputMode] = useState<"text" | "voice">("text");
  const [language, setLanguage] = useState<LangCode>((user?.preferred_language as LangCode) || "en");
  const [text, setText] = useState("");
  const [ward, setWard] = useState("");
  const [wards, setWards] = useState<string[]>([]);
  const [photo, setPhoto] = useState<File | null>(null);
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [submitSuccess, setSubmitSuccess] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const recorder = useAudioRecorder();

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

  useEffect(() => {
    if (!token) return;
    // Populate the ward dropdown from real ward names (i.e. wards that actually
    // have a worker assigned) so a citizen can never type a typo or a ward that
    // doesn't route anywhere.
    api.listWards(token).then(setWards).catch(() => setWards([]));
  }, [token]);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setSubmitError(null);
    setSubmitSuccess(false);

    if (inputMode === "text" && !text.trim()) {
      setSubmitError("Please describe the problem before submitting.");
      return;
    }
    if (inputMode === "voice" && !recorder.audioBlob) {
      setSubmitError("Please record your complaint before submitting.");
      return;
    }
    // Only enforce a ward choice when there are real wards to choose from — if
    // none are set up yet, don't block a citizen from reporting a problem at all.
    if (wards.length > 0 && !ward) {
      setSubmitError("Please select the area so your complaint reaches the right team.");
      return;
    }
    if (!token) return;

    const form = new FormData();
    form.append("language", language);
    if (inputMode === "text") {
      form.append("text", text.trim());
    } else if (recorder.audioBlob) {
      const extension = recorder.audioBlob.type.includes("mp4") ? "m4a" : recorder.audioBlob.type.includes("ogg") ? "ogg" : "webm";
      form.append("audio", recorder.audioBlob, `complaint.${extension}`);
    }
    if (ward.trim()) form.append("ward", ward.trim());
    if (photo) form.append("photo", photo);

    setSubmitting(true);
    try {
      await api.createComplaint(token, form);
      setText("");
      setWard("");
      setPhoto(null);
      recorder.reset();
      setSubmitSuccess(true);
      await loadComplaints();
    } catch (err) {
      setSubmitError(err instanceof ApiError ? err.message : "Could not submit complaint. Please try again.");
    } finally {
      setSubmitting(false);
    }
  }

  function formatSeconds(total: number): string {
    const m = Math.floor(total / 60);
    const s = total % 60;
    return `${m}:${String(s).padStart(2, "0")}`;
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
            <label>Describe the problem</label>
            <div className="langpills" style={{ marginBottom: 10 }}>
              <button
                type="button"
                className={`langpill ${inputMode === "text" ? "active" : ""}`}
                onClick={() => setInputMode("text")}
              >
                ✏️ Type
              </button>
              <button
                type="button"
                className={`langpill ${inputMode === "voice" ? "active" : ""}`}
                onClick={() => setInputMode("voice")}
              >
                🎙️ Speak
              </button>
            </div>

            {inputMode === "text" && (
              <textarea
                id="complaint-text"
                rows={3}
                value={text}
                onChange={(e) => setText(e.target.value)}
                placeholder="e.g. Garbage not collected near my house for 3 days"
              />
            )}

            {inputMode === "voice" && (
              <div style={{ border: "1px solid var(--line)", borderRadius: 10, padding: 14, background: "var(--paper)" }}>
                {recorder.error && <div className="banner-error" style={{ marginBottom: 10 }}>{recorder.error}</div>}

                {!recorder.isRecording && !recorder.audioUrl && (
                  <button type="button" className="btn btn-primary btn-sm" onClick={recorder.start}>
                    🎙️ Start recording
                  </button>
                )}

                {recorder.isRecording && (
                  <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
                    <span
                      style={{
                        width: 10,
                        height: 10,
                        borderRadius: "50%",
                        background: "var(--status-critical)",
                        display: "inline-block",
                      }}
                    />
                    <span className="mono" style={{ fontSize: 13 }}>{formatSeconds(recorder.seconds)}</span>
                    <button type="button" className="btn btn-primary btn-sm" onClick={recorder.stop}>
                      ⏹ Stop
                    </button>
                  </div>
                )}

                {!recorder.isRecording && recorder.audioUrl && (
                  <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
                    <audio controls src={recorder.audioUrl} style={{ width: "100%" }} />
                    <div>
                      <button type="button" className="btn btn-ghost btn-sm" onClick={recorder.reset}>
                        🔁 Record again
                      </button>
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>

          <div className="field">
            <label htmlFor="complaint-ward">Area / ward{wards.length === 0 ? " (optional)" : ""}</label>
            {wards.length > 0 ? (
              <>
                <select id="complaint-ward" value={ward} onChange={(e) => setWard(e.target.value)} required>
                  <option value="" disabled>
                    Select the area
                  </option>
                  {wards.map((w) => (
                    <option key={w} value={w}>
                      {w}
                    </option>
                  ))}
                </select>
                <p style={{ fontSize: 11, color: "var(--ink-2)", marginTop: 4 }}>
                  This determines which team's queue your complaint lands in.
                </p>
              </>
            ) : (
              <>
                <input id="complaint-ward" type="text" value={ward} onChange={(e) => setWard(e.target.value)} placeholder="e.g. Ward 14 — Rukadi Road" />
                <p style={{ fontSize: 11, color: "var(--ink-2)", marginTop: 4 }}>
                  No areas are set up yet, so this won't reach anyone's queue until an admin adds a worker for it.
                </p>
              </>
            )}
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

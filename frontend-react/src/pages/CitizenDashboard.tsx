import { useEffect, useState, type FormEvent } from "react";
import TopBar from "../components/TopBar";
import ComplaintTracker from "../components/ComplaintTracker";
import { useAuth } from "../lib/auth";
import { useUiLang } from "../lib/uiLang";
import { t } from "../lib/i18n";
import { api, ApiError, type Complaint } from "../lib/api";
import { useAudioRecorder } from "../lib/useAudioRecorder";

const STATUS_LABEL_KEY = {
  pending: "citizen.statusPending",
  assigned: "citizen.statusAssigned",
  accepted: "citizen.statusAccepted",
  resolved: "citizen.statusResolved",
} as const;

// Polling interval for "live" tracking updates (accept/reject/reassignment/resolve) while
// anything is still in flight — this app has no websockets/SSE, so a short poll is the fast,
// simple way to make status changes show up without the citizen having to manually refresh.
const LIVE_POLL_MS = 8000;

function FeedbackForm({
  complaintId,
  lang,
  token,
  onSubmitted,
}: {
  complaintId: number;
  lang: ReturnType<typeof useUiLang>["lang"];
  token: string;
  onSubmitted: () => void;
}) {
  const [rating, setRating] = useState(0);
  const [comment, setComment] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function submit() {
    if (rating < 1) return;
    setSubmitting(true);
    setError(null);
    try {
      await api.submitFeedback(token, complaintId, { rating, comment: comment.trim() || undefined });
      onSubmitted();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : t(lang, "citizen.errFeedbackFailed"));
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div style={{ marginTop: 10, paddingTop: 10, borderTop: "1px solid var(--line)" }}>
      <div style={{ fontSize: 12, fontWeight: 600, marginBottom: 6 }}>{t(lang, "citizen.feedbackTitle")}</div>
      {error && <div className="banner-error" style={{ marginBottom: 8 }}>{error}</div>}
      <div style={{ display: "flex", gap: 4, marginBottom: 8 }}>
        {[1, 2, 3, 4, 5].map((n) => (
          <button
            key={n}
            type="button"
            onClick={() => setRating(n)}
            aria-label={`${n}`}
            style={{
              background: "none", border: "none", cursor: "pointer", fontSize: 20, lineHeight: 1,
              color: n <= rating ? "var(--status-open)" : "var(--line)",
            }}
          >
            ★
          </button>
        ))}
      </div>
      <textarea
        rows={2}
        value={comment}
        onChange={(e) => setComment(e.target.value)}
        placeholder={t(lang, "citizen.feedbackCommentPlaceholder")}
        style={{ marginBottom: 8 }}
      />
      <button type="button" className="btn btn-primary btn-sm" onClick={submit} disabled={submitting || rating < 1}>
        {submitting ? t(lang, "citizen.feedbackSubmitting") : t(lang, "citizen.feedbackSubmit")}
      </button>
    </div>
  );
}

export default function CitizenDashboard() {
  const { token } = useAuth();
  // Single source of language for this whole page: the account's preferred language (kept in
  // sync with uiLang — see auth.tsx/SettingsModal). It drives both what language the complaint
  // list displays in *and* what language a new complaint is submitted as — no separate "what
  // language is this complaint in" picker; Settings is the one place to change either.
  const { lang } = useUiLang();
  const [complaints, setComplaints] = useState<Complaint[]>([]);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  const [inputMode, setInputMode] = useState<"text" | "voice">("text");
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
      setSubmitError(t(lang, "citizen.errNoText"));
      return;
    }
    if (inputMode === "voice" && recorder.audioSegments.length === 0) {
      setSubmitError(t(lang, "citizen.errNoAudio"));
      return;
    }
    // Only enforce a ward choice when there are real wards to choose from — if
    // none are set up yet, don't block a citizen from reporting a problem at all.
    if (wards.length > 0 && !ward) {
      setSubmitError(t(lang, "citizen.errNoWard"));
      return;
    }
    if (!token) return;

    const form = new FormData();
    form.append("language", lang);
    if (inputMode === "text") {
      form.append("text", text.trim());
    } else {
      // A long recording arrives as several ≤28s segments (see useAudioRecorder.ts) --
      // append every one under the same "audio" field name so the backend receives them
      // as a list and transcribes + stitches them back into one complaint.
      recorder.audioSegments.forEach((segment, i) => {
        const extension = segment.type.includes("mp4") ? "m4a" : segment.type.includes("ogg") ? "ogg" : "webm";
        form.append("audio", segment, `complaint_part${i + 1}.${extension}`);
      });
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
      setSubmitError(err instanceof ApiError ? err.message : t(lang, "citizen.errSubmitFailed"));
    } finally {
      setSubmitting(false);
    }
  }

  function formatSeconds(total: number): string {
    const m = Math.floor(total / 60);
    const s = total % 60;
    return `${m}:${String(s).padStart(2, "0")}`;
  }

  const openCount = complaints.filter((c) => c.status !== "resolved").length;
  const resolvedCount = complaints.filter((c) => c.status === "resolved").length;

  return (
    <div>
      <TopBar />
      <div className="page">
        <div className="page-head">
          <div>
            <h1 className="page-title display">{t(lang, "citizen.title")}</h1>
            <p className="page-sub">{t(lang, "citizen.subtitle")}</p>
          </div>
        </div>

        {submitError && <div className="banner-error">{submitError}</div>}
        {submitSuccess && (
          <div style={{ background: "var(--status-resolved-bg)", color: "var(--status-resolved)", borderRadius: 8, padding: "10px 14px", fontSize: 13, marginBottom: 14 }}>
            {t(lang, "citizen.submitSuccess")}
          </div>
        )}

        <form onSubmit={handleSubmit} noValidate style={{ background: "var(--surface)", border: "1px solid var(--line)", borderRadius: 12, padding: 20, marginBottom: 30 }}>
          <div className="field">
            <label>{t(lang, "citizen.describe")}</label>
            <div className="langpills" style={{ marginBottom: 10 }}>
              <button
                type="button"
                className={`langpill ${inputMode === "text" ? "active" : ""}`}
                onClick={() => setInputMode("text")}
              >
                {t(lang, "citizen.type")}
              </button>
              <button
                type="button"
                className={`langpill ${inputMode === "voice" ? "active" : ""}`}
                onClick={() => setInputMode("voice")}
              >
                {t(lang, "citizen.speak")}
              </button>
            </div>

            {inputMode === "text" && (
              <textarea
                id="complaint-text"
                rows={3}
                value={text}
                onChange={(e) => setText(e.target.value)}
                placeholder={t(lang, "citizen.textPlaceholder")}
              />
            )}

            {inputMode === "voice" && (
              <div style={{ border: "1px solid var(--line)", borderRadius: 10, padding: 14, background: "var(--paper)" }}>
                {recorder.error && <div className="banner-error" style={{ marginBottom: 10 }}>{recorder.error}</div>}

                {!recorder.isRecording && recorder.audioSegments.length === 0 && (
                  <button type="button" className="btn btn-primary btn-sm" onClick={recorder.start}>
                    {t(lang, "citizen.startRecording")}
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
                      {t(lang, "citizen.stopRecording")}
                    </button>
                  </div>
                )}

                {!recorder.isRecording && recorder.audioSegments.length > 0 && (
                  <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
                    {recorder.audioUrl ? (
                      <audio controls src={recorder.audioUrl} style={{ width: "100%" }} />
                    ) : (
                      // A recording long enough to span multiple segments doesn't get a
                      // gapless local preview (see useAudioRecorder.ts) -- it still submits
                      // and transcribes correctly, so just confirm the total length instead.
                      <div style={{ fontSize: 13 }}>
                        {t(lang, "citizen.voiceRecorded")} <span className="mono">{formatSeconds(recorder.seconds)}</span>
                      </div>
                    )}
                    <div>
                      <button type="button" className="btn btn-ghost btn-sm" onClick={recorder.reset}>
                        {t(lang, "citizen.recordAgain")}
                      </button>
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>

          <div className="field">
            <label htmlFor="complaint-ward">{wards.length === 0 ? t(lang, "citizen.wardOptional") : t(lang, "citizen.ward")}</label>
            {wards.length > 0 ? (
              <>
                <select id="complaint-ward" value={ward} onChange={(e) => setWard(e.target.value)} required>
                  <option value="" disabled>
                    {t(lang, "citizen.wardSelectPlaceholder")}
                  </option>
                  {wards.map((w) => (
                    <option key={w} value={w}>
                      {w}
                    </option>
                  ))}
                </select>
                <p style={{ fontSize: 11, color: "var(--ink-2)", marginTop: 4 }}>
                  {t(lang, "citizen.wardHelpHasWards")}
                </p>
              </>
            ) : (
              <>
                <input id="complaint-ward" type="text" value={ward} onChange={(e) => setWard(e.target.value)} placeholder={t(lang, "citizen.wardPlaceholder")} />
                <p style={{ fontSize: 11, color: "var(--ink-2)", marginTop: 4 }}>
                  {t(lang, "citizen.wardHelpNoWards")}
                </p>
              </>
            )}
          </div>
          <div className="field">
            <label htmlFor="complaint-photo">{t(lang, "citizen.photo")}</label>
            <input id="complaint-photo" type="file" accept="image/jpeg,image/png" onChange={(e) => setPhoto(e.target.files?.[0] ?? null)} />
          </div>
          <button type="submit" className="btn btn-primary" disabled={submitting}>
            {submitting ? t(lang, "citizen.submitting") : t(lang, "citizen.submit")}
          </button>
        </form>

        <div className="statstrip" style={{ display: "flex", gap: 10, marginBottom: 26 }}>
          <div className="statchip" style={{ background: "var(--surface)", border: "1px solid var(--line)", borderRadius: 10, padding: "10px 16px", flex: 1 }}>
            <div className="display" style={{ fontSize: 26, color: "var(--status-open)" }}>{openCount}</div>
            <div style={{ fontSize: 11, color: "var(--ink-2)" }}>{t(lang, "citizen.open")}</div>
          </div>
          <div className="statchip" style={{ background: "var(--surface)", border: "1px solid var(--line)", borderRadius: 10, padding: "10px 16px", flex: 1 }}>
            <div className="display" style={{ fontSize: 26, color: "var(--status-resolved)" }}>{resolvedCount}</div>
            <div style={{ fontSize: 11, color: "var(--ink-2)" }}>{t(lang, "citizen.resolved")}</div>
          </div>
        </div>

        <div className="section-label" style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <span>{t(lang, "citizen.yourComplaints")}</span>
        </div>

        {loadError && <div className="banner-error">{loadError}</div>}
        {loading && <p style={{ color: "var(--ink-2)" }}>{t(lang, "common.loading")}</p>}
        {!loading && complaints.length === 0 && <p style={{ color: "var(--ink-2)" }}>{t(lang, "citizen.noComplaints")}</p>}

        <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
          {complaints.map((c) => (
            <div key={c.id} style={{ background: "var(--surface)", border: "1px solid var(--line)", borderRadius: 12, padding: "14px 16px" }}>
              <div style={{ display: "flex", justifyContent: "space-between", gap: 12, flexWrap: "wrap" }}>
                <div>
                  <div className="mono" style={{ fontSize: 11, color: "var(--ink-3)" }}>JM-{String(c.id).padStart(5, "0")}</div>
                  <div style={{ fontWeight: 600, margin: "3px 0" }}>{c.display_text}</div>
                  <div style={{ fontSize: 12, color: "var(--ink-2)" }}>{c.display_summary}</div>
                </div>
                <div style={{ textAlign: "right" }}>
                  <span className={`status ${c.status}`}>{t(lang, STATUS_LABEL_KEY[c.status])}</span>
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
    </div>
  );
}

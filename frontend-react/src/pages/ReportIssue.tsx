import { useEffect, useState } from "react";
import { useNavigate, useSearchParams, Link } from "react-router-dom";
import TopBar from "../components/TopBar";
import MicWaveform from "../components/MicWaveform";
import MultiPhotoUpload from "../components/MultiPhotoUpload";
import LocationPicker, { type LocationValue } from "../components/LocationPicker";
import { useAuth } from "../lib/auth";
import { useUiLang } from "../lib/uiLang";
import { t } from "../lib/i18n";
import { api, ApiError, type Complaint } from "../lib/api";
import { useAudioRecorder } from "../lib/useAudioRecorder";
import { useToast } from "../lib/toast";
import { SERVICE_CATEGORY_DEFS, guessServiceCategory, type ServiceCategoryDef } from "../lib/serviceCategories";
import type { ServiceCategory } from "../lib/ragTypes";

type Step = "location" | "description" | "media" | "ai" | "preview";
const STEPS: Step[] = ["location", "description", "media", "ai", "preview"];

/**
 * Smart Complaint Creation wizard (P0, Task 2). Location -> Description -> Voice/Photo ->
 * AI Understanding (mock) -> Preview/Confirmation -> Submit -> Success.
 *
 * The only thing in this whole flow that is mock/dev data is the "AI Understanding" step's
 * service-category guess (see lib/serviceCategories.ts#guessServiceCategory) — a plain
 * client-side keyword match, clearly labeled as a development preview, never presented as a
 * real backend classification (the spec's AIServiceIdentification contract has a `confidence`
 * field for when a real model is wired in; this never fills it in with a fake number). Every
 * other piece of data here — ward, description, photo, and the complaint returned after submit
 * — is real, sent through the existing api.createComplaint exactly as CitizenDashboard already
 * did before this wizard replaced its inline form.
 */
export default function ReportIssue() {
  const { token } = useAuth();
  const { lang } = useUiLang();
  const [params] = useSearchParams();
  const navigate = useNavigate();
  const toast = useToast();
  const recorder = useAudioRecorder();

  const preselected = params.get("service") as ServiceCategory | null;

  const [step, setStep] = useState<Step>("location");
  const [location, setLocation] = useState<LocationValue>({ ward: "", coords: null });
  const [wards, setWards] = useState<string[]>([]);
  const [inputMode, setInputMode] = useState<"text" | "voice">("text");
  const [text, setText] = useState("");
  const [photos, setPhotos] = useState<File[]>([]);
  const [category, setCategory] = useState<ServiceCategoryDef | null>(
    SERVICE_CATEGORY_DEFS.find((d) => d.id === preselected) ?? null
  );
  const [aiRunning, setAiRunning] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [submitted, setSubmitted] = useState<Complaint | null>(null);

  useEffect(() => {
    if (!token) return;
    api.listWards(token).then(setWards).catch(() => setWards([]));
  }, [token]);

  const stepIndex = STEPS.indexOf(step);

  function goNext() {
    setError(null);
    if (step === "location" && wards.length > 0 && !location.ward) {
      setError(t(lang, "citizen.errNoWard"));
      return;
    }
    if (step === "description") {
      if (inputMode === "text" && !text.trim()) {
        setError(t(lang, "citizen.errNoText"));
        return;
      }
      if (inputMode === "voice" && recorder.audioSegments.length === 0) {
        setError(t(lang, "citizen.errNoAudio"));
        return;
      }
    }
    if (step === "media") {
      // Entering the AI step: run the mock classification once, briefly, so the loading state
      // reads as real work happening rather than an instant, suspicious-looking guess.
      setStep("ai");
      setAiRunning(true);
      window.setTimeout(() => {
        setCategory((prev) => prev ?? guessServiceCategory(text));
        setAiRunning(false);
      }, 900);
      return;
    }
    const next = STEPS[stepIndex + 1];
    if (next) setStep(next);
  }

  function goBack() {
    setError(null);
    const prev = STEPS[stepIndex - 1];
    if (prev) setStep(prev);
  }

  async function handleSubmit() {
    if (!token) return;
    setSubmitting(true);
    setError(null);
    const form = new FormData();
    form.append("language", lang);
    if (inputMode === "text") {
      form.append("text", text.trim());
    } else {
      recorder.audioSegments.forEach((segment, i) => {
        const extension = segment.type.includes("mp4") ? "m4a" : segment.type.includes("ogg") ? "ogg" : "webm";
        form.append("audio", segment, `complaint_part${i + 1}.${extension}`);
      });
    }
    if (location.ward.trim()) form.append("ward", location.ward.trim());
    // Sent whenever "use current location" succeeded, regardless of whether a ward was also
    // picked — the backend independently resolves/stores both (see routes/complaints.py).
    if (location.coords) {
      form.append("latitude", String(location.coords.lat));
      form.append("longitude", String(location.coords.lng));
      form.append("accuracy", String(location.coords.accuracy));
    }
    for (const photo of photos) form.append("photos", photo);

    try {
      const complaint = await api.createComplaint(token, form);
      setSubmitted(complaint);
      toast.success(t(lang, "citizen.submitSuccess"));
    } catch (err) {
      setError(err instanceof ApiError ? err.message : t(lang, "citizen.errSubmitFailed"));
    } finally {
      setSubmitting(false);
    }
  }

  function formatSeconds(total: number): string {
    const m = Math.floor(total / 60);
    const s = total % 60;
    return `${m}:${String(s).padStart(2, "0")}`;
  }

  if (submitted) {
    return (
      <div>
        <TopBar />
        <div className="page" id="main-content">
          <div className="surface-card wizard-panel enter" style={{ textAlign: "center", padding: "40px 24px" }}>
            <div className="success-icon" style={{ margin: "0 auto 16px", width: 56, height: 56, borderRadius: "50%", background: "var(--status-resolved-bg)", display: "flex", alignItems: "center", justifyContent: "center" }}>
              <svg width="28" height="28" viewBox="0 0 24 24" fill="none">
                <path d="M4 12.5 9.5 18 20 6" stroke="var(--status-resolved)" strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round" />
              </svg>
            </div>
            <h2 className="display" style={{ margin: "0 0 8px" }}>{t(lang, "wizard.success.title")}</h2>
            <p style={{ color: "var(--ink-2)", marginBottom: 6 }}>{t(lang, "wizard.success.body")}</p>
            <div className="mono" style={{ fontSize: 18, fontWeight: 700, margin: "16px 0 24px" }}>
              JM-{String(submitted.id).padStart(5, "0")}
            </div>
            <div style={{ display: "flex", gap: 10, justifyContent: "center", flexWrap: "wrap" }}>
              <Link to="/citizen/complaints" className="btn btn-primary">
                {t(lang, "wizard.success.track")}
              </Link>
              <Link to="/citizen" className="btn btn-ghost">
                {t(lang, "wizard.success.home")}
              </Link>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div>
      <TopBar />
      <div className="page" id="main-content">
        <div className="page-head">
          <div>
            <h1 className="page-title display">{t(lang, "wizard.title")}</h1>
            <p className="page-sub">{t(lang, "wizard.subtitle")}</p>
          </div>
        </div>

        <div className="wizard-steps" aria-hidden="true">
          {STEPS.map((s, i) => (
            <div key={s} className={`wizard-step-dot ${i < stepIndex ? "done" : i === stepIndex ? "active" : ""}`} />
          ))}
        </div>

        {error && <div className="banner-error">{error}</div>}

        <div className="surface-card wizard-panel enter">
          {step === "location" && (
            <>
              <h2>{t(lang, "wizard.location.title")}</h2>
              <p className="wizard-hint">{t(lang, "wizard.location.hint")}</p>
              <LocationPicker value={location} onChange={setLocation} wards={wards} />
            </>
          )}

          {step === "description" && (
            <>
              <h2>{t(lang, "wizard.description.title")}</h2>
              <p className="wizard-hint">{t(lang, "wizard.description.hint")}</p>
              <div className="langpills" style={{ marginBottom: 10 }}>
                <button type="button" className={`langpill ${inputMode === "text" ? "active" : ""}`} onClick={() => setInputMode("text")}>
                  {t(lang, "citizen.type")}
                </button>
                <button type="button" className={`langpill ${inputMode === "voice" ? "active" : ""}`} onClick={() => setInputMode("voice")}>
                  {t(lang, "citizen.speak")}
                </button>
              </div>
              {inputMode === "text" && (
                <>
                  <label htmlFor="complaint-text" className="sr-only">{t(lang, "citizen.describe")}</label>
                  <textarea id="complaint-text" rows={4} value={text} onChange={(e) => setText(e.target.value)} placeholder={t(lang, "citizen.textPlaceholder")} />
                </>
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
                      <span style={{ color: "var(--status-critical)" }}>
                        <MicWaveform />
                      </span>
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
            </>
          )}

          {step === "media" && (
            <>
              <h2>{t(lang, "wizard.media.title")}</h2>
              <p className="wizard-hint">{t(lang, "wizard.media.hint")}</p>
              <MultiPhotoUpload photos={photos} onChange={setPhotos} />
            </>
          )}

          {step === "ai" && (
            <>
              <h2>{t(lang, "wizard.ai.title")}</h2>
              <p className="wizard-hint">{t(lang, "wizard.ai.hint")}</p>
              {aiRunning ? (
                <div style={{ display: "flex", alignItems: "center", gap: 10, padding: "20px 0", color: "var(--ink-2)" }}>
                  <span className="ai-dot active" />
                  {t(lang, "wizard.ai.analyzing")}
                </div>
              ) : (
                <div className="surface-card" style={{ padding: 16 }}>
                  <div className="dev-badge" style={{ marginBottom: 10 }}>{t(lang, "wizard.ai.devBadge")}</div>
                  {category ? (
                    <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
                      <div className={`service-card-icon service-tile-${category.color}`} style={{ marginBottom: 0 }}>{category.icon}</div>
                      <div>
                        <div style={{ fontWeight: 700 }}>{t(lang, category.titleKey)}</div>
                        <div style={{ fontSize: 12, color: "var(--ink-2)" }}>{t(lang, "wizard.ai.matchedNote")}</div>
                      </div>
                    </div>
                  ) : (
                    <p style={{ margin: 0, fontSize: 13, color: "var(--ink-2)" }}>{t(lang, "wizard.ai.noMatch")}</p>
                  )}
                  <label style={{ display: "block", marginTop: 14, fontSize: 12, fontWeight: 700, color: "var(--ink-2)" }}>{t(lang, "wizard.ai.changeLabel")}</label>
                  <select value={category?.id ?? ""} onChange={(e) => setCategory(SERVICE_CATEGORY_DEFS.find((d) => d.id === e.target.value) ?? null)} style={{ marginTop: 6 }}>
                    <option value="">{t(lang, "wizard.ai.notSure")}</option>
                    {SERVICE_CATEGORY_DEFS.map((d) => (
                      <option key={d.id} value={d.id}>
                        {t(lang, d.titleKey)}
                      </option>
                    ))}
                  </select>
                </div>
              )}
            </>
          )}

          {step === "preview" && (
            <>
              <h2>{t(lang, "wizard.preview.title")}</h2>
              <p className="wizard-hint">{t(lang, "wizard.preview.hint")}</p>
              <dl style={{ margin: 0 }}>
                <div className="wizard-summary-row">
                  <dt>{t(lang, "wizard.preview.service")}</dt>
                  <dd>{category ? t(lang, category.titleKey) : t(lang, "wizard.ai.notSure")}</dd>
                </div>
                <div className="wizard-summary-row">
                  <dt>{t(lang, "wizard.preview.location")}</dt>
                  <dd>{location.ward || t(lang, "wizard.preview.noLocation")}</dd>
                </div>
                <div className="wizard-summary-row">
                  <dt>{t(lang, "wizard.preview.description")}</dt>
                  <dd>{inputMode === "text" ? text || "—" : t(lang, "citizen.voiceRecorded")}</dd>
                </div>
                <div className="wizard-summary-row">
                  <dt>{t(lang, "wizard.preview.photo")}</dt>
                  <dd>{photos.length > 0 ? photos.map((p) => p.name).join(", ") : t(lang, "wizard.preview.noPhoto")}</dd>
                </div>
                <div className="wizard-summary-row">
                  <dt>{t(lang, "wizard.preview.priority")}</dt>
                  <dd>{t(lang, "wizard.preview.priorityStandard")}</dd>
                </div>
              </dl>
            </>
          )}

          <div className="wizard-nav">
            <button type="button" className="btn btn-ghost" onClick={stepIndex === 0 ? () => navigate("/citizen") : goBack} disabled={submitting}>
              {stepIndex === 0 ? t(lang, "common.cancel") : t(lang, "wizard.back")}
            </button>
            {step === "preview" ? (
              <button type="button" className="btn btn-primary" onClick={handleSubmit} disabled={submitting}>
                {submitting ? t(lang, "citizen.submitting") : t(lang, "citizen.submit")}
              </button>
            ) : (
              <button type="button" className="btn btn-primary" onClick={goNext} disabled={aiRunning}>
                {t(lang, "wizard.next")}
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

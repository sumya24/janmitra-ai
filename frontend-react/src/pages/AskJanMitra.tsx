import { useEffect, useState, type FormEvent } from "react";
import { Link } from "react-router-dom";
import TopBar from "../components/TopBar";
import SourceCard from "../components/SourceCard";
import Mascot, { type MascotState } from "../components/Mascot";
import MultiPhotoUpload from "../components/MultiPhotoUpload";
import VoiceAssistantOverlay from "../components/VoiceAssistantOverlay";
import { useUiLang } from "../lib/uiLang";
import { useAuth } from "../lib/auth";
import { t } from "../lib/i18n";
import { api, ApiError } from "../lib/api";
import { useSpeechToText } from "../lib/useSpeechToText";
import type { AskJanMitraResponse, AskJanMitraConversationTurn } from "../lib/ragTypes";

const SUGGESTED_KEYS = ["waterLeak", "pothole", "garbage", "streetlight"] as const;

/**
 * Ask JanMitra — a civic information/reference assistant, not a chat product (P0, Task 5).
 * One question in, one grounded answer card with sources out, then a fixed set of next
 * actions — deliberately no message history/bubbles/streaming cursor, so it doesn't read as
 * ChatGPT-with-a-new-coat-of-paint.
 *
 * Wired to the real POST /ask-janmitra backend (see backend/services/ask_janmitra_service.py) —
 * the mock lookup this page used before the RAG backend existed has been removed entirely (see
 * lib/ragTypes.ts's AskJanMitraResponse docstring). `conversationHistory` is resent with every
 * request (the API is
 * stateless server-side, see backend/schemas/ask_janmitra.py's ConversationTurn docstring) so a
 * follow-up ("street light not working" after already having said "I'm in Mohali") doesn't make
 * the citizen repeat their location.
 *
 * Split into two exports: `AskJanMitraContent` is the actual chat UI (form, suggestions, answer
 * card) with no assumptions about what wraps it, and the default export is the thin full-page
 * version (just TopBar) used by the standalone /citizen/ask route. The
 * floating widget (AskJanMitraWidget.tsx) renders `AskJanMitraContent` directly inside its
 * slide-out panel instead -- same component, same real backend calls, no forked logic to keep
 * in sync between the two entry points.
 */
export function AskJanMitraContent() {
  const { lang } = useUiLang();
  const { token } = useAuth();
  const [question, setQuestion] = useState("");
  const [asked, setAsked] = useState<string | null>(null);
  const [response, setResponse] = useState<AskJanMitraResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [history, setHistory] = useState<AskJanMitraConversationTurn[]>([]);
  const [locatingGps, setLocatingGps] = useState(false);
  const [manualLocationInput, setManualLocationInput] = useState<string | null>(null);
  const speech = useSpeechToText(lang);
  const [showSuccess, setShowSuccess] = useState(false);
  const [attachedImage, setAttachedImage] = useState<File[]>([]);
  const [voiceOverlayOpen, setVoiceOverlayOpen] = useState(false);

  // Live transcript -> the same editable text input typed questions use, so by the time the
  // citizen hits Ask it's an ordinary text request (see useSpeechToText.ts's docstring on why
  // this is the only way to route chat speech at all -- /ask-janmitra has no audio field).
  useEffect(() => {
    if (speech.status === "recording" && speech.transcript) {
      setQuestion(speech.transcript);
    }
  }, [speech.transcript, speech.status]);

  // Brief "success" mascot flash on a genuinely new answer, not on every render where a response
  // happens to still be set (e.g. loading a follow-up) -- keyed on the response object itself.
  useEffect(() => {
    if (!response) return;
    setShowSuccess(true);
    const timer = setTimeout(() => setShowSuccess(false), 1200);
    return () => clearTimeout(timer);
  }, [response]);

  // One mascot, real state in -> real expression out. No invented "error" expression: an error
  // already has its own text banner below, so the mascot just stays idle/neutral for it.
  const mascotState: MascotState =
    speech.status === "recording" ? "listening" : loading ? "thinking" : showSuccess ? "success" : "idle";

  async function runQuery(q: string, opts: { locationText?: string; lat?: number; lng?: number } = {}) {
    if (!token) return;
    const trimmed = q.trim();
    if (!trimmed && attachedImage.length === 0) return;
    setAsked(trimmed);
    setLoading(true);
    setError(null);
    setManualLocationInput(null);
    try {
      const result =
        attachedImage.length > 0
          ? await api.askJanMitraWithImage(token, {
              question: trimmed,
              language: lang,
              latitude: opts.lat,
              longitude: opts.lng,
              location_text: opts.locationText,
              conversation_history: history,
              image: attachedImage[0],
            })
          : await api.askJanMitra(token, {
              question: trimmed,
              language: lang,
              latitude: opts.lat,
              longitude: opts.lng,
              location_text: opts.locationText,
              conversation_history: history,
            });
      setResponse(result);
      setHistory((prev) => [...prev, { role: "user", content: trimmed }, { role: "assistant", content: result.answer }]);
      // Only clear on success -- a failed request keeps the attached photo so the citizen can
      // just retry, instead of having to re-select it.
      setAttachedImage([]);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : t(lang, "ask.error"));
      setResponse(null);
    } finally {
      setLoading(false);
      setQuestion("");
    }
  }

  function handleSubmit(e: FormEvent) {
    e.preventDefault();
    runQuery(question);
  }

  function handleFollowUpOption(option: string) {
    if (!asked) return;
    if (option === "Use current location") {
      if (!("geolocation" in navigator)) {
        setError(t(lang, "location.unavailable"));
        return;
      }
      setLocatingGps(true);
      navigator.geolocation.getCurrentPosition(
        (pos) => {
          setLocatingGps(false);
          runQuery(asked, { lat: pos.coords.latitude, lng: pos.coords.longitude });
        },
        () => {
          setLocatingGps(false);
          setError(t(lang, "location.unavailable"));
        },
        { timeout: 8000 }
      );
      return;
    }
    if (option === "Enter manually" || option === "Select city") {
      setManualLocationInput("");
      return;
    }
    // Any other option is a real place name (a specific city, or a disambiguation candidate) —
    // resend the same question with it as the explicit location.
    runQuery(asked, { locationText: option });
  }

  function handleManualLocationSubmit(e: FormEvent) {
    e.preventDefault();
    if (!asked || !manualLocationInput?.trim()) return;
    runQuery(asked, { locationText: manualLocationInput.trim() });
  }

  function askSuggested(key: (typeof SUGGESTED_KEYS)[number]) {
    runQuery(t(lang, `ask.suggested.${key}`));
  }

  function reset() {
    setAsked(null);
    setResponse(null);
    setError(null);
    setHistory([]);
    setManualLocationInput(null);
    setAttachedImage([]);
  }

  return (
    <>
        <div className="page-head">
          <div>
            <h1 className="page-title display" style={{ display: "flex", alignItems: "center", gap: 10 }}>
              <Mascot state={mascotState} size={28} />
              {t(lang, "ask.title")}
            </h1>
            <p className="page-sub">{t(lang, "ask.subtitle")}</p>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="surface-card" style={{ padding: 16, marginBottom: 4, display: "flex", flexDirection: "column", gap: 10 }}>
          <div style={{ display: "flex", gap: 10 }}>
            <input
              type="text"
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              placeholder={t(lang, "ask.inputPlaceholder")}
              aria-label={t(lang, "ask.inputPlaceholder")}
              style={{ flex: 1 }}
              disabled={loading}
            />
            {/* No button at all when the browser doesn't expose SpeechRecognition (e.g. Firefox) --
                true graceful absence, not a disabled ghost control. */}
            {speech.supported && (
              <button
                type="button"
                className="btn btn-ghost"
                onClick={() => (speech.status === "recording" ? speech.stop() : speech.start())}
                disabled={loading}
                aria-label={t(lang, speech.status === "recording" ? "ask.voice.stop" : "ask.voice.micLabel")}
                aria-pressed={speech.status === "recording"}
                title={t(lang, speech.status === "recording" ? "ask.voice.stop" : "ask.voice.micLabel")}
              >
                {speech.status === "recording" ? (
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
                    <rect x="7" y="7" width="10" height="10" rx="2" fill="currentColor" />
                  </svg>
                ) : (
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
                    <rect x="9" y="3" width="6" height="12" rx="3" stroke="currentColor" strokeWidth="1.8" />
                    <path d="M5 11a7 7 0 0 0 14 0M12 18v3" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
                  </svg>
                )}
              </button>
            )}
            {/* "Mic 2" -- a genuinely separate control from the mic above (Mic 1, which just
                fills this text input for manual editing/sending). This one opens a dedicated
                spoken-conversation overlay instead -- see VoiceAssistantOverlay.tsx's docstring
                for why the two are deliberately not the same button/hook. */}
            <button
              type="button"
              className="btn btn-ghost"
              onClick={() => setVoiceOverlayOpen(true)}
              disabled={loading}
              aria-label={t(lang, "ask.voiceAssistant.openLabel")}
              title={t(lang, "ask.voiceAssistant.openLabel")}
            >
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
                <path d="M4 13a8 8 0 0 1 16 0" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
                <rect x="2.5" y="12" width="4" height="7" rx="1.5" stroke="currentColor" strokeWidth="1.6" />
                <rect x="17.5" y="12" width="4" height="7" rx="1.5" stroke="currentColor" strokeWidth="1.6" />
              </svg>
            </button>
            <button type="submit" className="btn btn-primary" disabled={(!question.trim() && attachedImage.length === 0) || loading}>
              {t(lang, "ask.submit")}
            </button>
          </div>
          <MultiPhotoUpload photos={attachedImage} onChange={setAttachedImage} maxFiles={1} placeholderKey="ask.image.addLabel" />
        </form>
        {speech.supported && speech.error && (
          <p className="page-sub" style={{ color: "var(--status-critical)", marginTop: 0, marginBottom: 8 }}>
            {t(lang, speech.error)}
          </p>
        )}

        {!asked && (
          <div className="ask-suggestions">
            {SUGGESTED_KEYS.map((key) => (
              <button key={key} type="button" className="ask-suggestion" onClick={() => askSuggested(key)}>
                {t(lang, `ask.suggested.${key}`)}
              </button>
            ))}
          </div>
        )}

        {asked && (
          <div className="enter">
            <div className="ask-question-echo">
              {t(lang, "ask.youAsked")} <strong>{asked}</strong>
            </div>

            {(loading || locatingGps) && (
              <div className="surface-card ask-answer-card" aria-live="polite">
                {t(lang, locatingGps ? "location.locating" : "ask.loading")}
              </div>
            )}

            {!loading && !locatingGps && error && (
              <div className="surface-card ask-answer-card banner-error">{error}</div>
            )}

            {!loading && !locatingGps && !error && response && (
              <div className="surface-card ask-answer-card">
                <p className="ask-answer-text">{response.answer}</p>

                {response.follow_up_required && (
                  <div className="ask-followup">
                    {response.follow_up_question && (
                      <div className="ask-sources-label">{t(lang, "ask.followUp.label")}</div>
                    )}
                    <div style={{ display: "flex", flexWrap: "wrap", gap: 8, marginTop: 8 }}>
                      {(response.follow_up_options.length > 0
                        ? response.follow_up_options
                        : ["Use current location", "Enter manually"]
                      ).map((opt) => (
                        <button key={opt} type="button" className="btn btn-ghost btn-sm" onClick={() => handleFollowUpOption(opt)}>
                          {opt === "Use current location"
                            ? t(lang, "location.useCurrent")
                            : opt === "Select city" || opt === "Enter manually"
                              ? t(lang, "location.selectManually")
                              : opt}
                        </button>
                      ))}
                    </div>
                    {manualLocationInput !== null && (
                      <form onSubmit={handleManualLocationSubmit} style={{ display: "flex", gap: 8, marginTop: 10 }}>
                        <input
                          type="text"
                          value={manualLocationInput}
                          onChange={(e) => setManualLocationInput(e.target.value)}
                          placeholder={t(lang, "citizen.wardPlaceholder")}
                          style={{ flex: 1 }}
                          autoFocus
                        />
                        <button type="submit" className="btn btn-primary btn-sm" disabled={!manualLocationInput.trim()}>
                          {t(lang, "ask.submit")}
                        </button>
                      </form>
                    )}
                  </div>
                )}

                {response.sources.length > 0 && (
                  <>
                    <div className="ask-sources-label">{t(lang, "ask.sourcesLabel")}</div>
                    {response.sources.map((source) => (
                      <SourceCard key={source.source_id} source={source} />
                    ))}
                  </>
                )}

                <div className="ask-quick-actions">
                  <Link to="/citizen/report" className="btn btn-primary btn-sm">
                    {t(lang, "ask.action.report")}
                  </Link>
                  <Link to="/citizen/complaints" className="btn btn-ghost btn-sm">
                    {t(lang, "ask.action.track")}
                  </Link>
                  <button type="button" className="btn btn-ghost btn-sm" onClick={reset}>
                    {t(lang, "ask.action.askAnother")}
                  </button>
                </div>
              </div>
            )}
          </div>
        )}

        {voiceOverlayOpen && <VoiceAssistantOverlay onClose={() => setVoiceOverlayOpen(false)} />}
    </>
  );
}

/** The standalone full-page route (/citizen/ask) -- TopBar + the same content the floating
 * widget renders, so a direct link/bookmark/browser-back still lands somewhere real. */
export default function AskJanMitra() {
  return (
    <div>
      <TopBar />
      <div className="page">
        <AskJanMitraContent />
      </div>
    </div>
  );
}

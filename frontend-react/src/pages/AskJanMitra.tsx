import { useEffect, useRef, useState, type FormEvent, type KeyboardEvent } from "react";
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

/** One turn in the visible chat log. `history` sent to the backend (AskJanMitraConversationTurn[])
 * is always derived from this array (role + text only) rather than kept as a second, parallel
 * list -- one source of truth for what the citizen sees AND what gets resent as context. */
interface ChatMessage {
  id: number;
  role: "user" | "assistant";
  text: string;
  /** User messages only -- an object URL for the attached photo, so the citizen sees exactly
   * what they sent. Revoked on unmount (see the cleanup effect below), not on every render. */
  imagePreview?: string;
  /** Assistant messages only -- the full backend response, so sources/follow-up/complaint
   * outcome can render without a second shape to keep in sync with `text`. */
  response?: AskJanMitraResponse;
  /** Assistant messages only -- the user question this response is answering, captured at
   * creation time. Needed so a follow-up option clicked later (e.g. "Use current location")
   * can resend the SAME original question with added location info, exactly like the previous
   * single-turn UI did with its one top-level `asked` variable -- just now per-message instead
   * of global, since multiple turns are visible at once. */
  originalQuestion?: string;
  /** Set when this turn's request failed -- `text` is the error message in that case, and
   * `retry` (bound to this exact question/options at send time) re-issues the same request. */
  isError?: boolean;
  retry?: () => void;
}

/**
 * Ask JanMitra -- a continuous, ChatGPT-style conversation with JanMitra, not a single-question
 * form (see git history for the earlier form-shaped version deliberately replaced here). Same
 * real backend, same real Mic 1 (useSpeechToText.ts)/Mic 2 (VoiceAssistantOverlay.tsx)/image
 * attach (MultiPhotoUpload.tsx)/mascot (Mascot.tsx) as before -- this file only changes how the
 * conversation is *laid out*, not what powers it. `conversationHistory` is resent with every
 * request (the API is stateless server-side, see backend/schemas/ask_janmitra.py's
 * ConversationTurn docstring) so a follow-up ("street light not working" after already having
 * said "I'm in Mohali") doesn't make the citizen repeat their location -- now derived from the
 * full visible `messages` transcript instead of a separate parallel list.
 *
 * Split into two exports: `AskJanMitraContent` is the actual chat UI (message list + composer)
 * with no assumptions about what wraps it -- its root fills whatever height its parent flex
 * container provides, which is what lets the exact same component work both as the standalone
 * page below (a fixed-height flex column under TopBar) and inside AskJanMitraWidget.tsx's
 * slide-out panel (already its own flex column) without needing to know which one it's in.
 */
export function AskJanMitraContent() {
  const { lang } = useUiLang();
  const { token } = useAuth();
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [loading, setLoading] = useState(false);
  const [locatingGps, setLocatingGps] = useState(false);
  const [manualLocationInput, setManualLocationInput] = useState<string | null>(null);
  const [manualLocationTargetId, setManualLocationTargetId] = useState<number | null>(null);
  const speech = useSpeechToText(lang);
  const [showSuccess, setShowSuccess] = useState(false);
  const [attachedImage, setAttachedImage] = useState<File[]>([]);
  const [showAttach, setShowAttach] = useState(false);
  const [voiceOverlayOpen, setVoiceOverlayOpen] = useState(false);
  // True while `question`'s current text came from Mic 1 rather than typing -- sent as
  // `was_voice_input` so the backend's LangSmith metadata can distinguish "TEXT"/"IMAGE" from
  // "STT"/"IMAGE_STT" (see ask_janmitra_service.py). Purely an observability signal; never
  // changes what gets asked or how it's routed.
  const [questionFromVoice, setQuestionFromVoice] = useState(false);

  const nextIdRef = useRef(0);
  const imagePreviewUrlsRef = useRef<string[]>([]);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  function nextId() {
    nextIdRef.current += 1;
    return nextIdRef.current;
  }

  // Live transcript -> the same editable composer text typed questions use, so by the time the
  // citizen hits Send it's an ordinary text request (see useSpeechToText.ts's docstring on why
  // this is the only way to route chat speech at all -- /ask-janmitra has no audio field).
  useEffect(() => {
    if (speech.status === "recording" && speech.transcript) {
      setQuestion(speech.transcript);
      setQuestionFromVoice(true);
    }
  }, [speech.transcript, speech.status]);

  // Brief "success" mascot flash on a genuinely new answer, not on every render.
  useEffect(() => {
    if (loading) return;
    const last = messages[messages.length - 1];
    if (!last || last.role !== "assistant" || last.isError) return;
    setShowSuccess(true);
    const timer = setTimeout(() => setShowSuccess(false), 1200);
    return () => clearTimeout(timer);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [messages.length, loading]);

  // Auto-scroll to the latest turn (or the thinking indicator) -- a real conversation, so the
  // newest message is always what's in view, same as any chat app.
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [messages.length, loading, locatingGps]);

  // Composer grows with content up to a cap, then scrolls internally -- never pushes the send
  // row off-screen on a long paste.
  useEffect(() => {
    const el = textareaRef.current;
    if (!el) return;
    el.style.height = "auto";
    el.style.height = `${Math.min(el.scrollHeight, 160)}px`;
  }, [question]);

  useEffect(() => {
    const urls = imagePreviewUrlsRef.current;
    return () => {
      urls.forEach((url) => URL.revokeObjectURL(url));
    };
  }, []);

  // One mascot, real state in -> real expression out. No invented "error" expression: an error
  // already has its own text bubble, so the mascot just stays idle rather than performing an
  // emotion this 5-state set doesn't have.
  const mascotState: MascotState =
    speech.status === "recording" ? "listening" : loading ? "thinking" : showSuccess ? "success" : "idle";

  async function runQuery(q: string, opts: { locationText?: string; lat?: number; lng?: number } = {}) {
    if (!token) return;
    const trimmed = q.trim();
    const imageToSend = attachedImage[0];
    if (!trimmed && !imageToSend) return;

    // Everything already on screen, in order -- exactly what the backend should treat as prior
    // context for this new turn (see the class docstring on why this replaces a separate list).
    const historyForRequest: AskJanMitraConversationTurn[] = messages.map((m) => ({ role: m.role, content: m.text }));

    let imagePreview: string | undefined;
    if (imageToSend) {
      imagePreview = URL.createObjectURL(imageToSend);
      imagePreviewUrlsRef.current.push(imagePreview);
    }
    setMessages((prev) => [...prev, { id: nextId(), role: "user", text: trimmed, imagePreview }]);
    setQuestion("");
    setManualLocationInput(null);
    setManualLocationTargetId(null);
    setLoading(true);

    try {
      const result = imageToSend
        ? await api.askJanMitraWithImage(token, {
            question: trimmed,
            language: lang,
            latitude: opts.lat,
            longitude: opts.lng,
            location_text: opts.locationText,
            conversation_history: historyForRequest,
            image: imageToSend,
            was_voice_input: questionFromVoice,
          })
        : await api.askJanMitra(token, {
            question: trimmed,
            language: lang,
            latitude: opts.lat,
            longitude: opts.lng,
            location_text: opts.locationText,
            conversation_history: historyForRequest,
            was_voice_input: questionFromVoice,
          });
      setMessages((prev) => [
        ...prev,
        { id: nextId(), role: "assistant", text: result.answer, response: result, originalQuestion: trimmed },
      ]);
      // Only clear on success -- a failed request keeps the attached photo so the citizen can
      // just retry without re-selecting it.
      setAttachedImage([]);
      setShowAttach(false);
    } catch (err) {
      const message = err instanceof ApiError ? err.message : t(lang, "ask.error");
      setMessages((prev) => [
        ...prev,
        { id: nextId(), role: "assistant", text: message, isError: true, retry: () => runQuery(trimmed, opts) },
      ]);
    } finally {
      setLoading(false);
      setQuestionFromVoice(false);
    }
  }

  function handleSubmit(e?: FormEvent) {
    e?.preventDefault();
    runQuery(question);
  }

  function handleComposerKeyDown(e: KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      if (!loading && (question.trim() || attachedImage.length > 0)) handleSubmit();
    }
  }

  function handleFollowUpOption(msg: ChatMessage, option: string) {
    if (!msg.originalQuestion) return;
    if (option === "Use current location") {
      if (!("geolocation" in navigator)) return;
      setLocatingGps(true);
      navigator.geolocation.getCurrentPosition(
        (pos) => {
          setLocatingGps(false);
          runQuery(msg.originalQuestion!, { lat: pos.coords.latitude, lng: pos.coords.longitude });
        },
        () => {
          setLocatingGps(false);
          setMessages((prev) => [
            ...prev,
            { id: nextId(), role: "assistant", text: t(lang, "location.unavailable"), isError: true },
          ]);
        },
        { timeout: 8000 }
      );
      return;
    }
    if (option === "Enter manually" || option === "Select city") {
      setManualLocationInput("");
      setManualLocationTargetId(msg.id);
      return;
    }
    runQuery(msg.originalQuestion, { locationText: option });
  }

  function handleManualLocationSubmit(e: FormEvent, msg: ChatMessage) {
    e.preventDefault();
    if (!msg.originalQuestion || !manualLocationInput?.trim()) return;
    runQuery(msg.originalQuestion, { locationText: manualLocationInput.trim() });
  }

  function askSuggested(key: (typeof SUGGESTED_KEYS)[number]) {
    runQuery(t(lang, `ask.suggested.${key}`));
  }

  const lastMessageId = messages.length > 0 ? messages[messages.length - 1].id : null;

  return (
    <div className="ask-chat-shell">
      <div className="ask-chat-messages">
        {messages.length === 0 && (
          <div className="ask-chat-empty">
            <Mascot state={mascotState} size={64} />
            <h1 className="ask-chat-empty-title">{t(lang, "ask.title")}</h1>
            <p className="ask-chat-empty-sub">{t(lang, "ask.subtitle")}</p>
            <div className="ask-suggestions ask-suggestions-center">
              {SUGGESTED_KEYS.map((key) => (
                <button key={key} type="button" className="ask-suggestion" onClick={() => askSuggested(key)}>
                  {t(lang, `ask.suggested.${key}`)}
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((msg) => (
          <div key={msg.id} className={`ask-chat-row ask-chat-row-${msg.role}`}>
            {msg.role === "assistant" && (
              <div className="ask-chat-avatar">
                <Mascot state="idle" size={22} />
              </div>
            )}

            <div className={`ask-chat-bubble${msg.isError ? " ask-chat-bubble-error" : ""}`}>
              {msg.imagePreview && (
                <img src={msg.imagePreview} alt={t(lang, "photo.previewAlt")} className="ask-chat-image" />
              )}
              <p className="ask-chat-text">{msg.text}</p>

              {msg.isError && msg.retry && (
                <button type="button" className="btn btn-ghost btn-sm" onClick={msg.retry} style={{ marginTop: 8 }}>
                  {t(lang, "ask.voiceAssistant.tryAgain")}
                </button>
              )}

              {msg.response && (
                <>
                  {msg.response.complaint_id != null && (
                    <div className="ask-chat-complaint-note">
                      <span className="ai-dot active" />
                      {t(lang, "citizen.submitSuccess")}
                      <Link to="/citizen/complaints" className="ask-chat-complaint-link">
                        {t(lang, "ask.action.track")}
                      </Link>
                    </div>
                  )}

                  {msg.response.follow_up_required && msg.id === lastMessageId && !loading && (
                    <div className="ask-followup">
                      {msg.response.follow_up_question && (
                        <div className="ask-sources-label">{t(lang, "ask.followUp.label")}</div>
                      )}
                      <div style={{ display: "flex", flexWrap: "wrap", gap: 8, marginTop: 8 }}>
                        {(msg.response.follow_up_options.length > 0
                          ? msg.response.follow_up_options
                          : ["Use current location", "Enter manually"]
                        ).map((opt) => (
                          <button
                            key={opt}
                            type="button"
                            className="btn btn-ghost btn-sm"
                            onClick={() => handleFollowUpOption(msg, opt)}
                            disabled={locatingGps}
                          >
                            {opt === "Use current location"
                              ? t(lang, "location.useCurrent")
                              : opt === "Select city" || opt === "Enter manually"
                                ? t(lang, "location.selectManually")
                                : opt}
                          </button>
                        ))}
                      </div>
                      {manualLocationTargetId === msg.id && manualLocationInput !== null && (
                        <form onSubmit={(e) => handleManualLocationSubmit(e, msg)} style={{ display: "flex", gap: 8, marginTop: 10 }}>
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

                  {msg.response.sources.length > 0 && (
                    <>
                      <div className="ask-sources-label">{t(lang, "ask.sourcesLabel")}</div>
                      {msg.response.sources.map((source) => (
                        <SourceCard key={source.source_id} source={source} />
                      ))}
                    </>
                  )}

                  {!msg.response.follow_up_required && (
                    <div className="ask-quick-actions">
                      <Link to="/citizen/report" className="btn btn-ghost btn-sm">
                        {t(lang, "ask.action.report")}
                      </Link>
                      <Link to="/citizen/complaints" className="btn btn-ghost btn-sm">
                        {t(lang, "ask.action.track")}
                      </Link>
                    </div>
                  )}
                </>
              )}
            </div>
          </div>
        ))}

        {(loading || locatingGps) && (
          <div className="ask-chat-row ask-chat-row-assistant">
            <div className="ask-chat-avatar">
              <Mascot state="thinking" size={22} />
            </div>
            <div className="ask-chat-bubble ask-chat-thinking" aria-live="polite">
              <span className="ask-chat-thinking-dots" aria-hidden="true">
                <span />
                <span />
                <span />
              </span>
              {t(lang, locatingGps ? "location.locating" : "ask.loading")}
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      <form onSubmit={handleSubmit} className="ask-chat-composer">
        {(showAttach || attachedImage.length > 0) && (
          <div className="ask-chat-attach-panel">
            <MultiPhotoUpload photos={attachedImage} onChange={setAttachedImage} maxFiles={1} placeholderKey="ask.image.addLabel" />
          </div>
        )}

        {speech.supported && speech.error && (
          <p className="ask-chat-composer-error">{t(lang, speech.error)}</p>
        )}

        <div className="ask-chat-composer-row">
          {/* Live mascot state, always visible next to the composer -- not just in the empty
              state (which disappears after the first message) or the per-message avatars (fixed
              "idle", so they don't show a live in-progress state). This is what keeps
              listening/thinking/success connected to real app state throughout an entire
              conversation, not just before it starts. */}
          <div className="ask-chat-composer-mascot" aria-hidden="true">
            <Mascot state={mascotState} size={26} />
          </div>
          <button
            type="button"
            className={`ask-chat-icon-btn${showAttach || attachedImage.length > 0 ? " active" : ""}`}
            onClick={() => setShowAttach((s) => !s)}
            disabled={loading}
            aria-label={t(lang, "ask.image.addLabel")}
            title={t(lang, "ask.image.addLabel")}
            aria-pressed={showAttach || attachedImage.length > 0}
          >
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
              <path d="M12 5v14M5 12h14" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
            </svg>
          </button>

          <textarea
            ref={textareaRef}
            value={question}
            onChange={(e) => {
              setQuestion(e.target.value);
              // A manual edit after Mic 1 filled the box means the citizen is typing now --
              // the request should honestly report "TEXT", not "STT".
              setQuestionFromVoice(false);
            }}
            onKeyDown={handleComposerKeyDown}
            placeholder={t(lang, "ask.inputPlaceholder")}
            aria-label={t(lang, "ask.inputPlaceholder")}
            className="ask-chat-textarea"
            rows={1}
            disabled={loading}
          />

          {/* No button at all when the browser doesn't expose SpeechRecognition (e.g. Firefox) --
              true graceful absence, not a disabled ghost control. */}
          {speech.supported && (
            <button
              type="button"
              className={`ask-chat-icon-btn ask-chat-mic1-btn${speech.status === "recording" ? " active" : ""}`}
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

          {/* "Mic 2" -- a genuinely separate control from the mic above (Mic 1, which just fills
              the composer for manual editing/sending). This one opens a dedicated
              spoken-conversation overlay instead -- see VoiceAssistantOverlay.tsx's docstring
              for why the two are deliberately not the same button/hook. */}
          <button
            type="button"
            className="ask-chat-icon-btn"
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

          <button
            type="submit"
            className="ask-chat-send-btn"
            disabled={(!question.trim() && attachedImage.length === 0) || loading}
            aria-label={t(lang, "ask.submit")}
            title={t(lang, "ask.submit")}
          >
            {loading ? (
              <span className="ask-chat-send-spinner" aria-hidden="true" />
            ) : (
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
                <path d="M4 12h15M13 6l6 6-6 6" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
              </svg>
            )}
          </button>
        </div>
      </form>

      {voiceOverlayOpen && <VoiceAssistantOverlay onClose={() => setVoiceOverlayOpen(false)} />}
    </div>
  );
}

/** The standalone full-page route (/citizen/ask) -- TopBar + the same chat content the floating
 * widget renders, so a direct link/bookmark/browser-back still lands somewhere real. Gives
 * AskJanMitraContent a fixed, viewport-relative height to fill (100dvh minus TopBar) so its
 * composer stays anchored near the bottom instead of just trailing off at the end of a long page. */
export default function AskJanMitra() {
  return (
    <div className="ask-page-viewport">
      <TopBar />
      <div className="page ask-page">
        <AskJanMitraContent />
      </div>
    </div>
  );
}

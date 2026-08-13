import { useEffect, useRef, useState, type FormEvent, type KeyboardEvent } from "react";
import { Link } from "react-router-dom";
import TopBar from "../components/TopBar";
import SourceCard from "../components/SourceCard";
import Mascot, { type MascotState } from "../components/Mascot";
import MultiPhotoUpload from "../components/MultiPhotoUpload";
import VoiceAssistantOverlay from "../components/VoiceAssistantOverlay";
import LocationPicker, { type LocationValue } from "../components/LocationPicker";
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
 * Ask Sarthi -- a continuous, ChatGPT-style conversation with Sarthi, not a single-question
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

/** Crossfades between two mascot poses instead of hard-swapping the <img src>, which is what read
 * as "fake"/slideshow-like -- two static poses popping in and out with no transition at all. Both
 * poses are real, already-existing Mascot states (no invented pose); this only smooths *how* the
 * welcome screen moves between them. Scoped to this one welcome-screen usage rather than changing
 * Mascot.tsx itself, since every other consumer (message avatars, the widget FAB, VoiceAssistantOverlay)
 * only ever renders one state at a time with no complaint about the transition. */
function WelcomeMascot({ state, size }: { state: MascotState; size: number }) {
  const [current, setCurrent] = useState(state);
  const [outgoing, setOutgoing] = useState<MascotState | null>(null);
  const lastState = useRef(state);

  useEffect(() => {
    if (state === lastState.current) return;
    setOutgoing(lastState.current);
    setCurrent(state);
    lastState.current = state;
    const timeout = window.setTimeout(() => setOutgoing(null), 500);
    return () => window.clearTimeout(timeout);
  }, [state]);

  return (
    <div className="ask-chat-welcome-mascot" style={{ height: size, width: size }}>
      {outgoing && (
        <div key={`out-${outgoing}`} className="ask-chat-welcome-mascot-layer ask-chat-welcome-mascot-out">
          <Mascot state={outgoing} size={size} />
        </div>
      )}
      <div key={`in-${current}`} className="ask-chat-welcome-mascot-layer ask-chat-welcome-mascot-in">
        <Mascot state={current} size={size} />
      </div>
    </div>
  );
}

export function AskJanMitraContent() {
  const { lang } = useUiLang();
  const { token } = useAuth();
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [loading, setLoading] = useState(false);
  // Real, worker-backed wards -- the SAME list/component ReportIssue.tsx's "Report an Issue"
  // wizard already uses (see LocationPicker.tsx's own docstring), reused here rather than a
  // hand-rolled button list so a citizen actually gets a real dropdown of serviceable areas, not
  // a generic "type something" box. Fetched once; this list changes rarely (only when an admin
  // adds/removes a worker), same assumption ReportIssue.tsx already makes.
  const [wards, setWards] = useState<string[]>([]);
  const [locationPickerValue, setLocationPickerValue] = useState<LocationValue>({ ward: "", coords: null });
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
  }, [messages.length, loading]);

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

  useEffect(() => {
    if (!token) return;
    api.listWards(token).then(setWards).catch(() => setWards([]));
  }, [token]);

  // One mascot, real state in -> real expression out. No invented "error" expression: an error
  // already has its own text bubble, so the mascot just stays idle rather than performing an
  // emotion this 5-state set doesn't have.
  const mascotState: MascotState =
    speech.status === "recording" ? "listening" : loading ? "thinking" : showSuccess ? "success" : "idle";

  // Ambient wave<->namaste loop, but ONLY for the pre-conversation welcome screen and ONLY while
  // nothing real is actually happening (mascotState is genuinely "idle") -- ask.widget.greeting's
  // bubble greeting stays a true one-shot per its own docstring; this is a separate, explicitly
  // requested exception scoped to the empty state, done by re-applying the .mascot-greeting class
  // on an interval rather than changing the underlying one-shot wave animation itself.
  const [welcomeWave, setWelcomeWave] = useState(false);
  useEffect(() => {
    if (messages.length > 0 || mascotState !== "idle") return;
    const interval = setInterval(() => setWelcomeWave((w) => !w), 2600);
    return () => clearInterval(interval);
  }, [messages.length, mascotState]);
  const welcomeMascotState: MascotState = mascotState === "idle" && welcomeWave ? "greeting" : mascotState;

  async function runQuery(
    q: string,
    opts: { locationText?: string; lat?: number; lng?: number; displayText?: string } = {}
  ) {
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
    // `opts.displayText`, when given, is what the citizen actually just DID (e.g. "Ward 22 —
    // Kothrud, Pune" from the location picker, or a picked city name for an ambiguous-location
    // reply) -- shown in the chat bubble AND sent as this turn's conversation-history content,
    // instead of silently resending `trimmed` (the ORIGINAL complaint question, needed as the
    // real `question` field for the backend) as if the citizen had typed it again. Real, reported
    // bug this closes: "पानी के रिसाव की शिकायत कैसे करें?" appeared twice in a row after picking
    // a ward from the dropdown, reading as if the citizen had retyped their own question, when
    // they'd actually just answered "where". `historyForRequest` above is derived from `messages`
    // (the visible transcript, see this component's own docstring on why there's no second,
    // parallel history list) -- showing the real answer here also makes conversation_history read
    // (and resolve, e.g. via nodes.py's own conversation-history location fallback) correctly on
    // any LATER turn, rather than re-showing the original question a second time in history too.
    setMessages((prev) => [...prev, { id: nextId(), role: "user", text: opts.displayText ?? trimmed, imagePreview }]);
    setQuestion("");
    setLocationPickerValue({ ward: "", coords: null });
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
    // Ground this in real conversation state, not a guess at the typed text's shape: if the
    // AI's last message was SPECIFICALLY asking for a location (either the plain "what is the
    // location?" shape -- follow_up_options includes "Use current location" -- or the ambiguous
    // "which city, X or Y?" shape -- location.is_ambiguous), treat this reply as the answer to
    // THAT question rather than a brand-new one. Real, reported problem this closes: a citizen
    // typing a real city name (e.g. "Kolhapur") directly into the composer, instead of using the
    // "Select location" button, got the identical location question back forever -- their answer
    // was sent as a new `question` with no `location_text`, so it was never even considered a
    // location. Every OTHER follow-up shape (category, status, unclear, image-no-text) has a
    // distinct options shape that does NOT match this check, so this can't misfire on those --
    // e.g. it won't treat a reply to "what issue would you like to report?" as a location.
    const lastMsg = messages[messages.length - 1];
    const lastAskedForLocation =
      lastMsg?.role === "assistant" &&
      lastMsg.response?.follow_up_required &&
      (lastMsg.response.follow_up_options.includes("Use current location") || lastMsg.response.location?.is_ambiguous);
    if (lastAskedForLocation && lastMsg.originalQuestion && question.trim() && attachedImage.length === 0) {
      // Same displayText fix as handleLocationPickerSubmit below -- what's typed here (e.g.
      // "Kolhapur") IS already the real answer, so show it, not the original question again.
      runQuery(lastMsg.originalQuestion, { locationText: question.trim(), displayText: question.trim() });
      return;
    }
    runQuery(question);
  }

  function handleComposerKeyDown(e: KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      if (!loading && (question.trim() || attachedImage.length > 0)) handleSubmit();
    }
  }

  // Only ever reached for `location_ambiguous`'s real city-name options now (e.g. "Patiala" vs
  // "Sahibzada Ajit Singh Nagar (Mohali)", see clarification_flow_node) -- the plain "which
  // location?" case (`_LOCATION_CLARIFICATION_OPTIONS`) is handled entirely by the real
  // `LocationPicker` below instead of this generic button-label resend, so a citizen actually
  // gets a real dropdown of serviceable wards (see `handleLocationPickerSubmit`), not a button
  // whose own label text ("Select location") used to get sent as if it were a place name.
  function handleFollowUpOption(msg: ChatMessage, option: string) {
    if (!msg.originalQuestion) return;
    runQuery(msg.originalQuestion, { locationText: option, displayText: option });
  }

  function handleLocationPickerSubmit(msg: ChatMessage) {
    if (!msg.originalQuestion || !locationPickerValue.ward.trim()) return;
    const ward = locationPickerValue.ward.trim();
    runQuery(msg.originalQuestion, { locationText: ward, displayText: ward });
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
            <WelcomeMascot state={welcomeMascotState} size={130} />
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
                <Mascot state="idle" size={72} />
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
                      {msg.response.follow_up_options.includes("Use current location") && !msg.response.location?.is_ambiguous ? (
                        // The plain "what is the location?" case (`_LOCATION_CLARIFICATION_
                        // OPTIONS`, see nodes.py) -- a real `LocationPicker` (GPS, or a dropdown
                        // of the actual currently-staffed wards), the SAME component ReportIssue.
                        // tsx's "Report an Issue" wizard already uses, instead of a hand-rolled
                        // button list. Closes a real, reported gap: the raw backend option labels
                        // ("Enter location"/"Select location") both used to open the identical
                        // free-text box -- two buttons that looked like a choice but weren't one
                        // -- when "Select location" was always meant to be a real dropdown (see
                        // LocationPicker.tsx's own "Choose your ward or area from a list" hint,
                        // which only this component actually delivers on).
                        <div style={{ marginTop: 8 }}>
                          <LocationPicker value={locationPickerValue} onChange={setLocationPickerValue} wards={wards} />
                          <button
                            type="button"
                            className="btn btn-primary btn-sm"
                            style={{ marginTop: 10 }}
                            disabled={!locationPickerValue.ward.trim()}
                            onClick={() => handleLocationPickerSubmit(msg)}
                          >
                            {t(lang, "ask.submit")}
                          </button>
                        </div>
                      ) : msg.response.follow_up_options.length > 0 ? (
                        // location_ambiguous's real city-name candidates (e.g. "Patiala" vs
                        // "Sahibzada Ajit Singh Nagar (Mohali)") or the category options -- a
                        // short, fixed, already-meaningful list, where a plain button per option
                        // is the correct UI (not a full ward-picker).
                        <div style={{ display: "flex", flexWrap: "wrap", gap: 8, marginTop: 8 }}>
                          {msg.response.follow_up_options.map((opt) => (
                            <button key={opt} type="button" className="btn btn-ghost btn-sm" onClick={() => handleFollowUpOption(msg, opt)}>
                              {opt}
                            </button>
                          ))}
                        </div>
                      ) : msg.response.intent === "TYPE_C_STATUS" ? (
                        // status_flow_node deliberately leaves follow_up_options empty here --
                        // there's no fixed list of complaint numbers to offer, it wants a free-
                        // typed one (the citizen can just type it in the composer as normal).
                        // This used to fall through to the location-picker branch below, which
                        // made a "what's your complaint number?" question show "Use current
                        // location"/GPS buttons -- a real, reported bug. A link to the complaints
                        // list matches the answer text's own "...or check your complaints list."
                        <div style={{ display: "flex", flexWrap: "wrap", gap: 8, marginTop: 8 }}>
                          <Link to="/citizen/complaints" className="btn btn-ghost btn-sm">
                            {t(lang, "ask.action.track")}
                          </Link>
                        </div>
                      ) : msg.response.intent === "UNCLEAR" ? (
                        // unclear_flow_node ALSO leaves follow_up_options empty (see nodes.py) --
                        // the same bug the TYPE_C_STATUS branch above fixes, just a second real
                        // occurrence caught later (a plain "hello" reproduced it live: the answer
                        // correctly said "I didn't understand", but the UI still offered a "Use
                        // current location" button underneath it, which makes no sense for a
                        // greeting). There's no single right action to offer here -- the answer
                        // text itself already says what to do ("What would you like help with?"),
                        // so the citizen just types their real question in the composer. No
                        // buttons is the honest UI for that, not a location picker.
                        null
                      ) : (
                        // Defensive fallback only, for a genuinely unknown future case -- NOT a
                        // location picker (see above: no real backend path with empty options has
                        // ever actually meant "needs a location" -- every real location
                        // clarification already populates follow_up_options via
                        // clarification_flow_node's four branches). Rendering nothing is the safe
                        // default; a specific new empty-options case should get its own branch
                        // above, the same way TYPE_C_STATUS/UNCLEAR did, not a guessed-at button.
                        null
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

        {loading && (
          <div className="ask-chat-row ask-chat-row-assistant">
            <div className="ask-chat-avatar">
              <Mascot state="thinking" size={72} />
            </div>
            <div className="ask-chat-bubble ask-chat-thinking" aria-live="polite">
              <span className="ask-chat-thinking-dots" aria-hidden="true">
                <span />
                <span />
                <span />
              </span>
              {t(lang, "ask.loading")}
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

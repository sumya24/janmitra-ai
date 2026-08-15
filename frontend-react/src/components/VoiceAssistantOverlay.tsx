import { useEffect, useRef, useState } from "react";
import Mascot, { type MascotState } from "./Mascot";
import MultiPhotoUpload from "./MultiPhotoUpload";
import { useUiLang } from "../lib/uiLang";
import { useAuth } from "../lib/auth";
import { t, SUPPORTED_LANGUAGES } from "../lib/i18n";
import { api, ApiError } from "../lib/api";
import { useAudioRecorder } from "../lib/useAudioRecorder";
import type { AskJanMitraConversationTurn } from "../lib/ragTypes";
import "./VoiceAssistantOverlay.css";

type VoicePhase = "idle" | "listening" | "processing" | "speaking" | "error";

/**
 * "Mic 2" -- the voice-to-voice conversation assistant. A genuinely different control from Mic 1
 * (useSpeechToText.ts, which just fills the text input for manual editing/sending): this opens a
 * dedicated overlay, captures a full spoken turn via the SAME chunked-recording hook the
 * complaint-creation voice flow already uses (useAudioRecorder.ts), sends it to the real
 * POST /ask-janmitra/voice backend, and plays back the AI's real synthesized speech.
 *
 * Turn-based by design (not real-time interruption) -- see the implementation plan for why: this
 * stack has no streaming ASR/persistent channel, so real barge-in isn't feasible without a real
 * architecture change. The citizen explicitly stops their turn; the AI's full spoken response
 * plays before the next turn can start. Mute stops local playback only, never the backend call.
 *
 * The mascot's "speaking" state (Mascot.tsx's own `.mascot-speaking` pulse) is applied ONLY
 * while the <audio> element is actually firing `playing` -- removed again on pause/ended/error
 * (see the `audioPlaying` state below, set only from those real events) -- so it never appears
 * to speak without real audio playing, and never for a fixed/guessed duration.
 */
export default function VoiceAssistantOverlay({ onClose }: { onClose: () => void }) {
  const { lang } = useUiLang();
  const { token } = useAuth();
  const recorder = useAudioRecorder();

  const [phase, setPhase] = useState<VoicePhase>("idle");
  const [error, setError] = useState<string | null>(null);
  const [transcript, setTranscript] = useState<string | null>(null);
  const [responseText, setResponseText] = useState<string | null>(null);
  const [muted, setMuted] = useState(false);
  const [audioPlaying, setAudioPlaying] = useState(false);
  const [history, setHistory] = useState<AskJanMitraConversationTurn[]>([]);
  const [attachedImage, setAttachedImage] = useState<File[]>([]);

  const stopRequestedRef = useRef(false);
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const audioUrlRef = useRef<string | null>(null);

  // useAudioRecorder's audioSegments only reflects the final segment once its own async
  // MediaRecorder.onstop handler fires (see that hook's docstring) -- calling stop() does not
  // mean the last segment is ready yet, so the actual submit is deferred to here.
  useEffect(() => {
    if (!stopRequestedRef.current) return;
    if (recorder.isRecording) return;
    if (recorder.audioSegments.length === 0) return;
    stopRequestedRef.current = false;
    const segments = recorder.audioSegments;
    recorder.reset();
    void submitTurn(segments);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [recorder.isRecording, recorder.audioSegments]);

  // Stop any in-flight recording/playback if the overlay unmounts uncleanly.
  useEffect(() => {
    return () => {
      audioRef.current?.pause();
      if (audioUrlRef.current) URL.revokeObjectURL(audioUrlRef.current);
      recorder.stop();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  function handleMicTap() {
    if (phase === "listening") {
      stopRequestedRef.current = true;
      setPhase("processing");
      recorder.stop();
      return;
    }
    if (phase === "idle" || phase === "error") {
      setError(null);
      setResponseText(null);
      setPhase("listening");
      void recorder.start();
    }
  }

  async function submitTurn(segments: Blob[]) {
    if (!token) return;
    try {
      const result = await api.askJanMitraVoice(token, {
        language: lang,
        conversation_history: history,
        audioSegments: segments,
        image: attachedImage[0] ?? null,
      });
      setTranscript(result.question);
      setResponseText(result.answer);
      setHistory((prev) => [
        ...prev,
        { role: "user", content: result.question },
        { role: "assistant", content: result.answer },
      ]);
      // Only clear on success -- a failed request keeps the attached photo so the citizen can
      // just retry, matching AskJanMitra.tsx's own text/image submit behavior.
      setAttachedImage([]);

      if (result.audio_base64) {
        playAudio(result.audio_base64, result.audio_format);
      } else {
        // TTS failed server-side -- a real, honest degrade: the text answer above is already
        // real, there's just no audio to play. Never fabricate/placeholder audio here.
        setPhase("idle");
      }
    } catch (err) {
      setError(err instanceof ApiError ? err.message : t(lang, "ask.voiceAssistant.errorGeneric"));
      setPhase("error");
    }
  }

  function playAudio(audioBase64: string, format: string) {
    const byteChars = atob(audioBase64);
    const bytes = new Uint8Array(byteChars.length);
    for (let i = 0; i < byteChars.length; i++) bytes[i] = byteChars.charCodeAt(i);
    const blob = new Blob([bytes], { type: `audio/${format}` });
    const url = URL.createObjectURL(blob);
    audioUrlRef.current = url;

    const audioEl = new Audio(url);
    audioEl.muted = muted;
    audioRef.current = audioEl;

    audioEl.onplaying = () => setAudioPlaying(true);
    audioEl.onpause = () => setAudioPlaying(false);
    audioEl.onended = () => {
      setAudioPlaying(false);
      setPhase("idle");
      URL.revokeObjectURL(url);
      audioUrlRef.current = null;
    };
    audioEl.onerror = () => {
      setAudioPlaying(false);
      setPhase("idle");
    };

    setPhase("speaking");
    audioEl.play().catch(() => {
      setAudioPlaying(false);
      setPhase("idle");
    });
  }

  function toggleMute() {
    setMuted((prev) => {
      const next = !prev;
      if (audioRef.current) audioRef.current.muted = next;
      return next;
    });
  }

  function handleEnd() {
    audioRef.current?.pause();
    recorder.stop();
    onClose();
  }

  const mascotState: MascotState =
    phase === "listening" ? "listening"
    : phase === "processing" ? "thinking"
    : audioPlaying ? "speaking"
    : "idle";

  return (
    <div className="voice-overlay-backdrop" onClick={handleEnd}>
      <div
        className="voice-overlay-panel"
        role="dialog"
        aria-modal="true"
        aria-label={t(lang, "ask.voiceAssistant.title")}
        onClick={(e) => e.stopPropagation()}
      >
        <button
          type="button"
          className="voice-overlay-close"
          aria-label={t(lang, "ask.voiceAssistant.close")}
          onClick={handleEnd}
        >
          ✕
        </button>

        {/* The animated glow is purely decorative (aria-hidden) and keyed off `phase`, not
            `mascotState` -- phase has a real "error" state mascotState collapses into "idle",
            and the glow should visibly dim/redden on error rather than keep pulsing like
            nothing's wrong. */}
        <div className={`voice-orb voice-orb-${phase}`}>
          <div className="voice-orb-glow" aria-hidden="true" />
          <div className="voice-overlay-mascot">
            <Mascot state={mascotState} size={80} />
          </div>
        </div>

        <div className="voice-overlay-state" aria-live="polite">
          {t(lang, `ask.voiceAssistant.state.${phase}`)}
        </div>

        <div className="voice-overlay-language">{SUPPORTED_LANGUAGES[lang].name}</div>

        {/* Attaching a photo here is optional and only meaningful before/between turns -- a
            combined voice+image turn (see backend ask_janmitra_service.ask_voice()), reusing
            the exact same single-image attach control the text/image flow already uses. */}
        {(phase === "idle" || phase === "error") && (
          <MultiPhotoUpload photos={attachedImage} onChange={setAttachedImage} maxFiles={1} placeholderKey="ask.image.addLabel" />
        )}

        {transcript && (
          <div className="voice-overlay-transcript">
            <div className="voice-overlay-transcript-label">{t(lang, "ask.voiceAssistant.transcriptLabel")}</div>
            <p>{transcript}</p>
          </div>
        )}

        {responseText && (
          <div className="voice-overlay-transcript voice-overlay-response">
            <div className="voice-overlay-transcript-label">{t(lang, "ask.voiceAssistant.responseLabel")}</div>
            <p>{responseText}</p>
          </div>
        )}

        {error && <div className="banner-error">{error}</div>}
        {recorder.error && <div className="banner-error">{recorder.error}</div>}

        <div className="voice-overlay-controls">
          <button
            type="button"
            className="voice-overlay-mic"
            onClick={handleMicTap}
            disabled={phase === "processing" || phase === "speaking"}
            aria-pressed={phase === "listening"}
            aria-label={t(
              lang,
              phase === "listening" ? "ask.voiceAssistant.micControl.stop" : "ask.voiceAssistant.micControl.start"
            )}
          >
            {phase === "listening" ? (
              <svg width="26" height="26" viewBox="0 0 24 24" fill="none">
                <rect x="7" y="7" width="10" height="10" rx="2" fill="currentColor" />
              </svg>
            ) : (
              <svg width="26" height="26" viewBox="0 0 24 24" fill="none">
                <rect x="9" y="3" width="6" height="12" rx="3" stroke="currentColor" strokeWidth="1.8" />
                <path d="M5 11a7 7 0 0 0 14 0M12 18v3" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
              </svg>
            )}
          </button>

          {phase === "listening" && <span className="voice-overlay-seconds mono">{recorder.seconds}s</span>}

          <button
            type="button"
            className="btn btn-ghost btn-sm"
            onClick={toggleMute}
            aria-pressed={muted}
            aria-label={t(lang, muted ? "ask.voiceAssistant.unmute" : "ask.voiceAssistant.mute")}
          >
            {muted ? "🔇" : "🔊"}
          </button>

          <button type="button" className="btn btn-ghost btn-sm" onClick={handleEnd}>
            {t(lang, "ask.voiceAssistant.endConversation")}
          </button>
        </div>

        {phase === "error" && (
          <button type="button" className="btn btn-primary btn-sm" onClick={() => setPhase("idle")}>
            {t(lang, "ask.voiceAssistant.tryAgain")}
          </button>
        )}

        <p className="voice-overlay-note">{t(lang, "ask.voiceAssistant.turnBasedNote")}</p>
      </div>
    </div>
  );
}

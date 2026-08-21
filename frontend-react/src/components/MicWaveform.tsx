/** Small animated equalizer-style waveform -- real-time visual feedback that a mic is actively
 * listening, for the SIMPLE voice-input path (speech-to-text filling a text field) on both the
 * Ask Sarthi composer's own mic and the Report an Issue wizard's voice recorder.
 *
 * Deliberately NOT reused from VoiceAssistantOverlay's orb-glow effect (see that component's own
 * CSS) -- that one is a large, full-screen modal animation built specifically around the mascot
 * character for the separate voice-TO-voice conversation experience ("Mic 2"). This is a small,
 * inline, CSS-only bar animation sized to sit directly on/beside a compact mic button, with no
 * JS-driven audio analysis -- a rhythmic pulse standing in for "listening", not a literal
 * amplitude visualization of the real audio (the browser's SpeechRecognition/MediaRecorder APIs
 * this app uses don't expose live amplitude data to draw a true one from anyway). */
export default function MicWaveform() {
  return (
    <span className="mic-waveform" aria-hidden="true">
      <span />
      <span />
      <span />
      <span />
      <span />
    </span>
  );
}

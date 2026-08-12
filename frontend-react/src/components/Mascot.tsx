/** JanMitra's mascot -- the actual character the user supplied (cropped from their own
 * reference character sheet: "ChatGPT Image Aug 10, 2026, 06_20_08 PM.png", the green-vest/
 * white-cap "जनमित्र" branded municipal assistant), not a hand-drawn placeholder. Background
 * removed (flood-filled from the image edges, so only the connected white backdrop goes
 * transparent -- the character's own white clothing stays intact) and each pose downscaled to
 * a sensible on-screen size (public/mascot/*.png, ~40-55KB each, well under the "don't load
 * huge character assets" guidance).
 *
 * Deliberately does NOT use the sheet's own baked-in speech-bubble poses (e.g. "नमस्कार! मैं
 * जनमित्र AI आपका स्वागत करता हूँ") -- this app supports 6 languages via i18n.ts, and a phrase
 * baked into a raster image would only ever render in whichever language it happened to be
 * generated in, regardless of the citizen's actual selected language. All 5 crops here are the
 * character ALONE; any accompanying text (the greeting bubble, etc.) stays real, translated UI
 * text rendered next to the image, same as before.
 *
 * Each state is real application state, never a proxy -- see AskJanMitraWidget.tsx and
 * AskJanMitra.tsx's AskJanMitraContent for exactly what drives each one. There is deliberately
 * no "error" state: an error is already communicated by the existing text error banner, so the
 * mascot just stays idle rather than performing an emotion this 5-state set doesn't have.
 */

export type MascotState = "idle" | "greeting" | "thinking" | "listening" | "success";

// Each source crop has its own natural aspect ratio (a person, not a square icon) -- rather than
// stretch/pad every state to a fixed square, `size` below controls height and each image keeps
// its own width via these ratios, sampled directly from the actual asset dimensions.
const ASPECT: Record<MascotState, number> = {
  idle: 189 / 240,
  greeting: 126 / 240,
  thinking: 92 / 240,
  listening: 108 / 240,
  success: 142 / 240,
};

export default function Mascot({ state, size = 40 }: { state: MascotState; size?: number }) {
  return (
    <img
      src={`/mascot/mascot-${state}.png`}
      alt=""
      className={`mascot mascot-${state}`}
      style={{ height: size, width: size * ASPECT[state], display: "block", objectFit: "contain" }}
    />
  );
}

import { useNavigate } from "react-router-dom";
import { useUiLang } from "../lib/uiLang";
import type { LangCode } from "../lib/i18n";
import "./LanguageGate.css";

const OPTIONS: { code: LangCode; native: string; gloss: string }[] = [
  { code: "mr", native: "मराठी", gloss: "Marathi" },
  { code: "hi", native: "हिंदी", gloss: "Hindi" },
  { code: "en", native: "English", gloss: "English" },
];

export default function LanguageGate() {
  const { setLang } = useUiLang();
  const navigate = useNavigate();

  function choose(code: LangCode) {
    setLang(code);
    navigate("/welcome");
  }

  return (
    <div className="gate">
      <div className="gate-card">
        <div className="gate-seal">JM</div>
        <h1 className="gate-title display">
          Choose your language · तुमची भाषा निवडा · अपनी भाषा चुनें
        </h1>
        <p className="gate-sub">You can change this anytime later in Settings</p>
        <div className="gate-options">
          {OPTIONS.map((opt) => (
            <button key={opt.code} className="gate-opt" onClick={() => choose(opt.code)}>
              <span className="gate-opt-label">
                <span className={`native ${opt.code !== "en" ? "devanagari" : ""}`}>{opt.native}</span>
                {opt.code !== "en" && <span className="gloss">{opt.gloss}</span>}
              </span>
              <span className="arrow">→</span>
            </button>
          ))}
        </div>
        <p className="gate-note">
          Used to decide what language JanMitra AI shows you in — nothing is sent anywhere yet.
        </p>
      </div>
    </div>
  );
}

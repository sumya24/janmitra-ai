import { Link } from "react-router-dom";
import { useUiLang } from "../lib/uiLang";
import { SUPPORTED_LANGUAGES, t } from "../lib/i18n";
import "./Landing.css";

export default function Landing() {
  const { lang } = useUiLang();

  return (
    <div>
      <nav className="landingnav">
        <div className="brand">
          <div className="seal">JM</div>
          <div className="brand-word display">JanMitra AI</div>
        </div>
        <div className="navactions">
          <Link to="/" className="lang-badge">
            {SUPPORTED_LANGUAGES[lang].name}
          </Link>
          <Link to="/login" className="btn btn-ghost btn-sm">
            {t(lang, "landing.login")}
          </Link>
          <Link to="/signup" className="btn btn-primary btn-sm">
            {t(lang, "landing.signup")}
          </Link>
        </div>
      </nav>

      <div className="hero">
        <div className="hero-copy">
          <div className="eyebrow">Municipal grievance redressal</div>
          <h1 className="display">{t(lang, "hero.headline")}</h1>
          <p className="lede">{t(lang, "hero.sub")}</p>
          <div className="hero-ctas">
            <Link to="/signup" className="btn btn-primary">
              {t(lang, "hero.cta.primary")}
            </Link>
            <Link to="/login" className="btn btn-ghost">
              {t(lang, "hero.cta.secondary")}
            </Link>
          </div>
        </div>
        <div className="hero-visual">
          <svg viewBox="0 0 380 300" width="100%" style={{ display: "block", height: "auto" }}>
            <rect x="18" y="40" width="110" height="220" rx="20" fill="var(--surface)" stroke="var(--line)" strokeWidth="2" />
            <rect x="34" y="64" width="78" height="150" rx="8" fill="var(--paper)" />
            <circle cx="73" cy="132" r="22" fill="var(--status-progress-bg)" stroke="var(--status-progress)" strokeWidth="2" />
            <path d="M73 122a8 8 0 0 1 8 8v6a8 8 0 0 1-16 0v-6a8 8 0 0 1 8-8Z" fill="var(--status-progress)" />
            <path d="M62 138a11 11 0 0 0 22 0M73 149v7" stroke="var(--status-progress)" strokeWidth="2.2" fill="none" strokeLinecap="round" />
            <rect x="50" y="175" width="46" height="7" rx="3.5" fill="var(--line)" />
            <rect x="58" y="188" width="30" height="7" rx="3.5" fill="var(--line)" />
            <rect x="252" y="40" width="110" height="220" rx="20" fill="var(--surface)" stroke="var(--line)" strokeWidth="2" />
            <rect x="268" y="64" width="78" height="150" rx="8" fill="var(--paper)" />
            <rect x="280" y="86" width="54" height="8" rx="4" fill="var(--status-resolved)" opacity="0.85" />
            <rect x="280" y="102" width="40" height="8" rx="4" fill="var(--line)" />
            <rect x="280" y="118" width="48" height="8" rx="4" fill="var(--line)" />
            <circle cx="307" cy="160" r="16" fill="var(--status-resolved-bg)" stroke="var(--status-resolved)" strokeWidth="2" />
            <path d="M300 160l5 5 9-10" stroke="var(--status-resolved)" strokeWidth="2.4" fill="none" strokeLinecap="round" strokeLinejoin="round" />
            <path d="M138 130c34-6 58-6 96 0" stroke="var(--accent)" strokeWidth="2.5" fill="none" strokeDasharray="1 8" strokeLinecap="round" />
            <path d="M222 122l14 8-14 8" stroke="var(--accent)" strokeWidth="2.5" fill="none" strokeLinecap="round" strokeLinejoin="round" />
          </svg>
        </div>
      </div>
    </div>
  );
}

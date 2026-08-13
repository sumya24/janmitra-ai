import { t, type LangCode } from "../lib/i18n";

/** The branded left panel shared by Login and Signup — fills what used to be empty background
 * around a lonely centered card with the same value proposition shown on the landing page,
 * restated for someone who's already decided to sign up or log in. Hidden on narrow screens
 * (see Auth.css) where there isn't room for it without crowding the actual form. */
export default function AuthPanel({ lang }: { lang: LangCode }) {
  return (
    <div className="auth-panel">
      <div className="auth-panel-brand">
        {/* Centered, no separate text beside it -- adding a duplicate "JanSarthi AI" label next
         * to the image (which already has the wordmark baked in) read as redundant rather than
         * filling space well. The image alone, centered, is the cleaner result. */}
        <img src="/brand/logo-lockup.png" alt="JanSarthi AI" className="auth-panel-mark" />
      </div>

      <div className="auth-panel-body">
        <h2 className="display">{t(lang, "auth.panel.title")}</h2>
        <p>{t(lang, "auth.panel.subtitle")}</p>
        <ul className="auth-panel-points">
          <li>
            <span className="tick">✓</span>
            {t(lang, "auth.panel.point1")}
          </li>
          <li>
            <span className="tick">✓</span>
            {t(lang, "auth.panel.point2")}
          </li>
          <li>
            <span className="tick">✓</span>
            {t(lang, "auth.panel.point3")}
          </li>
        </ul>
      </div>

      <div className="auth-panel-foot">{t(lang, "topbar.subtitle")}</div>
    </div>
  );
}

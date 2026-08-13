import { useState } from "react";
import { useAuth } from "../lib/auth";
import { useUiLang } from "../lib/uiLang";
import { SUPPORTED_LANGUAGES, t, type LangCode } from "../lib/i18n";
import { api, ApiError } from "../lib/api";

export default function SettingsModal({ onClose, onLogout }: { onClose: () => void; onLogout: () => void }) {
  const { user, token, updateUser } = useAuth();
  const { lang, setLang } = useUiLang();
  const [fullName, setFullName] = useState(user?.full_name ?? "");
  const [language, setLanguage] = useState<LangCode>((user?.preferred_language as LangCode) ?? "en");
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  async function handleSave() {
    if (!token) return;
    setSaving(true);
    setError(null);
    try {
      const updated = await api.updateMe(token, { full_name: fullName.trim(), preferred_language: language });
      updateUser(updated);
      setLang(language); // instant — dashboards/TopBar/complaint list follow immediately, no reload
      onClose();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : t(lang, "settings.error"));
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="overlay" onClick={(e) => e.target === e.currentTarget && onClose()}>
      <div className="modal">
        <div className="modal-head">
          <h3 className="display">{t(lang, "settings.title")}</h3>
          <button className="x" aria-label={t(lang, "common.close")} onClick={onClose}>
            ✕
          </button>
        </div>

        {error && <div className="banner-error">{error}</div>}

        <div className="field">
          <label htmlFor="settings-name">{t(lang, "settings.fullName")}</label>
          <input id="settings-name" type="text" value={fullName} onChange={(e) => setFullName(e.target.value)} />
        </div>
        <div className="field">
          <label htmlFor="settings-phone">{t(lang, "settings.phone")}</label>
          <input id="settings-phone" type="tel" value={user?.phone ?? ""} disabled />
        </div>
        {user?.role === "citizen" && (
          <div className="field">
            <label htmlFor="settings-ward">{t(lang, "citizen.ward")}</label>
            <input id="settings-ward" type="text" value={user?.ward || t(lang, "area.noWardSet")} disabled />
          </div>
        )}
        <div className="field">
          <label id="settings-language-label">{t(lang, "settings.preferredLanguage")}</label>
          <div className="langpills">
            {(Object.keys(SUPPORTED_LANGUAGES) as LangCode[]).map((code) => (
              <button
                key={code}
                type="button"
                className={`langpill ${language === code ? "active" : ""}`}
                onClick={() => setLanguage(code)}
              >
                {SUPPORTED_LANGUAGES[code].name}
              </button>
            ))}
          </div>
        </div>
        <p style={{ fontSize: 11.5, color: "var(--ink-3)", marginTop: 10 }}>
          {t(lang, "settings.languageHelp")}
        </p>

        <div className="modal-actions">
          <button className="btn btn-ghost" onClick={onLogout}>
            {t(lang, "settings.logout")}
          </button>
          <button className="btn btn-primary" onClick={handleSave} disabled={saving}>
            {saving ? t(lang, "settings.saving") : t(lang, "settings.save")}
          </button>
        </div>
      </div>
    </div>
  );
}

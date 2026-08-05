import { useState } from "react";
import { useAuth } from "../lib/auth";
import { SUPPORTED_LANGUAGES, type LangCode } from "../lib/i18n";
import { api, ApiError } from "../lib/api";

export default function SettingsModal({ onClose, onLogout }: { onClose: () => void; onLogout: () => void }) {
  const { user, token, updateUser } = useAuth();
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
      onClose();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Could not save changes. Please try again.");
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="overlay" onClick={(e) => e.target === e.currentTarget && onClose()}>
      <div className="modal">
        <div className="modal-head">
          <h3 className="display">Profile &amp; settings</h3>
          <button className="x" aria-label="Close" onClick={onClose}>
            ✕
          </button>
        </div>

        {error && <div className="banner-error">{error}</div>}

        <div className="field">
          <label htmlFor="settings-name">Full name</label>
          <input id="settings-name" type="text" value={fullName} onChange={(e) => setFullName(e.target.value)} />
        </div>
        <div className="field">
          <label htmlFor="settings-phone">Phone number</label>
          <input id="settings-phone" type="tel" value={user?.phone ?? ""} disabled />
        </div>
        <div className="field">
          <label id="settings-language-label">Preferred language</label>
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
          This changes the language JanMitra AI shows you — complaint forms, notifications, everything.
        </p>

        <div className="modal-actions">
          <button className="btn btn-ghost" onClick={onLogout}>
            Log out
          </button>
          <button className="btn btn-primary" onClick={handleSave} disabled={saving}>
            {saving ? "Saving…" : "Save changes"}
          </button>
        </div>
      </div>
    </div>
  );
}

import { useState } from "react";
import { useAuth } from "../lib/auth";
import { useUiLang } from "../lib/uiLang";
import { SUPPORTED_LANGUAGES, t, type LangCode } from "../lib/i18n";
import { api, ApiError } from "../lib/api";
import { useModalA11y } from "../lib/useModalA11y";

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

  // Collapsed by default -- own section, own fields, own submit action, deliberately separate
  // from the profile Save button above (changing a password is a materially different, more
  // sensitive action than editing a display name). Previously there was no way for a citizen to
  // change their own password at all -- see backend/routes/auth.py's change-password endpoint.
  const [showChangePassword, setShowChangePassword] = useState(false);
  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmNewPassword, setConfirmNewPassword] = useState("");
  const [passwordFieldErrors, setPasswordFieldErrors] = useState<Record<string, boolean>>({});
  const [passwordError, setPasswordError] = useState<string | null>(null);
  const [passwordSuccess, setPasswordSuccess] = useState(false);
  const [changingPassword, setChangingPassword] = useState(false);

  // Same client-side echo of the server's rule as Signup.tsx -- see that file's own comment.
  const newPasswordTooWeak =
    newPassword.length > 0 && (newPassword.length < 8 || !/[A-Za-z]/.test(newPassword) || !/\d/.test(newPassword));

  async function handleChangePassword() {
    if (!token) return;
    setPasswordError(null);
    setPasswordSuccess(false);

    const errors: Record<string, boolean> = {};
    if (!currentPassword) errors.currentPassword = true;
    if (!newPassword || newPasswordTooWeak) errors.newPassword = true;
    if (!confirmNewPassword || confirmNewPassword !== newPassword) errors.confirmNewPassword = true;
    setPasswordFieldErrors(errors);
    if (Object.keys(errors).length > 0) return;

    setChangingPassword(true);
    try {
      await api.changePassword(token, { current_password: currentPassword, new_password: newPassword });
      // Backend revokes every OTHER refresh token on a successful change (see that endpoint's
      // own docstring) -- this session's own tokens are untouched, so no re-login needed here.
      setPasswordSuccess(true);
      setCurrentPassword("");
      setNewPassword("");
      setConfirmNewPassword("");
    } catch (err) {
      setPasswordError(err instanceof ApiError ? err.message : t(lang, "common.somethingWrong"));
    } finally {
      setChangingPassword(false);
    }
  }

  const modalRef = useModalA11y(onClose);

  return (
    <div className="overlay" onClick={(e) => e.target === e.currentTarget && onClose()}>
      <div ref={modalRef} className="modal" role="dialog" aria-modal="true" aria-labelledby="jm-modal-title" tabIndex={-1}>
        <div className="modal-head">
          <h3 className="display" id="jm-modal-title">{t(lang, "settings.title")}</h3>
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

        <hr style={{ border: "none", borderTop: "1px solid var(--line)", margin: "16px 0" }} />

        {!showChangePassword ? (
          <button type="button" className="btn btn-ghost btn-sm" onClick={() => setShowChangePassword(true)}>
            {t(lang, "auth.changePassword.title")}
          </button>
        ) : (
          <div>
            <h4 style={{ margin: "0 0 10px" }}>{t(lang, "auth.changePassword.title")}</h4>
            {passwordError && <div className="banner-error">{passwordError}</div>}
            {passwordSuccess && <div className="banner-success">{t(lang, "auth.changePassword.success")}</div>}
            <div className={`field ${passwordFieldErrors.currentPassword ? "has-error" : ""}`}>
              <label htmlFor="settings-current-password">{t(lang, "auth.changePassword.current")}</label>
              <input
                id="settings-current-password"
                type="password"
                value={currentPassword}
                onChange={(e) => setCurrentPassword(e.target.value)}
                aria-invalid={passwordFieldErrors.currentPassword || undefined}
              />
              {passwordFieldErrors.currentPassword && (
                <div className="field-error">{t(lang, "common.fieldRequired")}</div>
              )}
            </div>
            <div className={`field ${passwordFieldErrors.newPassword ? "has-error" : ""}`}>
              <label htmlFor="settings-new-password">{t(lang, "auth.changePassword.new")}</label>
              <input
                id="settings-new-password"
                type="password"
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
                aria-invalid={passwordFieldErrors.newPassword || undefined}
              />
              {passwordFieldErrors.newPassword ? (
                <div className="field-error">{t(lang, newPassword ? "auth.field.passwordWeak" : "common.fieldRequired")}</div>
              ) : (
                <div className="field-hint">{t(lang, "auth.field.passwordHint")}</div>
              )}
            </div>
            <div className={`field ${passwordFieldErrors.confirmNewPassword ? "has-error" : ""}`}>
              <label htmlFor="settings-confirm-new-password">{t(lang, "auth.changePassword.confirmNew")}</label>
              <input
                id="settings-confirm-new-password"
                type="password"
                value={confirmNewPassword}
                onChange={(e) => setConfirmNewPassword(e.target.value)}
                aria-invalid={passwordFieldErrors.confirmNewPassword || undefined}
              />
              {passwordFieldErrors.confirmNewPassword && (
                <div className="field-error">
                  {t(lang, confirmNewPassword ? "auth.field.passwordMismatch" : "common.fieldRequired")}
                </div>
              )}
            </div>
            <button type="button" className="btn btn-primary btn-sm" onClick={handleChangePassword} disabled={changingPassword}>
              {changingPassword ? t(lang, "settings.saving") : t(lang, "auth.changePassword.button")}
            </button>
          </div>
        )}

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

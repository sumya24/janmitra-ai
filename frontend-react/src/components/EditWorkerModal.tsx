import { useState, type FormEvent } from "react";
import { useAuth } from "../lib/auth";
import { useUiLang } from "../lib/uiLang";
import { SUPPORTED_LANGUAGES, t, type LangCode } from "../lib/i18n";
import { api, ApiError, type WorkerSummary } from "../lib/api";
import { useToast } from "../lib/toast";

/** Edits a worker's profile (name/ward/language) and, optionally in the same submit, resets
 * their password -- two separate backend calls (PATCH .../workers/{id} and POST
 * .../workers/{id}/reset-password, see backend/routes/admin.py) sequenced behind one form,
 * since from the admin's point of view "fix this worker's account" is one action whether or
 * not a password reset happens to be part of it this time. */
export default function EditWorkerModal({
  worker,
  onClose,
  onUpdated,
}: {
  worker: WorkerSummary;
  onClose: () => void;
  onUpdated: () => void;
}) {
  const { token } = useAuth();
  const { lang } = useUiLang();
  const [fullName, setFullName] = useState(worker.full_name);
  const [ward, setWard] = useState(worker.ward ?? "");
  const [language, setLanguage] = useState<LangCode>((worker.preferred_language as LangCode) || "en");
  const [newPassword, setNewPassword] = useState("");
  const [fieldErrors, setFieldErrors] = useState<Record<string, boolean>>({});
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);
  const toast = useToast();

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);

    const errors: Record<string, boolean> = {};
    if (!fullName.trim()) errors.fullName = true;
    if (!ward.trim()) errors.ward = true;
    if (newPassword && newPassword.length < 6) errors.newPassword = true;
    setFieldErrors(errors);
    if (Object.keys(errors).length > 0) return;

    if (!token) return;
    setSaving(true);
    try {
      await api.updateWorker(token, worker.id, {
        full_name: fullName.trim(),
        ward: ward.trim(),
        preferred_language: language,
      });
      if (newPassword) {
        await api.resetWorkerPassword(token, worker.id, newPassword);
      }
      toast.success(`${t(lang, "admin.workerUpdatedToast")} ${fullName.trim()}`);
      onUpdated();
      onClose();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : t(lang, "admin.workerUpdateErrFailed"));
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="overlay" onClick={(e) => e.target === e.currentTarget && !saving && onClose()}>
      <div className="modal">
        <div className="modal-head">
          <h3 className="display">{t(lang, "admin.editWorkerTitle")}</h3>
          <button className="x" aria-label={t(lang, "common.close")} onClick={onClose} disabled={saving}>
            ✕
          </button>
        </div>

        {error && <div className="banner-error">{error}</div>}

        <form onSubmit={handleSubmit} noValidate>
          <div className={`field ${fieldErrors.fullName ? "has-error" : ""}`}>
            <label htmlFor="edit-worker-name">{t(lang, "addWorker.fullName")}</label>
            <input id="edit-worker-name" type="text" value={fullName} onChange={(e) => setFullName(e.target.value)} />
            {fieldErrors.fullName && <div className="field-error">{t(lang, "common.fieldRequired")}</div>}
          </div>
          <div className={`field ${fieldErrors.ward ? "has-error" : ""}`}>
            <label htmlFor="edit-worker-ward">{t(lang, "addWorker.ward")}</label>
            <input id="edit-worker-ward" type="text" value={ward} onChange={(e) => setWard(e.target.value)} />
            {fieldErrors.ward && <div className="field-error">{t(lang, "common.fieldRequired")}</div>}
          </div>
          <div className="field">
            <label id="edit-worker-language-label">{t(lang, "addWorker.preferredLanguage")}</label>
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
          <div className={`field ${fieldErrors.newPassword ? "has-error" : ""}`}>
            <label htmlFor="edit-worker-password">{t(lang, "admin.editWorkerNewPassword")}</label>
            <input
              id="edit-worker-password"
              type="text"
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
              placeholder={t(lang, "admin.editWorkerNewPasswordPlaceholder")}
            />
            {fieldErrors.newPassword ? (
              <div className="field-error">{t(lang, "admin.editWorkerPasswordTooShort")}</div>
            ) : (
              <p style={{ fontSize: 11.5, color: "var(--ink-3)", marginTop: 5 }}>{t(lang, "admin.editWorkerPasswordHint")}</p>
            )}
          </div>

          <div className="modal-actions">
            <button type="button" className="btn btn-ghost" onClick={onClose} disabled={saving}>
              {t(lang, "addWorker.cancel")}
            </button>
            <button type="submit" className="btn btn-primary" disabled={saving}>
              {saving ? t(lang, "admin.savingWorker") : t(lang, "admin.saveWorker")}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

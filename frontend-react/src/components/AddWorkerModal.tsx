import { useState, type FormEvent } from "react";
import { useAuth } from "../lib/auth";
import { useUiLang } from "../lib/uiLang";
import { SUPPORTED_LANGUAGES, t, type LangCode } from "../lib/i18n";
import { api, ApiError } from "../lib/api";

export default function AddWorkerModal({ onClose, onCreated }: { onClose: () => void; onCreated: () => void }) {
  const { token } = useAuth();
  const { lang } = useUiLang();
  const [fullName, setFullName] = useState("");
  const [phone, setPhone] = useState("");
  const [password, setPassword] = useState("");
  const [ward, setWard] = useState("");
  const [language, setLanguage] = useState<LangCode>("mr");
  const [fieldErrors, setFieldErrors] = useState<Record<string, boolean>>({});
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);

    const errors: Record<string, boolean> = {};
    if (!fullName.trim()) errors.fullName = true;
    if (!phone.trim()) errors.phone = true;
    if (!password) errors.password = true;
    if (!ward.trim()) errors.ward = true;
    setFieldErrors(errors);
    if (Object.keys(errors).length > 0) return;

    if (!token) return;
    setSaving(true);
    try {
      await api.createWorker(token, {
        full_name: fullName.trim(),
        phone: phone.trim(),
        password,
        ward: ward.trim(),
        preferred_language: language,
      });
      onCreated();
      onClose();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : t(lang, "addWorker.errFailed"));
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="overlay" onClick={(e) => e.target === e.currentTarget && onClose()}>
      <div className="modal">
        <div className="modal-head">
          <h3 className="display">{t(lang, "addWorker.title")}</h3>
          <button className="x" aria-label={t(lang, "common.close")} onClick={onClose}>
            ✕
          </button>
        </div>
        <div className="modal-note">
          {t(lang, "addWorker.note")}
        </div>

        {error && <div className="banner-error">{error}</div>}

        <form onSubmit={handleSubmit} noValidate>
          <div className={`field ${fieldErrors.fullName ? "has-error" : ""}`}>
            <label htmlFor="worker-name">{t(lang, "addWorker.fullName")}</label>
            <input id="worker-name" type="text" value={fullName} onChange={(e) => setFullName(e.target.value)} placeholder={t(lang, "addWorker.fullNamePlaceholder")} />
            {fieldErrors.fullName && <div className="field-error">{t(lang, "common.fieldRequired")}</div>}
          </div>
          <div className={`field ${fieldErrors.phone ? "has-error" : ""}`}>
            <label htmlFor="worker-phone">{t(lang, "addWorker.phone")}</label>
            <input id="worker-phone" type="tel" value={phone} onChange={(e) => setPhone(e.target.value)} placeholder="98xxxxxxxx" />
            {fieldErrors.phone && <div className="field-error">{t(lang, "common.fieldRequired")}</div>}
          </div>
          <div className={`field ${fieldErrors.password ? "has-error" : ""}`}>
            <label htmlFor="worker-password">{t(lang, "addWorker.tempPassword")}</label>
            <input id="worker-password" type="text" value={password} onChange={(e) => setPassword(e.target.value)} />
            {fieldErrors.password && <div className="field-error">{t(lang, "common.fieldRequired")}</div>}
          </div>
          <div className={`field ${fieldErrors.ward ? "has-error" : ""}`}>
            <label htmlFor="worker-ward">{t(lang, "addWorker.ward")}</label>
            <input id="worker-ward" type="text" value={ward} onChange={(e) => setWard(e.target.value)} placeholder={t(lang, "addWorker.wardPlaceholder")} />
            {fieldErrors.ward && <div className="field-error">{t(lang, "common.fieldRequired")}</div>}
          </div>
          <div className="field">
            <label id="worker-language-label">{t(lang, "addWorker.preferredLanguage")}</label>
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

          <div className="modal-actions">
            <button type="button" className="btn btn-ghost" onClick={onClose}>
              {t(lang, "addWorker.cancel")}
            </button>
            <button type="submit" className="btn btn-primary" disabled={saving}>
              {saving ? t(lang, "addWorker.submitting") : t(lang, "addWorker.submit")}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

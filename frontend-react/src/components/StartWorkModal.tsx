import { useState, type FormEvent } from "react";
import { useAuth } from "../lib/auth";
import { useUiLang } from "../lib/uiLang";
import { t } from "../lib/i18n";
import { api, ApiError, type Complaint } from "../lib/api";
import MultiPhotoUpload from "./MultiPhotoUpload";

/** Mandatory initial-assessment modal, shown only once a complaint is ACCEPTED. Submitting moves
 * the complaint straight to IN_PROGRESS (no separate "confirm start" step) -- see
 * backend/routes/complaints.py's start_work(): ACCEPTED -> Start Work -> mandatory assessment ->
 * Save -> IN_PROGRESS is one atomic action from the worker's point of view. */
export default function StartWorkModal({
  complaintId,
  onClose,
  onStarted,
}: {
  complaintId: number;
  onClose: () => void;
  onStarted: (updated: Complaint) => void;
}) {
  const { token } = useAuth();
  const { lang } = useUiLang();
  const [assessment, setAssessment] = useState("");
  const [photos, setPhotos] = useState<File[]>([]);
  const [fieldError, setFieldError] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    if (!assessment.trim()) {
      setFieldError(true);
      return;
    }
    if (!token) return;
    setSaving(true);
    try {
      const updated = await api.startWork(token, complaintId, assessment.trim(), photos);
      onStarted(updated);
      onClose();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : t(lang, "worker.start.errFailed"));
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="overlay" onClick={(e) => e.target === e.currentTarget && !saving && onClose()}>
      <div className="modal">
        <div className="modal-head">
          <h3 className="display">{t(lang, "worker.start.title")}</h3>
          <button className="x" aria-label={t(lang, "common.close")} onClick={onClose} disabled={saving}>
            ✕
          </button>
        </div>
        <div className="modal-note">{t(lang, "worker.start.note")}</div>

        {error && <div className="banner-error">{error}</div>}

        <form onSubmit={handleSubmit} noValidate>
          <div className={`field ${fieldError ? "has-error" : ""}`}>
            <label htmlFor="start-assessment">{t(lang, "worker.start.assessmentLabel")}</label>
            <textarea
              id="start-assessment"
              rows={4}
              value={assessment}
              onChange={(e) => {
                setAssessment(e.target.value);
                if (fieldError) setFieldError(false);
              }}
              placeholder={t(lang, "worker.start.assessmentPlaceholder")}
            />
            {fieldError && <div className="field-error">{t(lang, "worker.start.assessmentRequired")}</div>}
          </div>
          <div className="field">
            <label>{t(lang, "worker.start.photoLabel")}</label>
            <MultiPhotoUpload photos={photos} onChange={setPhotos} />
          </div>

          <div className="modal-actions">
            <button type="button" className="btn btn-ghost" onClick={onClose} disabled={saving}>
              {t(lang, "common.cancel")}
            </button>
            <button type="submit" className="btn btn-primary" disabled={saving}>
              {saving ? t(lang, "worker.start.submitting") : t(lang, "worker.start.confirm")}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

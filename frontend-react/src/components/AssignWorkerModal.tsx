import { useState, type FormEvent } from "react";
import { useAuth } from "../lib/auth";
import { useUiLang } from "../lib/uiLang";
import { t } from "../lib/i18n";
import { api, ApiError, type WorkerSummary } from "../lib/api";
import { useToast } from "../lib/toast";
import { useModalA11y } from "../lib/useModalA11y";

/** Manually assigns a complaint to a specific worker — the fix for a complaint stuck "pending"
 * because assign_next_worker's automatic ward-matching (see backend/services/
 * assignment_service.py) found nobody eligible. Deliberately lists EVERY worker, not just ones
 * in the complaint's own ward — an admin overriding the automatic match is exactly the case
 * where "the ward has nobody" is the problem being worked around. */
export default function AssignWorkerModal({
  complaintId,
  workers,
  onClose,
  onAssigned,
}: {
  complaintId: number;
  workers: WorkerSummary[];
  onClose: () => void;
  onAssigned: () => void;
}) {
  const { token } = useAuth();
  const { lang } = useUiLang();
  const [workerId, setWorkerId] = useState<number | "">("");
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);
  const toast = useToast();

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (!token || workerId === "") return;
    setSaving(true);
    setError(null);
    try {
      const result = await api.assignComplaint(token, complaintId, workerId);
      toast.success(`${t(lang, "admin.assignedToast")} ${result.assigned_worker_name ?? ""}`);
      onAssigned();
      onClose();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : t(lang, "admin.assignErrFailed"));
    } finally {
      setSaving(false);
    }
  }

  const modalRef = useModalA11y(onClose);

  return (
    <div className="overlay" onClick={(e) => e.target === e.currentTarget && !saving && onClose()}>
      <div ref={modalRef} className="modal" role="dialog" aria-modal="true" aria-labelledby="jm-modal-title" tabIndex={-1}>
        <div className="modal-head">
          <h3 className="display" id="jm-modal-title">{t(lang, "admin.assignModalTitle")}</h3>
          <button className="x" aria-label={t(lang, "common.close")} onClick={onClose} disabled={saving}>
            ✕
          </button>
        </div>

        {error && <div className="banner-error">{error}</div>}

        {workers.length === 0 ? (
          <p style={{ fontSize: 13.5, color: "var(--ink-2)" }}>{t(lang, "admin.assignModalNoWorkers")}</p>
        ) : (
          <form onSubmit={handleSubmit} noValidate>
            <div className="field">
              <label htmlFor="assign-worker-select">{t(lang, "admin.assignModalLabel")}</label>
              <select
                id="assign-worker-select"
                value={workerId}
                onChange={(e) => setWorkerId(e.target.value ? Number(e.target.value) : "")}
              >
                <option value="">{t(lang, "admin.assignModalPlaceholder")}</option>
                {workers.map((w) => (
                  <option key={w.id} value={w.id}>
                    {w.full_name} — {w.ward}
                  </option>
                ))}
              </select>
            </div>

            <div className="modal-actions">
              <button type="button" className="btn btn-ghost" onClick={onClose} disabled={saving}>
                {t(lang, "addWorker.cancel")}
              </button>
              <button type="submit" className="btn btn-primary" disabled={saving || workerId === ""}>
                {saving ? t(lang, "admin.assigning") : t(lang, "admin.assignModalSubmit")}
              </button>
            </div>
          </form>
        )}
      </div>
    </div>
  );
}

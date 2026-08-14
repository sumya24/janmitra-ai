import { useModalA11y } from "../lib/useModalA11y";

/** Generic confirm/cancel modal — reused for every destructive Admin action (delete worker,
 * delete complaint) rather than a bespoke confirm dialog per action. Purely presentational and
 * i18n-agnostic: the caller (which already has `lang`/`t`) passes in already-translated labels,
 * so this component has no i18n dependency of its own and can be reused for any future
 * confirm-before-you-act flow, not just Admin's. */
export default function ConfirmModal({
  title,
  message,
  confirmLabel,
  cancelLabel,
  closeLabel,
  danger = false,
  saving = false,
  onConfirm,
  onClose,
}: {
  title: string;
  message: string;
  confirmLabel: string;
  cancelLabel: string;
  closeLabel: string;
  danger?: boolean;
  saving?: boolean;
  onConfirm: () => void;
  onClose: () => void;
}) {
  const modalRef = useModalA11y(onClose);
  return (
    <div className="overlay" onClick={(e) => e.target === e.currentTarget && !saving && onClose()}>
      <div ref={modalRef} className="modal" style={{ maxWidth: 380 }} role="dialog" aria-modal="true" aria-label={title} tabIndex={-1}>
        <div className="modal-head">
          <h3 className="display">{title}</h3>
          <button className="x" aria-label={closeLabel} onClick={onClose} disabled={saving}>
            ✕
          </button>
        </div>
        <p style={{ fontSize: 13.5, color: "var(--ink-2)", lineHeight: 1.5, margin: 0 }}>{message}</p>
        <div className="modal-actions">
          <button type="button" className="btn btn-ghost" onClick={onClose} disabled={saving}>
            {cancelLabel}
          </button>
          <button type="button" className={danger ? "btn btn-danger" : "btn btn-primary"} onClick={onConfirm} disabled={saving}>
            {confirmLabel}
          </button>
        </div>
      </div>
    </div>
  );
}

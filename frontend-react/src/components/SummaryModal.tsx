import { useUiLang } from "../lib/uiLang";
import { t } from "../lib/i18n";
import type { Complaint } from "../lib/api";
import StatusBadge from "./StatusBadge";
import "../styles/dashboard.css";
import { useModalA11y } from "../lib/useModalA11y";

/** "Summary" -- a quick, no-extra-network-call glance at a complaint (id, status, filed date,
 * location, description, assigned worker), distinct from "View Report" (ReportModal /
 * ComplaintReportView), which fetches the full deterministic resolution report (evidence,
 * initial assessment, progress updates, timeline) plus download/share. Everything shown here is
 * already present on the row's own `Complaint` object, so opening this never triggers a fetch --
 * it's meant to be an instant look, not a smaller version of the report. */
export default function SummaryModal({
  complaint,
  statusLabel,
  onClose,
}: {
  complaint: Complaint;
  statusLabel: string;
  onClose: () => void;
}) {
  const { lang } = useUiLang();
  const location = [complaint.ward, complaint.location_ulb, complaint.location_district, complaint.location_state]
    .filter(Boolean)
    .join(", ");

  const modalRef = useModalA11y(onClose);

  return (
    <div className="overlay" onClick={(e) => e.target === e.currentTarget && onClose()}>
      <div ref={modalRef} className="modal" style={{ maxWidth: 460 }} role="dialog" aria-modal="true" aria-labelledby="jm-modal-title" tabIndex={-1}>
        <div className="modal-head">
          <h3 className="display" id="jm-modal-title">{t(lang, "worker.summary.title")}</h3>
          <button className="x" aria-label={t(lang, "common.close")} onClick={onClose}>
            ✕
          </button>
        </div>

        <div className="report-view">
          <dl className="report-fields">
            <dt>{t(lang, "worker.report.complaintId")}</dt>
            <dd className="mono">JM-{String(complaint.id).padStart(5, "0")}</dd>

            <dt>{t(lang, "admin.colStatus")}</dt>
            <dd>
              <StatusBadge status={complaint.status} label={statusLabel} />
            </dd>

            <dt>{t(lang, "worker.report.filedOn")}</dt>
            <dd>{new Date(complaint.created_at).toLocaleString()}</dd>

            <dt>{t(lang, "worker.report.description")}</dt>
            <dd>{complaint.display_summary || complaint.summary}</dd>

            {location && (
              <>
                <dt>{t(lang, "worker.report.location")}</dt>
                <dd>{location}{complaint.address ? ` (${complaint.address})` : ""}</dd>
              </>
            )}

            {complaint.assigned_worker_name && (
              <>
                <dt>{t(lang, "worker.report.assignedWorker")}</dt>
                <dd>{complaint.assigned_worker_name}</dd>
              </>
            )}
          </dl>
        </div>

        <div className="modal-actions">
          <button type="button" className="btn btn-ghost" onClick={onClose}>
            {t(lang, "common.close")}
          </button>
        </div>
      </div>
    </div>
  );
}

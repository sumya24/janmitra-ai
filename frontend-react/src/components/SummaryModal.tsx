import { useEffect, useState } from "react";
import { useAuth } from "../lib/auth";
import { useUiLang } from "../lib/uiLang";
import { t } from "../lib/i18n";
import { api, type Complaint, type ComplaintReport } from "../lib/api";
import StatusBadge from "./StatusBadge";
import ComplaintReportView from "./ComplaintReportView";
import "../styles/dashboard.css";
import { useModalA11y } from "../lib/useModalA11y";

/** "Summary" -- a quick glance at a complaint (id, status, filed date, location, description,
 * assigned worker) built entirely from the row's own `Complaint` object, so it always paints
 * instantly with no network call, for every status.
 *
 * For a RESOLVED complaint, it ALSO fetches and shows the same full resolution report "View
 * Report" (ReportModal) shows -- initial assessment, progress updates, completion, evidence,
 * status timeline -- so a citizen/worker/admin doesn't need to open a second modal to see it.
 * Only attempted when `complaint.status === "resolved"`: the backend's own report endpoint 404s
 * for anything earlier (see complaint_report_service.py), and there's genuinely no "assessment"/
 * "completion"/timeline content to show yet for an open complaint -- so this never fires a
 * guaranteed-404 request or flashes an error state for the common (non-resolved) case. If the
 * fetch itself fails for a resolved complaint (network issue), the quick fields above still
 * stand alone -- never a broken/empty-looking modal. */
export default function SummaryModal({
  complaint,
  statusLabel,
  onClose,
}: {
  complaint: Complaint;
  statusLabel: string;
  onClose: () => void;
}) {
  const { token } = useAuth();
  const { lang } = useUiLang();
  const location = [complaint.ward, complaint.location_ulb, complaint.location_district, complaint.location_state]
    .filter(Boolean)
    .join(", ");

  const [report, setReport] = useState<ComplaintReport | null>(null);

  useEffect(() => {
    if (!token || complaint.status !== "resolved") return;
    let cancelled = false;
    api
      .getComplaintReport(token, complaint.id)
      .then((r) => !cancelled && setReport(r))
      .catch(() => {
        /* Resolved but the full report couldn't be fetched -- the quick fields below already
         * cover the essentials, so this stays silent rather than showing an error banner over an
         * otherwise-working summary. */
      });
    return () => {
      cancelled = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token, complaint.id, complaint.status]);

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

        {report ? (
          <ComplaintReportView report={report} />
        ) : (
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
        )}

        <div className="modal-actions">
          <button type="button" className="btn btn-ghost" onClick={onClose}>
            {t(lang, "common.close")}
          </button>
        </div>
      </div>
    </div>
  );
}

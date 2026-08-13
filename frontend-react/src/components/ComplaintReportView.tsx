import { useUiLang } from "../lib/uiLang";
import { t } from "../lib/i18n";
import type { ComplaintReport } from "../lib/api";
import EvidenceGallery, { type GalleryItem } from "./EvidenceGallery";

function toItems(filePaths: string[]): GalleryItem[] {
  return filePaths.map((filePath) => ({ filePath }));
}

/** Renders the same real, deterministically-assembled report data the PDF download contains
 * (complaint + status history + worker updates + evidence -- never LLM-generated, see
 * backend/services/complaint_report_service.py). Pure presentational -- the caller
 * (ReportModal / WorkerComplaintDetail) owns fetching. */
export default function ComplaintReportView({ report }: { report: ComplaintReport }) {
  const { lang } = useUiLang();
  const location = [report.location_ward, report.location_ulb, report.location_district, report.location_state]
    .filter(Boolean)
    .join(", ");

  return (
    <div className="report-view">
      <div style={{ textAlign: "center", marginBottom: 16 }}>
        <div className="display" style={{ fontSize: 16, fontWeight: 700 }}>JanSarthi AI</div>
        <div style={{ fontSize: 11, color: "var(--ink-3)", textTransform: "uppercase", letterSpacing: "0.06em" }}>
          {t(lang, "worker.report.heading")}
        </div>
      </div>

      <dl className="report-fields">
        <dt>{t(lang, "worker.report.complaintId")}</dt>
        <dd className="mono">{report.display_id}</dd>

        <dt>{t(lang, "worker.report.filedOn")}</dt>
        <dd>{new Date(report.created_at).toLocaleString()}</dd>

        <dt>{t(lang, "worker.report.description")}</dt>
        <dd>{report.service_summary}{report.original_description && report.original_description !== report.service_summary ? ` — ${report.original_description}` : ""}</dd>
      </dl>

      {report.citizen_evidence.length > 0 && (
        <div className="report-section" style={{ marginTop: 0, borderTop: "none", paddingTop: 0 }}>
          <div className="section-label" style={{ marginTop: 0 }}>{t(lang, "evidence.citizenPhotos")}</div>
          <EvidenceGallery items={toItems(report.citizen_evidence)} />
        </div>
      )}

      <dl className="report-fields">
        {location && (
          <>
            <dt>{t(lang, "worker.report.location")}</dt>
            <dd>{location}{report.location_address ? ` (${report.location_address})` : ""}</dd>
          </>
        )}

        {report.assigned_worker_name && (
          <>
            <dt>{t(lang, "worker.report.assignedWorker")}</dt>
            <dd>{report.assigned_worker_name}</dd>
          </>
        )}
      </dl>

      {report.initial_assessment && (
        <div className="report-section">
          <div className="section-label">{t(lang, "worker.detail.initialAssessment")}</div>
          <p>{report.initial_assessment}</p>
          {report.initial_assessment_at && (
            <div style={{ fontSize: 11, color: "var(--ink-3)" }}>{new Date(report.initial_assessment_at).toLocaleString()}</div>
          )}
          {report.initial_assessment_evidence.length > 0 && (
            <div style={{ marginTop: 8 }}>
              <EvidenceGallery items={toItems(report.initial_assessment_evidence)} />
            </div>
          )}
        </div>
      )}

      {report.progress_updates.length > 0 && (
        <div className="report-section">
          <div className="section-label">{t(lang, "worker.detail.progressUpdates")}</div>
          {report.progress_updates.map((u, i) => (
            <div key={i} style={{ marginBottom: 8 }}>
              <p style={{ margin: 0 }}>{u.text}</p>
              <div style={{ fontSize: 11, color: "var(--ink-3)" }}>{new Date(u.created_at).toLocaleString()}</div>
              {u.evidence.length > 0 && (
                <div style={{ marginTop: 6 }}>
                  <EvidenceGallery items={toItems(u.evidence)} />
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {report.completion_status && (
        <div className="report-section">
          <div className="section-label">{t(lang, "worker.detail.completion")}</div>
          <p>{report.completion_status}</p>
          {report.resolved_at && <div style={{ fontSize: 11, color: "var(--ink-3)" }}>{new Date(report.resolved_at).toLocaleString()}</div>}
          {(() => {
            // completion_evidence (evidence-upload phase, multi-file) plus the legacy single
            // completion_evidence_photo for complaints resolved before that system existed.
            const items = toItems(report.completion_evidence);
            if (report.completion_evidence_photo && !report.completion_evidence.includes(report.completion_evidence_photo)) {
              items.push({ filePath: report.completion_evidence_photo });
            }
            return items.length > 0 ? (
              <div style={{ marginTop: 8 }}>
                <EvidenceGallery items={items} />
              </div>
            ) : null;
          })()}
        </div>
      )}

      {report.timeline.length > 0 && (
        <div className="report-section">
          <div className="section-label">{t(lang, "worker.detail.timeline")}</div>
          {report.timeline.map((entry, i) => (
            <div key={i} style={{ display: "flex", justifyContent: "space-between", gap: 10, fontSize: 12.5, padding: "5px 0", borderBottom: i < report.timeline.length - 1 ? "1px solid var(--line)" : "none" }}>
              <span>{entry.from_status ? `${entry.from_status} → ${entry.to_status}` : entry.to_status}</span>
              <span className="mono" style={{ color: "var(--ink-3)" }}>{new Date(entry.created_at).toLocaleString()}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

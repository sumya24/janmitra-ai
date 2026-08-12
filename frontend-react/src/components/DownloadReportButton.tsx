import { useState } from "react";
import { useAuth } from "../lib/auth";
import { useUiLang } from "../lib/uiLang";
import { t } from "../lib/i18n";
import { api, ApiError } from "../lib/api";
import { useToast } from "../lib/toast";

/** "Download Report" -- only ever rendered by a caller that already knows the complaint is
 * RESOLVED (backend independently re-enforces this: a 404 here means the button was rendered
 * for a stale/wrong status, not that the report is being faked). Fetches the PDF as a blob
 * (auth goes through the same Bearer header as every other request -- no plain <a href> with a
 * token in the URL) and triggers a normal browser download via a throwaway object URL. */
export default function DownloadReportButton({ complaintId, className }: { complaintId: number; className?: string }) {
  const { token } = useAuth();
  const { lang } = useUiLang();
  const toast = useToast();
  const [downloading, setDownloading] = useState(false);

  async function handleDownload() {
    if (!token) return;
    setDownloading(true);
    try {
      const { blob, filename } = await api.downloadComplaintReport(token, complaintId);
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      link.remove();
      // Not revoked synchronously: a larger blob (a report with several embedded evidence
      // photos easily reaches a megabyte-plus) isn't necessarily finished being handed to the
      // browser's download machinery by the time click() returns -- revoking the object URL
      // immediately can abort that in-flight read. A short delay lets it actually start first.
      setTimeout(() => URL.revokeObjectURL(url), 2000);
    } catch (err) {
      toast.error(err instanceof ApiError ? err.message : t(lang, "worker.detail.downloadFailed"));
    } finally {
      setDownloading(false);
    }
  }

  return (
    <button type="button" className={className ?? "btn btn-ghost btn-sm"} onClick={handleDownload} disabled={downloading}>
      {downloading ? t(lang, "worker.downloadingReport") : t(lang, "worker.downloadReport")}
    </button>
  );
}

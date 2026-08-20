import { useState } from "react";
import { useAuth } from "../lib/auth";
import { useUiLang } from "../lib/uiLang";
import { t } from "../lib/i18n";
import { api, ApiError } from "../lib/api";
import { useToast } from "../lib/toast";

/** "Share" -- fetches the exact same authenticated PDF blob as DownloadReportButton (never a
 * plain link with a token in the URL, and never a second, weaker unauthenticated share endpoint)
 * and hands the real file bytes to the OS share sheet via the Web Share API's file-sharing
 * (`navigator.canShare({ files })`). Falls back to a normal download -- with a toast explaining
 * why -- on any browser/device that can't share files (e.g. desktop Firefox), so the click still
 * does something useful instead of a dead end. */
/** The share glyph (three connected nodes) -- same shape as Lucide's "Share2" icon (MIT
 * licensed), reproduced as a plain inline SVG rather than pulling in the whole icon package for
 * a single glyph used in exactly one place. */
function ShareIcon() {
  return (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <circle cx="18" cy="5" r="3" />
      <circle cx="6" cy="12" r="3" />
      <circle cx="18" cy="19" r="3" />
      <line x1="8.59" y1="13.51" x2="15.42" y2="17.49" />
      <line x1="15.41" y1="6.51" x2="8.59" y2="10.49" />
    </svg>
  );
}

export default function ShareReportButton({
  complaintId,
  className,
  iconOnly,
}: {
  complaintId: number;
  className?: string;
  iconOnly?: boolean;
}) {
  const { token } = useAuth();
  const { lang } = useUiLang();
  const toast = useToast();
  const [sharing, setSharing] = useState(false);

  async function handleShare() {
    if (!token) return;
    setSharing(true);
    try {
      const { blob, filename } = await api.downloadComplaintReport(token, complaintId, lang);
      const file = new File([blob], filename, { type: blob.type || "application/pdf" });
      const nav = navigator as Navigator & {
        canShare?: (data: { files: File[] }) => boolean;
        share?: (data: { files: File[]; title?: string }) => Promise<void>;
      };

      if (nav.canShare?.({ files: [file] }) && nav.share) {
        await nav.share({ files: [file], title: filename });
        return;
      }

      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      link.remove();
      setTimeout(() => URL.revokeObjectURL(url), 2000);
      toast.success(t(lang, "worker.shareUnsupported"));
    } catch (err) {
      // The citizen/worker just closed the OS share sheet without picking anything -- not a
      // real failure, no error toast for that.
      if (err instanceof DOMException && err.name === "AbortError") return;
      toast.error(err instanceof ApiError ? err.message : t(lang, "worker.shareFailed"));
    } finally {
      setSharing(false);
    }
  }

  const label = sharing ? t(lang, "worker.sharing") : t(lang, "worker.shareReport");
  return (
    <button
      type="button"
      className={className ?? "btn btn-ghost btn-sm"}
      onClick={handleShare}
      disabled={sharing}
      title={iconOnly ? label : undefined}
      aria-label={iconOnly ? label : undefined}
    >
      {iconOnly ? <ShareIcon /> : label}
    </button>
  );
}

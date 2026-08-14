import { useState } from "react";
import { useUiLang } from "../lib/uiLang";
import { t } from "../lib/i18n";
import { api, ApiError } from "../lib/api";
import { useToast } from "../lib/toast";

/** Star rating + optional comment for a resolved complaint -- extracted from CitizenDashboard.tsx
 * (where it originated) so CitizenComplaintDetail.tsx can reuse the exact same form instead of a
 * second copy that could drift out of sync. */
export default function FeedbackForm({
  complaintId,
  lang,
  token,
  onSubmitted,
}: {
  complaintId: number;
  lang: ReturnType<typeof useUiLang>["lang"];
  token: string;
  onSubmitted: () => void;
}) {
  const [rating, setRating] = useState(0);
  const [comment, setComment] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const toast = useToast();

  async function submit() {
    if (rating < 1) return;
    setSubmitting(true);
    setError(null);
    try {
      await api.submitFeedback(token, complaintId, { rating, comment: comment.trim() || undefined });
      toast.success(t(lang, "citizen.feedbackSubmitted"));
      onSubmitted();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : t(lang, "citizen.errFeedbackFailed"));
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div style={{ marginTop: 10, paddingTop: 10, borderTop: "1px solid var(--line)" }}>
      <div style={{ fontSize: 12, fontWeight: 600, marginBottom: 6 }}>{t(lang, "citizen.feedbackTitle")}</div>
      {error && (
        <div className="banner-error" style={{ marginBottom: 8 }} role="alert" aria-live="polite">
          {error}
        </div>
      )}
      {/* role="radiogroup"/"radio" -- a rating is fundamentally "pick exactly one of five", the
          same semantics a radio group already has, which plain buttons with bare numeric
          aria-labels didn't convey (no group name, no selected-state announced at all). Reuses
          the already-translated feedbackTitle right above as the group's accessible name rather
          than introducing a new "star"/"stars" word across 6 languages just for this. Buttons
          were also 20px glyphs with only 4px gaps and no padding -- comfortably readable but a
          cramped, imprecise tap target on a phone; 40x40px (matching this app's existing
          .icon-btn convention elsewhere) with unpadded 4px gaps between them fixes that without
          making the row visually bulkier than the rest of this compact card. */}
      <div role="radiogroup" aria-label={t(lang, "citizen.feedbackTitle")} style={{ display: "flex", gap: 4, marginBottom: 8 }}>
        {[1, 2, 3, 4, 5].map((n) => (
          <button
            key={n}
            type="button"
            role="radio"
            aria-checked={n <= rating}
            onClick={() => setRating(n)}
            aria-label={`${n}`}
            style={{
              background: "none", border: "none", cursor: "pointer", fontSize: 20, lineHeight: 1,
              width: 40, height: 40, display: "flex", alignItems: "center", justifyContent: "center",
              color: n <= rating ? "var(--status-open)" : "var(--line)",
            }}
          >
            ★
          </button>
        ))}
      </div>
      <textarea
        rows={2}
        value={comment}
        onChange={(e) => setComment(e.target.value)}
        placeholder={t(lang, "citizen.feedbackCommentPlaceholder")}
        style={{ marginBottom: 8 }}
      />
      <button type="button" className="btn btn-primary btn-sm" onClick={submit} disabled={submitting || rating < 1}>
        {submitting ? t(lang, "citizen.feedbackSubmitting") : t(lang, "citizen.feedbackSubmit")}
      </button>
    </div>
  );
}

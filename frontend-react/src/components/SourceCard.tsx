import { t } from "../lib/i18n";
import { useUiLang } from "../lib/uiLang";
import type { SourceRecord } from "../lib/ragTypes";

/**
 * Renders one source backing an "Ask JanMitra" answer. Everything it shows comes from the
 * `source` prop — this component never hard-codes a government source or URL itself, so it
 * stays correct the moment the real RAG backend starts returning `SourceRecord`s (see
 * lib/ragTypes.ts and data/rag_knowledge_base/schema/source_record.schema.json, which this
 * prop shape mirrors exactly).
 *
 * verification_status drives the two presentations the spec calls for:
 *  - VERIFIED: labeled "Official source"; if source_url exists, a real outbound link to it.
 *  - SYNTHETIC: labeled "Synthetic / prototype data" — never a link, even if source_url were
 *    somehow set, because a synthetic record has no real page behind it to send someone to.
 * A missing URL on a verified source is handled gracefully (no broken/fake link rendered).
 */
export default function SourceCard({ source }: { source: SourceRecord }) {
  const { lang } = useUiLang();
  const isVerified = source.verification_status === "VERIFIED";
  const hasLink = isVerified && !!source.source_url;

  return (
    <div className="source-card">
      <div className="source-card-head">
        <span className={`source-tag ${isVerified ? "verified" : "synthetic"}`}>
          {isVerified ? t(lang, "ask.source.official") : t(lang, "ask.source.synthetic")}
        </span>
        {source.geographic_scope && <span className="source-scope">{source.geographic_scope}</span>}
      </div>
      <div className="source-title">{source.source_title}</div>
      {source.source_organization && <div className="source-org">{source.source_organization}</div>}
      {hasLink && (
        <a href={source.source_url!} target="_blank" rel="noopener noreferrer" className="source-link">
          {t(lang, "ask.source.viewOfficial")}
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" aria-hidden="true">
            <path d="M7 17 17 7M9 7h8v8" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
          </svg>
        </a>
      )}
      {!isVerified && <p className="source-note">{t(lang, "ask.source.syntheticNote")}</p>}
    </div>
  );
}

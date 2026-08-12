import { useState } from "react";
import { useUiLang } from "../lib/uiLang";
import { t } from "../lib/i18n";

const MAX_FILES = 10;
const ALLOWED_TYPES = ["image/jpeg", "image/png"];
const MAX_SIZE_BYTES = 5 * 1024 * 1024;

/**
 * Multi-file evidence attach/preview/remove control -- used everywhere a citizen or worker can
 * attach evidence photos (complaint creation, initial assessment, progress updates, completion).
 * Replaces the old single-file PhotoUpload component (removed -- this fully superseded it).
 *
 * Client-side validation (type/size/count) is a UX convenience only -- the backend independently
 * re-validates every file authoritatively (content-type + size, see backend/routes/complaints.py's
 * _validate_and_write); this component's checks exist so a citizen/worker sees a clear error
 * immediately instead of waiting on a round-trip for something obviously wrong.
 */
export default function MultiPhotoUpload({
  photos,
  onChange,
  maxFiles = MAX_FILES,
  placeholderKey = "citizen.photoPlaceholder",
}: {
  photos: File[];
  onChange: (files: File[]) => void;
  maxFiles?: number;
  placeholderKey?: string;
}) {
  const { lang } = useUiLang();
  const [dragOver, setDragOver] = useState(false);
  const [error, setError] = useState<string | null>(null);

  function addFiles(incoming: FileList | File[]) {
    setError(null);
    const candidates = Array.from(incoming);
    if (photos.length + candidates.length > maxFiles) {
      setError(t(lang, "photo.tooMany").replace("{max}", String(maxFiles)));
      return;
    }
    const accepted: File[] = [];
    for (const file of candidates) {
      if (!ALLOWED_TYPES.includes(file.type)) {
        setError(t(lang, "photo.unsupportedType"));
        continue;
      }
      if (file.size > MAX_SIZE_BYTES) {
        setError(t(lang, "photo.tooLarge"));
        continue;
      }
      accepted.push(file);
    }
    if (accepted.length) onChange([...photos, ...accepted]);
  }

  function removeAt(index: number) {
    onChange(photos.filter((_, i) => i !== index));
  }

  return (
    <div>
      {error && <div className="field-error" style={{ marginBottom: 8 }}>{error}</div>}

      {photos.length > 0 && (
        <div className="multi-photo-grid">
          {photos.map((photo, i) => (
            <div key={`${photo.name}-${i}`} className="multi-photo-thumb">
              <img src={URL.createObjectURL(photo)} alt={t(lang, "photo.previewAlt")} />
              <button
                type="button"
                className="multi-photo-remove"
                aria-label={t(lang, "photo.remove")}
                onClick={() => removeAt(i)}
              >
                ✕
              </button>
            </div>
          ))}
        </div>
      )}

      {photos.length < maxFiles && (
        <label
          className={`file-drop${dragOver ? " drag-over" : ""}`}
          onDragOver={(e) => {
            e.preventDefault();
            setDragOver(true);
          }}
          onDragLeave={() => setDragOver(false)}
          onDrop={(e) => {
            e.preventDefault();
            setDragOver(false);
            if (e.dataTransfer.files?.length) addFiles(e.dataTransfer.files);
          }}
        >
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
            <rect x="3" y="5" width="18" height="14" rx="2.5" stroke="currentColor" strokeWidth="1.7" />
            <circle cx="9" cy="11" r="2.2" stroke="currentColor" strokeWidth="1.5" />
            <path d="M21 16l-5.5-5-4 4-2-1.5L3 18" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
          </svg>
          <span>{photos.length > 0 ? t(lang, "photo.addMore") : t(lang, placeholderKey)}</span>
          <input
            type="file"
            accept="image/jpeg,image/png"
            multiple
            onChange={(e) => {
              if (e.target.files?.length) addFiles(e.target.files);
              e.target.value = "";
            }}
          />
        </label>
      )}
    </div>
  );
}

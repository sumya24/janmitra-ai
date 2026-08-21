import { useState } from "react";
import { useUiLang } from "../lib/uiLang";
import { t } from "../lib/i18n";

export interface LocationValue {
  ward: string;
  coords: { lat: number; lng: number; accuracy: number } | null;
}

/**
 * Location step for Report an Issue: "Use current location" or "Select location" manually.
 * Geolocation permission denial (or any geolocation failure — unsupported browser, timeout)
 * never blocks the flow — it falls back to the manual picker with a plain-language notice,
 * per the spec's explicit requirement.
 *
 * `wards` is the same real, worker-backed ward list CitizenDashboard already fetches via
 * api.listWards — reused here rather than refetched, so this component never invents a ward
 * that doesn't route anywhere. When the list is empty, falls back to free-text entry, matching
 * the existing form's behavior.
 */
export default function LocationPicker({
  value,
  onChange,
  wards,
}: {
  value: LocationValue;
  onChange: (v: LocationValue) => void;
  wards: string[];
}) {
  const { lang } = useUiLang();
  const [mode, setMode] = useState<"choose" | "manual">("choose");
  const [locating, setLocating] = useState(false);
  const [geoError, setGeoError] = useState<string | null>(null);

  function useCurrentLocation() {
    if (!("geolocation" in navigator)) {
      setGeoError(t(lang, "location.unavailable"));
      setMode("manual");
      return;
    }
    setLocating(true);
    setGeoError(null);
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        setLocating(false);
        onChange({
          ...value,
          coords: { lat: pos.coords.latitude, lng: pos.coords.longitude, accuracy: pos.coords.accuracy },
        });
        setMode("manual"); // still let them confirm/pick the ward — coords alone don't map to a ward name
      },
      () => {
        setLocating(false);
        setGeoError(t(lang, "location.unavailable"));
        setMode("manual");
      },
      { timeout: 8000 }
    );
  }

  if (mode === "choose") {
    return (
      <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
        {geoError && <div className="banner-error">{geoError}</div>}
        <button type="button" className="location-option" onClick={useCurrentLocation} disabled={locating}>
          <span className="location-option-icon">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
              <circle cx="12" cy="12" r="3" stroke="currentColor" strokeWidth="1.7" />
              <path d="M12 2v3M12 19v3M2 12h3M19 12h3" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" />
            </svg>
          </span>
          <span>
            <strong style={{ display: "block" }}>{locating ? t(lang, "location.locating") : t(lang, "location.useCurrent")}</strong>
            <span style={{ fontSize: 11.5, color: "var(--ink-2)" }}>{t(lang, "location.useCurrentHint")}</span>
          </span>
        </button>
        <button type="button" className="location-option" onClick={() => setMode("manual")}>
          <span className="location-option-icon">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
              <path d="M12 21s7-6.5 7-11.5A7 7 0 0 0 5 9.5C5 14.5 12 21 12 21Z" stroke="currentColor" strokeWidth="1.7" strokeLinejoin="round" />
              <circle cx="12" cy="9.5" r="2.3" stroke="currentColor" strokeWidth="1.5" />
            </svg>
          </span>
          <span>
            <strong style={{ display: "block" }}>{t(lang, "location.selectManually")}</strong>
            <span style={{ fontSize: 11.5, color: "var(--ink-2)" }}>{t(lang, "location.selectManuallyHint")}</span>
          </span>
        </button>
      </div>
    );
  }

  return (
    <div>
      {geoError && <div className="banner-error">{geoError}</div>}
      {value.coords && (
        <div className="dev-badge" style={{ marginBottom: 10 }}>
          {t(lang, "location.gpsAttached")}
        </div>
      )}
      <div className="field">
        <label htmlFor="wizard-ward">{wards.length === 0 ? t(lang, "citizen.wardOptional") : t(lang, "citizen.ward")}</label>
        {wards.length > 0 ? (
          <select id="wizard-ward" value={value.ward} onChange={(e) => onChange({ ...value, ward: e.target.value })} required>
            <option value="" disabled>
              {t(lang, "citizen.wardSelectPlaceholder")}
            </option>
            {wards.map((w) => (
              <option key={w} value={w}>
                {w}
              </option>
            ))}
          </select>
        ) : (
          <input id="wizard-ward" type="text" value={value.ward} onChange={(e) => onChange({ ...value, ward: e.target.value })} placeholder={t(lang, "citizen.wardPlaceholder")} />
        )}
      </div>
      <button type="button" className="btn btn-ghost btn-sm" onClick={() => setMode("choose")}>
        {t(lang, "location.backToOptions")}
      </button>
    </div>
  );
}

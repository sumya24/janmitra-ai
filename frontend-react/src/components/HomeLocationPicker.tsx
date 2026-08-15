import { useEffect, useState } from "react";
import { api, type LocationOption } from "../lib/api";
import { t, type LangCode } from "../lib/i18n";

export interface HomeLocationValue {
  ward: string;
  home_state_id?: number;
  home_district_id?: number;
  home_ward_id?: number;
  home_locality_id?: number;
}

/** The single, cascading State -> City -> Ward -> Area location picker on Signup (see
 * backend/routes/locations.py) -- this IS the "Area / ward" field now (there used to be two
 * separate location sections on this form, a real, reported point of confusion; this replaces
 * both with one). `ward`, the value that still backs worker matching/"My Area"/everything that
 * already reads `User.ward` unchanged, is composed here from whichever levels were actually
 * resolved -- see composeWard() below -- using the exact "{ward} — {locality}, {city}" format
 * real seeded worker wards already use, so a citizen who picks a real Pune/Kanpur/etc. ward ends
 * up with a string that matches real workers, not an approximation.
 *
 * Real data only: only 6 of India's 36 states have seeded cities/wards/areas today, so any step
 * whose parent has no children falls back to free text rather than inventing options -- and once
 * ANY level is free text, every level below it is free text too (there's no structured id left
 * to query children from), never disabled.
 *
 * All 4 rows are always mounted (never conditionally added/removed) -- a step that isn't
 * reachable yet is shown disabled/greyed out rather than hidden, so the box's height never grows
 * as the citizen picks each level (a second real, reported layout-shift bug this also fixes). */
export default function HomeLocationPicker({
  lang, onChange, hasError,
}: {
  lang: LangCode; onChange: (value: HomeLocationValue) => void; hasError?: boolean;
}) {
  const [states, setStates] = useState<LocationOption[]>([]);
  const [stateId, setStateId] = useState<number | "">("");
  const [statesLoaded, setStatesLoaded] = useState(false);

  const [cities, setCities] = useState<LocationOption[]>([]);
  const [cityId, setCityId] = useState<number | "">("");
  const [cityText, setCityText] = useState("");
  const [citiesLoaded, setCitiesLoaded] = useState(false);

  const [wardOptions, setWardOptions] = useState<LocationOption[]>([]);
  const [wardId, setWardId] = useState<number | "">("");
  const [wardText, setWardText] = useState("");
  const [wardsLoaded, setWardsLoaded] = useState(false);

  const [localities, setLocalities] = useState<LocationOption[]>([]);
  const [localityId, setLocalityId] = useState<number | "">("");
  const [localityText, setLocalityText] = useState("");
  const [localitiesLoaded, setLocalitiesLoaded] = useState(false);

  useEffect(() => {
    api.listStates().then((s) => { setStates(s); setStatesLoaded(true); }).catch(() => setStatesLoaded(true));
  }, []);

  const cityName = cityId !== "" ? cities.find((c) => c.id === cityId)?.name ?? "" : cityText.trim();
  const wardName = wardId !== "" ? wardOptions.find((w) => w.id === wardId)?.name ?? "" : wardText.trim();
  const localityName = localityId !== "" ? localities.find((l) => l.id === localityId)?.name ?? "" : localityText.trim();

  // Mirrors the exact format real seeded worker wards already use ("Ward 22 — Kothrud, Pune"),
  // degrading gracefully when a level wasn't reached -- never fabricates a level that wasn't
  // actually given.
  function composeWard(): string {
    if (!wardName) return "";
    const withLocality = localityName ? `${wardName} — ${localityName}` : wardName;
    return cityName ? `${withLocality}, ${cityName}` : withLocality;
  }

  useEffect(() => {
    onChange({
      ward: composeWard(),
      home_state_id: stateId === "" ? undefined : stateId,
      home_district_id: cityId === "" ? undefined : cityId,
      home_ward_id: wardId === "" ? undefined : wardId,
      home_locality_id: localityId === "" ? undefined : localityId,
    });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [stateId, cityId, cityText, wardId, wardText, localityId, localityText]);

  function resetBelowState() {
    setCityId(""); setCityText(""); setCities([]); setCitiesLoaded(false);
    setWardId(""); setWardText(""); setWardOptions([]); setWardsLoaded(false);
    setLocalityId(""); setLocalityText(""); setLocalities([]); setLocalitiesLoaded(false);
  }

  function resetBelowCity() {
    setWardId(""); setWardText(""); setWardOptions([]); setWardsLoaded(false);
    setLocalityId(""); setLocalityText(""); setLocalities([]); setLocalitiesLoaded(false);
  }

  function resetBelowWard() {
    setLocalityId(""); setLocalityText(""); setLocalities([]); setLocalitiesLoaded(false);
  }

  function handleStateChange(raw: string) {
    const id = raw === "" ? "" : Number(raw);
    setStateId(id);
    resetBelowState();
    if (id !== "") {
      api.listCitiesForState(id).then((c) => { setCities(c); setCitiesLoaded(true); }).catch(() => setCitiesLoaded(true));
    }
  }

  function handleCityChange(raw: string) {
    const id = raw === "" ? "" : Number(raw);
    setCityId(id);
    resetBelowCity();
    if (id !== "") {
      api.listWardsForCity(id).then((w) => { setWardOptions(w); setWardsLoaded(true); }).catch(() => setWardsLoaded(true));
    }
  }

  function handleCityText(value: string) {
    setCityText(value);
    // Free-text city has no district id to query children from -- ward/area become directly
    // available as free text too, immediately, rather than staying disabled forever.
    resetBelowCity();
  }

  function handleWardChange(raw: string) {
    const id = raw === "" ? "" : Number(raw);
    setWardId(id);
    resetBelowWard();
    if (id !== "") {
      api.listLocalitiesForWard(id).then((l) => { setLocalities(l); setLocalitiesLoaded(true); }).catch(() => setLocalitiesLoaded(true));
    }
  }

  function handleWardText(value: string) {
    setWardText(value);
    resetBelowWard();
  }

  // A level is "resolved" once it has a real id OR non-empty free text -- either way, the next
  // level down can be worked on.
  const cityResolved = cityId !== "" || cityText.trim() !== "";
  const wardResolved = wardId !== "" || wardText.trim() !== "";

  const cityReady = stateId !== "" && citiesLoaded;
  // Ward becomes usable once the city is resolved -- via a real dropdown pick (then wait for its
  // wards to load) or via free text (no fetch needed, no gate to wait on).
  const wardReady = cityId !== "" ? wardsLoaded : cityResolved;
  const areaReady = wardId !== "" ? localitiesLoaded : wardResolved;

  return (
    <div className={`home-location-picker ${hasError ? "has-error" : ""}`}>
      <div className="home-location-heading">{t(lang, "signup.homeLocation.heading")}</div>
      <div className="home-location-subtitle">{t(lang, "signup.homeLocation.subtitle")}</div>

      <div className="field home-location-row">
        <label htmlFor="signup-home-state">{t(lang, "signup.homeLocation.state")}</label>
        {!statesLoaded ? (
          <select id="signup-home-state" value="" disabled>
            <option value="">{t(lang, "signup.homeLocation.statePlaceholder")}</option>
          </select>
        ) : (
          <select id="signup-home-state" value={stateId} onChange={(e) => handleStateChange(e.target.value)}>
            <option value="">{t(lang, "signup.homeLocation.statePlaceholder")}</option>
            {states.map((s) => (
              <option key={s.id} value={s.id}>{s.name}</option>
            ))}
          </select>
        )}
      </div>

      <div className="field home-location-row">
        <label htmlFor="signup-home-city">{t(lang, "signup.homeLocation.city")}</label>
        {!cityReady ? (
          <select id="signup-home-city" value="" disabled>
            <option value="">{t(lang, "signup.homeLocation.cityPlaceholder")}</option>
          </select>
        ) : cities.length > 0 ? (
          <select id="signup-home-city" value={cityId} onChange={(e) => handleCityChange(e.target.value)}>
            <option value="">{t(lang, "signup.homeLocation.cityPlaceholder")}</option>
            {cities.map((c) => (
              <option key={c.id} value={c.id}>{c.name}</option>
            ))}
          </select>
        ) : (
          <input
            id="signup-home-city"
            type="text"
            value={cityText}
            onChange={(e) => handleCityText(e.target.value)}
            placeholder={t(lang, "signup.homeLocation.cityTextPlaceholder")}
          />
        )}
      </div>

      <div className="field home-location-row">
        <label htmlFor="signup-home-ward">{t(lang, "signup.homeLocation.ward")}</label>
        {!wardReady ? (
          <select id="signup-home-ward" value="" disabled>
            <option value="">{t(lang, "signup.homeLocation.wardPlaceholder")}</option>
          </select>
        ) : wardOptions.length > 0 ? (
          <select id="signup-home-ward" value={wardId} onChange={(e) => handleWardChange(e.target.value)}>
            <option value="">{t(lang, "signup.homeLocation.wardPlaceholder")}</option>
            {wardOptions.map((w) => (
              <option key={w.id} value={w.id}>{w.name}</option>
            ))}
          </select>
        ) : (
          <input
            id="signup-home-ward"
            type="text"
            value={wardText}
            onChange={(e) => handleWardText(e.target.value)}
            placeholder={t(lang, "signup.homeLocation.wardTextPlaceholder")}
          />
        )}
      </div>

      <div className="field home-location-row home-location-row-last">
        <label htmlFor="signup-home-area">{t(lang, "signup.homeLocation.area")}</label>
        {!areaReady ? (
          <select id="signup-home-area" value="" disabled>
            <option value="">{t(lang, "signup.homeLocation.areaPlaceholder")}</option>
          </select>
        ) : localities.length > 0 ? (
          <select id="signup-home-area" value={localityId} onChange={(e) => setLocalityId(e.target.value === "" ? "" : Number(e.target.value))}>
            <option value="">{t(lang, "signup.homeLocation.areaPlaceholder")}</option>
            {localities.map((l) => (
              <option key={l.id} value={l.id}>{l.name}</option>
            ))}
          </select>
        ) : (
          <input
            id="signup-home-area"
            type="text"
            value={localityText}
            onChange={(e) => setLocalityText(e.target.value)}
            placeholder={t(lang, "signup.homeLocation.areaTextPlaceholder")}
          />
        )}
      </div>
    </div>
  );
}

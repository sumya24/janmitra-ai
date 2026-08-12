import { useEffect, useState, type FormEvent } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useUiLang } from "../lib/uiLang";
import { useAuth } from "../lib/auth";
import { t } from "../lib/i18n";
import { api, ApiError } from "../lib/api";
import ThemeToggle from "../components/ThemeToggle";
import AuthPanel from "../components/AuthPanel";
import AuthFormBrand from "../components/AuthFormBrand";
import "./Auth.css";

export default function Signup() {
  const { lang } = useUiLang();
  const { setSession } = useAuth();
  const navigate = useNavigate();

  const [fullName, setFullName] = useState("");
  const [phone, setPhone] = useState("");
  const [password, setPassword] = useState("");
  const [ward, setWard] = useState("");
  const [wards, setWards] = useState<string[]>([]);
  const [fieldErrors, setFieldErrors] = useState<Record<string, boolean>>({});
  const [formError, setFormError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  // Fetched without a token -- GET /complaints/wards is unauthenticated specifically so this
  // list is available before the citizen has signed up at all. Same real, worker-backed ward
  // list ReportIssue's LocationPicker already uses -- never a name that doesn't route anywhere.
  // Mandatory, one-time-at-signup, not editable later (no ward field in Settings) -- so every
  // citizen account is guaranteed to have one, and "My Area" (MyArea.tsx) never has to explain
  // a missing-ward state to an account that could have set it and didn't.
  useEffect(() => {
    api.listWards().then(setWards).catch(() => setWards([]));
  }, []);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setFormError(null);

    const errors: Record<string, boolean> = {};
    if (!fullName.trim()) errors.fullName = true;
    if (!phone.trim()) errors.phone = true;
    if (!password) errors.password = true;
    if (!ward.trim()) errors.ward = true;
    setFieldErrors(errors);
    if (Object.keys(errors).length > 0) return;

    setSubmitting(true);
    try {
      const { access_token, user } = await api.signup({
        full_name: fullName.trim(),
        phone: phone.trim(),
        password,
        preferred_language: lang,
        ward: ward.trim(),
      });
      setSession(access_token, user);
      navigate("/citizen");
    } catch (err) {
      setFormError(err instanceof ApiError ? err.message : t(lang, "common.somethingWrong"));
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="authwrap">
      <AuthPanel lang={lang} />
      <div className="auth-form-side">
        <div className="auth-form-side-bg" aria-hidden="true" />
        <ThemeToggle className="theme-toggle" />
        <AuthFormBrand />
        <div className="authcard enter">
          <div className="authtabs">
            <Link to="/login" className="authtab">
              {t(lang, "auth.tab.login")}
            </Link>
            <span className="authtab active">{t(lang, "auth.tab.signup")}</span>
          </div>

          {formError && <div className="banner-error">{formError}</div>}

          <form onSubmit={handleSubmit} noValidate>
            <div className={`field ${fieldErrors.fullName ? "has-error" : ""}`}>
              <label htmlFor="signup-name">{t(lang, "auth.field.name")}</label>
              <input id="signup-name" type="text" value={fullName} onChange={(e) => setFullName(e.target.value)} />
              {fieldErrors.fullName && <div className="field-error">{t(lang, "common.fieldRequired")}</div>}
            </div>
            <div className={`field ${fieldErrors.phone ? "has-error" : ""}`}>
              <label htmlFor="signup-phone">{t(lang, "auth.field.phone")}</label>
              <input id="signup-phone" type="tel" placeholder="98xxxxxxxx" value={phone} onChange={(e) => setPhone(e.target.value)} />
              {fieldErrors.phone && <div className="field-error">{t(lang, "common.fieldRequired")}</div>}
            </div>
            <div className={`field ${fieldErrors.password ? "has-error" : ""}`}>
              <label htmlFor="signup-password">{t(lang, "auth.field.password")}</label>
              <input id="signup-password" type="password" value={password} onChange={(e) => setPassword(e.target.value)} />
              {fieldErrors.password && <div className="field-error">{t(lang, "common.fieldRequired")}</div>}
            </div>
            <div className={`field ${fieldErrors.ward ? "has-error" : ""}`}>
              <label htmlFor="signup-ward">{t(lang, "citizen.ward")}</label>
              {wards.length > 0 ? (
                <select id="signup-ward" value={ward} onChange={(e) => setWard(e.target.value)}>
                  <option value="">{t(lang, "citizen.wardSelectPlaceholder")}</option>
                  {wards.map((w) => (
                    <option key={w} value={w}>
                      {w}
                    </option>
                  ))}
                </select>
              ) : (
                <input id="signup-ward" type="text" value={ward} onChange={(e) => setWard(e.target.value)} placeholder={t(lang, "citizen.wardPlaceholder")} />
              )}
              {fieldErrors.ward && <div className="field-error">{t(lang, "common.fieldRequired")}</div>}
            </div>

            <div className="worker-note">{t(lang, "auth.signup.workernote")}</div>

            <button type="submit" className="btn btn-primary full" disabled={submitting}>
              {submitting ? "…" : t(lang, "auth.signup.button")}
            </button>
          </form>

          <div className="switchline">
            {t(lang, "auth.signup.switch")} <Link to="/login">{t(lang, "auth.signup.switchlink")}</Link>
          </div>
        </div>
      </div>
    </div>
  );
}

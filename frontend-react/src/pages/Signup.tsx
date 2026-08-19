import { useState, type FormEvent } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useUiLang } from "../lib/uiLang";
import { useAuth } from "../lib/auth";
import { t } from "../lib/i18n";
import { api, ApiError } from "../lib/api";
import ThemeToggle from "../components/ThemeToggle";
import AuthPanel from "../components/AuthPanel";
import AuthFormBrand from "../components/AuthFormBrand";
import HomeLocationPicker, { type HomeLocationValue } from "../components/HomeLocationPicker";
import "./Auth.css";

export default function Signup() {
  const { lang } = useUiLang();
  const { setSession } = useAuth();
  const navigate = useNavigate();

  const [fullName, setFullName] = useState("");
  const [phone, setPhone] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  // The State/City/Ward/Area picker below IS the "Area / ward" field -- see
  // HomeLocationPicker.tsx's own docstring for why this used to be two separate sections.
  const [homeLocation, setHomeLocation] = useState<HomeLocationValue>({ ward: "" });
  const [fieldErrors, setFieldErrors] = useState<Record<string, boolean>>({});
  const [formError, setFormError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  // Client-side echo of backend/routes/auth.py's _validate_password_strength -- the server stays
  // the source of truth (this is only for immediate feedback), but a citizen shouldn't have to
  // submit the form to discover their password is too weak when the rule is this simple.
  const passwordTooWeak = password.length > 0 && (password.length < 8 || !/[A-Za-z]/.test(password) || !/\d/.test(password));

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setFormError(null);

    const errors: Record<string, boolean> = {};
    if (!fullName.trim()) errors.fullName = true;
    if (!phone.trim()) errors.phone = true;
    else if (!/^[6-9]\d{9}$/.test(phone.trim())) errors.phone = true;
    if (!password) errors.password = true;
    else if (passwordTooWeak) errors.password = true;
    if (!confirmPassword) errors.confirmPassword = true;
    else if (confirmPassword !== password) errors.confirmPassword = true;
    if (!homeLocation.ward.trim()) errors.ward = true;
    setFieldErrors(errors);
    if (Object.keys(errors).length > 0) return;

    setSubmitting(true);
    try {
      const { access_token, refresh_token, user } = await api.signup({
        full_name: fullName.trim(),
        phone: phone.trim(),
        password,
        preferred_language: lang,
        ...homeLocation,
        ward: homeLocation.ward.trim(),
      });
      setSession(access_token, refresh_token, user);
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
              <input
                id="signup-name"
                type="text"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                aria-invalid={fieldErrors.fullName || undefined}
                aria-describedby={fieldErrors.fullName ? "signup-name-error" : undefined}
              />
              {fieldErrors.fullName && (
                <div className="field-error" id="signup-name-error">
                  {t(lang, "common.fieldRequired")}
                </div>
              )}
            </div>
            <div className={`field ${fieldErrors.phone ? "has-error" : ""}`}>
              <label htmlFor="signup-phone">{t(lang, "auth.field.phone")}</label>
              <input
                id="signup-phone"
                type="tel"
                placeholder="98xxxxxxxx"
                value={phone}
                onChange={(e) => setPhone(e.target.value)}
                aria-invalid={fieldErrors.phone || undefined}
                aria-describedby={fieldErrors.phone ? "signup-phone-error" : undefined}
              />
              {fieldErrors.phone && (
                <div className="field-error" id="signup-phone-error">
                  {t(lang, phone.trim() ? "common.invalidPhone" : "common.fieldRequired")}
                </div>
              )}
            </div>
            <div className={`field ${fieldErrors.password ? "has-error" : ""}`}>
              <label htmlFor="signup-password">{t(lang, "auth.field.password")}</label>
              <input
                id="signup-password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                aria-invalid={fieldErrors.password || undefined}
                aria-describedby={fieldErrors.password ? "signup-password-error" : "signup-password-hint"}
              />
              {fieldErrors.password ? (
                <div className="field-error" id="signup-password-error">
                  {t(lang, password ? "auth.field.passwordWeak" : "common.fieldRequired")}
                </div>
              ) : (
                <div className="field-hint" id="signup-password-hint">
                  {t(lang, "auth.field.passwordHint")}
                </div>
              )}
            </div>
            <div className={`field ${fieldErrors.confirmPassword ? "has-error" : ""}`}>
              <label htmlFor="signup-confirm-password">{t(lang, "auth.field.confirmPassword")}</label>
              <input
                id="signup-confirm-password"
                type="password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                aria-invalid={fieldErrors.confirmPassword || undefined}
                aria-describedby={fieldErrors.confirmPassword ? "signup-confirm-password-error" : undefined}
              />
              {fieldErrors.confirmPassword && (
                <div className="field-error" id="signup-confirm-password-error">
                  {t(lang, confirmPassword ? "auth.field.passwordMismatch" : "common.fieldRequired")}
                </div>
              )}
            </div>
            <HomeLocationPicker lang={lang} onChange={setHomeLocation} hasError={fieldErrors.ward} />
            {fieldErrors.ward && <div className="field-error home-location-error">{t(lang, "signup.homeLocation.required")}</div>}

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

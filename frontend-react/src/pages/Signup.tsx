import { useState, type FormEvent } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useUiLang } from "../lib/uiLang";
import { useAuth } from "../lib/auth";
import { SUPPORTED_LANGUAGES, t } from "../lib/i18n";
import { api, ApiError } from "../lib/api";
import "./Auth.css";

export default function Signup() {
  const { lang } = useUiLang();
  const { setSession } = useAuth();
  const navigate = useNavigate();

  const [fullName, setFullName] = useState("");
  const [phone, setPhone] = useState("");
  const [password, setPassword] = useState("");
  const [fieldErrors, setFieldErrors] = useState<Record<string, boolean>>({});
  const [formError, setFormError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setFormError(null);

    const errors: Record<string, boolean> = {};
    if (!fullName.trim()) errors.fullName = true;
    if (!phone.trim()) errors.phone = true;
    if (!password) errors.password = true;
    setFieldErrors(errors);
    if (Object.keys(errors).length > 0) return;

    setSubmitting(true);
    try {
      const { access_token, user } = await api.signup({
        full_name: fullName.trim(),
        phone: phone.trim(),
        password,
        preferred_language: lang,
      });
      setSession(access_token, user);
      navigate("/citizen");
    } catch (err) {
      setFormError(err instanceof ApiError ? err.message : "Something went wrong. Please try again.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="authwrap">
      <div className="authcard">
        <div className="authtabs">
          <Link to="/login" className="authtab">
            {t(lang, "auth.tab.login") || "Log in"}
          </Link>
          <span className="authtab active">{t(lang, "auth.tab.signup") || "Sign up"}</span>
        </div>

        {formError && <div className="banner-error">{formError}</div>}

        <form onSubmit={handleSubmit} noValidate>
          <div className={`field ${fieldErrors.fullName ? "has-error" : ""}`}>
            <label htmlFor="signup-name">{t(lang, "auth.field.name")}</label>
            <input id="signup-name" type="text" value={fullName} onChange={(e) => setFullName(e.target.value)} />
            {fieldErrors.fullName && <div className="field-error">This field is required.</div>}
          </div>
          <div className={`field ${fieldErrors.phone ? "has-error" : ""}`}>
            <label htmlFor="signup-phone">{t(lang, "auth.field.phone")}</label>
            <input id="signup-phone" type="tel" placeholder="98xxxxxxxx" value={phone} onChange={(e) => setPhone(e.target.value)} />
            {fieldErrors.phone && <div className="field-error">This field is required.</div>}
          </div>
          <div className={`field ${fieldErrors.password ? "has-error" : ""}`}>
            <label htmlFor="signup-password">{t(lang, "auth.field.password")}</label>
            <input id="signup-password" type="password" value={password} onChange={(e) => setPassword(e.target.value)} />
            {fieldErrors.password && <div className="field-error">This field is required.</div>}
          </div>

          <div className="lang-lock">
            <span>
              {t(lang, "auth.signup.langlocked")} <b>{SUPPORTED_LANGUAGES[lang].name}</b>
            </span>
            <Link to="/">{t(lang, "auth.signup.changelang")}</Link>
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
  );
}

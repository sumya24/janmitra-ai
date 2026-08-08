import { useState, type FormEvent } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useUiLang } from "../lib/uiLang";
import { useAuth } from "../lib/auth";
import { t } from "../lib/i18n";
import { api, ApiError } from "../lib/api";
import ThemeToggle from "../components/ThemeToggle";
import "./Auth.css";

export default function Login() {
  const { lang } = useUiLang();
  const { setSession } = useAuth();
  const navigate = useNavigate();

  const [phone, setPhone] = useState("");
  const [password, setPassword] = useState("");
  const [fieldErrors, setFieldErrors] = useState<Record<string, boolean>>({});
  const [formError, setFormError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setFormError(null);

    const errors: Record<string, boolean> = {};
    if (!phone.trim()) errors.phone = true;
    if (!password) errors.password = true;
    setFieldErrors(errors);
    if (Object.keys(errors).length > 0) return;

    setSubmitting(true);
    try {
      const { access_token, user } = await api.login({ phone: phone.trim(), password });
      setSession(access_token, user);
      navigate(user.role === "citizen" ? "/citizen" : user.role === "worker" ? "/worker" : "/admin");
    } catch (err) {
      setFormError(err instanceof ApiError ? err.message : t(lang, "common.somethingWrong"));
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="authwrap">
      <ThemeToggle className="theme-toggle" />
      <div className="authcard">
        <div className="authtabs">
          <span className="authtab active">{t(lang, "auth.tab.login")}</span>
          <Link to="/signup" className="authtab">
            {t(lang, "auth.tab.signup")}
          </Link>
        </div>

        {formError && <div className="banner-error">{formError}</div>}

        <form onSubmit={handleSubmit} noValidate>
          <div className={`field ${fieldErrors.phone ? "has-error" : ""}`}>
            <label htmlFor="login-phone">{t(lang, "auth.field.phone")}</label>
            <input id="login-phone" type="tel" placeholder="98xxxxxxxx" value={phone} onChange={(e) => setPhone(e.target.value)} />
            {fieldErrors.phone && <div className="field-error">{t(lang, "common.fieldRequired")}</div>}
          </div>
          <div className={`field ${fieldErrors.password ? "has-error" : ""}`}>
            <label htmlFor="login-password">{t(lang, "auth.field.password")}</label>
            <input id="login-password" type="password" value={password} onChange={(e) => setPassword(e.target.value)} />
            {fieldErrors.password && <div className="field-error">{t(lang, "common.fieldRequired")}</div>}
          </div>
          <button type="submit" className="btn btn-primary full" disabled={submitting}>
            {submitting ? "…" : t(lang, "auth.login.button")}
          </button>
        </form>

        <div className="switchline">
          {t(lang, "auth.login.switch")} <Link to="/signup">{t(lang, "auth.login.switchlink")}</Link>
        </div>
      </div>
    </div>
  );
}

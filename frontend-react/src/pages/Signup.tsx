import { useEffect, useState, type FormEvent } from "react";
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

const EMAIL_PATTERN = /^[^@\s]+@[^@\s]+\.[^@\s]+$/;

// How long "Resend code" stays disabled after each send -- purely a spam-click guard on the
// button itself, unrelated to OTP_EXPIRE_MINUTES (the code stays valid on the SERVER for much
// longer than this; this only bounds how soon a citizen can ask for a NEW one).
const RESEND_COOLDOWN_SECONDS = 30;

// Email verification is mandatory before an account exists at all, but lives inline on the
// email field itself (a "Send code" button, then a confirm-code step right there), not as a
// separate page/step after the rest of the form -- see backend/routes/auth.py's module
// docstring. The rest of the form stays visible and editable throughout: a citizen can verify
// their email first, fill in the rest, then submit -- or fill in everything else first, verify
// email last, then submit. "Create account" itself is clickable the whole time (not hard-
// disabled until verified -- same as every other field here, which surfaces problems as an
// inline error on submit, not a disabled button); handleSubmit shows a clear error if email
// isn't verified yet, matching the honest-validation pattern the rest of the form already uses.
// The server independently re-checks via email_verification_token (see api.signup) regardless --
// the client-side check here is just UX, never the actual gate.
export default function Signup() {
  const { lang } = useUiLang();
  const { setSession } = useAuth();
  const navigate = useNavigate();

  const [fullName, setFullName] = useState("");
  const [phone, setPhone] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  // The State/City/Ward/Area picker below IS the "Area / ward" field -- see
  // HomeLocationPicker.tsx's own docstring for why this used to be two separate sections.
  const [homeLocation, setHomeLocation] = useState<HomeLocationValue>({ ward: "" });
  const [fieldErrors, setFieldErrors] = useState<Record<string, boolean>>({});
  const [formError, setFormError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  const [emailOtpSent, setEmailOtpSent] = useState(false);
  const [emailCode, setEmailCode] = useState("");
  const [emailVerified, setEmailVerified] = useState(false);
  const [emailVerificationToken, setEmailVerificationToken] = useState<string | null>(null);
  const [emailOtpError, setEmailOtpError] = useState<string | null>(null);
  const [sendingEmailCode, setSendingEmailCode] = useState(false);
  const [verifyingEmailCode, setVerifyingEmailCode] = useState(false);
  const [resendCooldown, setResendCooldown] = useState(0);

  // Self-scheduling countdown -- ticks resendCooldown down to 0 one second at a time. Re-runs
  // this effect on every tick (rather than a single setInterval) so it cleanly stops itself the
  // instant resendCooldown hits 0, with no separate clearInterval bookkeeping needed.
  useEffect(() => {
    if (resendCooldown <= 0) return;
    const timer = setTimeout(() => setResendCooldown((s) => s - 1), 1000);
    return () => clearTimeout(timer);
  }, [resendCooldown]);

  // Client-side echo of backend/routes/auth.py's _validate_password_strength -- the server stays
  // the source of truth (this is only for immediate feedback), but a citizen shouldn't have to
  // submit the form to discover their password is too weak when the rule is this simple.
  const passwordTooWeak =
    password.length > 0 &&
    (password.length < 8 || !/[A-Za-z]/.test(password) || !/\d/.test(password) || !/[^A-Za-z0-9]/.test(password));

  function resetEmailVerification() {
    setEmailOtpSent(false);
    setEmailCode("");
    setEmailVerified(false);
    setEmailVerificationToken(null);
    setEmailOtpError(null);
    setResendCooldown(0);
  }

  function handleEmailChange(value: string) {
    setEmail(value);
    // Editing the address after a code was sent (verified or not) invalidates whatever's in
    // flight -- the OTP/proof token were issued for the OLD address, not this one.
    if (emailOtpSent || emailVerified) resetEmailVerification();
  }

  async function handleSendEmailCode() {
    const trimmed = email.trim();
    if (!trimmed || !EMAIL_PATTERN.test(trimmed)) {
      setFieldErrors((prev) => ({ ...prev, email: true }));
      return;
    }
    setFieldErrors((prev) => ({ ...prev, email: false }));
    setEmailOtpError(null);
    setSendingEmailCode(true);
    try {
      await api.sendSignupEmailCode({ email: trimmed });
      setEmailOtpSent(true);
      setResendCooldown(RESEND_COOLDOWN_SECONDS);
    } catch (err) {
      setEmailOtpError(err instanceof ApiError ? err.message : t(lang, "common.somethingWrong"));
    } finally {
      setSendingEmailCode(false);
    }
  }

  async function handleVerifyEmailCode() {
    setEmailOtpError(null);
    if (!emailCode.trim()) {
      setFieldErrors((prev) => ({ ...prev, emailCode: true }));
      return;
    }
    setFieldErrors((prev) => ({ ...prev, emailCode: false }));
    setVerifyingEmailCode(true);
    try {
      const { email_verification_token } = await api.verifySignupEmailCode({
        email: email.trim(),
        code: emailCode.trim(),
      });
      setEmailVerificationToken(email_verification_token);
      setEmailVerified(true);
      setEmailOtpSent(false);
      setEmailCode("");
    } catch (err) {
      setEmailOtpError(err instanceof ApiError ? err.message : t(lang, "common.somethingWrong"));
    } finally {
      setVerifyingEmailCode(false);
    }
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setFormError(null);

    const errors: Record<string, boolean> = {};
    if (!fullName.trim()) errors.fullName = true;
    if (!phone.trim()) errors.phone = true;
    else if (!/^[6-9]\d{9}$/.test(phone.trim())) errors.phone = true;
    if (!email.trim()) errors.email = true;
    else if (!EMAIL_PATTERN.test(email.trim())) errors.email = true;
    if (!password) errors.password = true;
    else if (passwordTooWeak) errors.password = true;
    if (!confirmPassword) errors.confirmPassword = true;
    else if (confirmPassword !== password) errors.confirmPassword = true;
    if (!homeLocation.ward.trim()) errors.ward = true;
    setFieldErrors(errors);
    if (Object.keys(errors).length > 0) return;

    // Belt-and-suspenders: the "Create account" button is already disabled until this is true,
    // but the server is the actual source of truth (see backend/routes/auth.py's signup(), which
    // independently re-checks email_verification_token) -- this just gives an honest message
    // instead of a raw 400 in the unlikely event this branch is ever reached.
    if (!emailVerified || !emailVerificationToken) {
      setFormError(t(lang, "auth.signup.verifyEmailFirst"));
      return;
    }

    setSubmitting(true);
    try {
      const { access_token, refresh_token, user } = await api.signup({
        full_name: fullName.trim(),
        phone: phone.trim(),
        email: email.trim(),
        email_verification_token: emailVerificationToken,
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

            <div className="email-verify-block">
              <div className={`field ${fieldErrors.email ? "has-error" : ""}`}>
                <label htmlFor="signup-email">{t(lang, "auth.email.label")}</label>
                <div className="email-verify-row">
                  <input
                    id="signup-email"
                    type="email"
                    value={email}
                    disabled={emailVerified}
                    onChange={(e) => handleEmailChange(e.target.value)}
                    aria-invalid={fieldErrors.email || undefined}
                    aria-describedby={fieldErrors.email ? "signup-email-error" : undefined}
                  />
                  {emailVerified ? (
                    <span className="email-verified-badge">✓ {t(lang, "auth.email.verified")}</span>
                  ) : (
                    !emailOtpSent && (
                      <button
                        type="button"
                        className="btn btn-ghost btn-sm"
                        onClick={handleSendEmailCode}
                        disabled={sendingEmailCode || !email.trim()}
                      >
                        {sendingEmailCode ? "…" : t(lang, "auth.email.sendCode")}
                      </button>
                    )
                  )}
                </div>
                {fieldErrors.email && (
                  <div className="field-error" id="signup-email-error">
                    {t(lang, "common.fieldRequired")}
                  </div>
                )}
              </div>

              {emailOtpSent && !emailVerified && (
                <div className="email-otp-inline">
                  {emailOtpError && <div className="banner-error">{emailOtpError}</div>}
                  <div className="field-hint">{t(lang, "auth.email.sent")}</div>
                  <div className={`field ${fieldErrors.emailCode ? "has-error" : ""}`}>
                    <label htmlFor="signup-email-otp">{t(lang, "auth.field.otpCode")}</label>
                    <input
                      id="signup-email-otp"
                      type="text"
                      inputMode="numeric"
                      value={emailCode}
                      onChange={(e) => setEmailCode(e.target.value)}
                      aria-invalid={fieldErrors.emailCode || undefined}
                      aria-describedby={fieldErrors.emailCode ? "signup-email-otp-error" : undefined}
                    />
                    {fieldErrors.emailCode && (
                      <div className="field-error" id="signup-email-otp-error">
                        {t(lang, "common.fieldRequired")}
                      </div>
                    )}
                  </div>
                  <button
                    type="button"
                    className="btn btn-primary btn-sm"
                    onClick={handleVerifyEmailCode}
                    disabled={verifyingEmailCode}
                  >
                    {verifyingEmailCode ? "…" : t(lang, "auth.email.verify")}
                  </button>
                  <button
                    type="button"
                    className="btn btn-ghost btn-sm"
                    onClick={handleSendEmailCode}
                    disabled={sendingEmailCode || resendCooldown > 0}
                  >
                    {sendingEmailCode
                      ? "…"
                      : resendCooldown > 0
                        ? `${t(lang, "auth.email.resend")} (${resendCooldown}s)`
                        : t(lang, "auth.email.resend")}
                  </button>
                </div>
              )}

              {emailVerified && (
                <button type="button" className="email-change-link" onClick={resetEmailVerification}>
                  {t(lang, "auth.email.change")}
                </button>
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

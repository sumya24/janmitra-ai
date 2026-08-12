/** Logo + colorful "JanMitra AI" wordmark shown above the login/signup card, centered on one
 * line. AuthPanel (the big navy side panel) hides below 860px, which left narrow/mobile
 * viewports with no branding at all on the auth pages — this shows regardless of viewport
 * width, so the form side always carries the brand, not just wide screens.
 *
 * Colored to match the source logo's own wordmark (navy "Jan" / green "Mitra" / blue "AI")
 * exactly, unlike AuthPanel's lightened variant -- this sits on the page's normal light/dark
 * surface, not a navy panel, so the real logo colors already have good contrast here. */
export default function AuthFormBrand() {
  return (
    <div className="auth-form-brand">
      <img src="/brand/logo-mark.png" alt="" className="auth-form-brand-mark" />
      <div className="auth-form-brand-word display">
        <span className="auth-form-brand-jan">Jan</span>
        <span className="auth-form-brand-mitra">Mitra</span> <span className="auth-form-brand-ai">AI</span>
      </div>
    </div>
  );
}

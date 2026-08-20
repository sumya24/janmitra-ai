import { expect, type Page } from "@playwright/test";

let _uniquePhoneCounter = 0;

export function uniquePhone(): string {
  // 10-digit, starting with 9, unique enough per test run to avoid 409 conflicts. A trailing
  // in-process counter (not just Date.now()) matters here: two calls back-to-back with no
  // await between them can land in the same millisecond and otherwise collide.
  _uniquePhoneCounter = (_uniquePhoneCounter + 1) % 100;
  const suffix = String(_uniquePhoneCounter).padStart(2, "0");
  return "9" + String(Date.now()).slice(-7) + suffix;
}

let _uniqueEmailCounter = 0;

export function uniqueEmail(): string {
  _uniqueEmailCounter = (_uniqueEmailCounter + 1) % 100;
  const suffix = String(_uniqueEmailCounter).padStart(2, "0");
  return `test${Date.now()}${suffix}@example.com`;
}

/** Completes Signup.tsx's inline, mandatory email-verification step -- email verification is
 * mandatory at signup (see backend/routes/auth.py's module docstring), but lives inline on the
 * email field itself (a "Send code" button, then a confirm-code step right there), not as a
 * separate page/step after the rest of the form. The "Create account" button stays disabled
 * until this succeeds, so every spec that signs up a citizen needs this called after the
 * #signup-email field has a value and BEFORE clicking "Create account" -- exactly where in the
 * rest of the form-filling that happens doesn't matter, since verifying the email doesn't
 * disturb any other already-filled field. Reads the email back from the #signup-email input
 * itself (rather than requiring callers to pass it in) so callers don't need to thread a
 * variable through.
 *
 * Fetches the code from GET /auth/_dev/otp-code (backend/routes/auth.py's dev/test-only
 * endpoint, 404s in production) instead of reading a real inbox -- this project's local .env may
 * have real SMTP credentials configured for manual testing, and e2e specs must never depend on
 * (or spam) a real mailbox. Full absolute backend URL, not a relative path: page.request's own
 * baseURL is the Vite dev server on :5173 (per playwright.config.ts), which doesn't proxy
 * /auth/* -- only the React app itself talks to the backend directly, via VITE_API_URL (see
 * lib/api.ts). */
export async function verifySignupEmail(page: Page): Promise<void> {
  const email = await page.locator("#signup-email").inputValue();
  await page.getByRole("button", { name: "Send code" }).click();
  // Longer-than-default timeout: the send-code call does a real (non-mocked) SMTP send before
  // returning, and that occasionally takes several seconds -- observed causing flaky/failed
  // e2e runs at the default 5000ms even though the backend request itself always succeeds.
  // Matches this suite's existing precedent of widening waits around real backend round-trips
  // (see fillHomeLocationPicker's expect.poll below).
  await expect(page.getByLabel("Verification code")).toBeVisible({ timeout: 15000 });
  const otpResponse = await page.request.get(
    `http://localhost:8000/auth/_dev/otp-code?email=${encodeURIComponent(email)}`
  );
  const { code } = (await otpResponse.json()) as { code: string };
  await page.getByLabel("Verification code").fill(code);
  await page.getByRole("button", { name: "Verify" }).click();
  await expect(page.getByText("Verified", { exact: false })).toBeVisible();
}

/** Fills Signup's mandatory State/City/Ward/Area picker (HomeLocationPicker.tsx) -- the single
 * shared implementation every spec that signs up a citizen should call, replacing what used to
 * be 12 separate copies of near-identical select-or-freetext logic against the old single "Area
 * / ward" field that component replaced (see its own docstring for why there's now one merged
 * picker instead of two separate location sections).
 *
 * Locates by element id (#signup-home-state/city/ward), not label text -- several callers sign
 * up in non-English UI languages, and ids stay the same across all 6 while the label text is
 * translated. State is always a real `<select>` (options are whatever states
 * backend/routes/locations.py's _COVERED_STATE_CODES currently covers, plus an always-present
 * "Other" -- index 1 is always a real state, never "Other", since it's appended last); City and
 * Ward each independently render as either a `<select>` (real seeded data for that branch) or a
 * plain `<input>` (free-text fallback -- true for most of those states' cities today) depending
 * on what this test run's database actually has, never assume one shape. Area is left untouched: it's
 * optional, and no spec's actual test logic depends on the citizen's own signup-time ward text
 * matching anything else (workers are assigned separately by admin; a citizen's own complaints
 * are filed with their own explicit ward picker in the complaint wizard) -- any valid, non-empty
 * ward value from this picker is sufficient to get past the "ward is required" validation. */
export async function fillHomeLocationPicker(page: Page): Promise<void> {
  const stateField = page.locator("#signup-home-state");
  // The state list itself loads async (GET /locations/states, fired on mount) -- explicitly wait
  // for it to actually be populated rather than leaning on selectOption's own built-in retry
  // budget, which is bounded by the TEST's timeout, not this helper's. Real, observed failure
  // this fixes: under load (backend still warming up, or contending with other requests), the
  // fetch can take longer than expected, and a bare selectOption({index: 1}) against a select
  // that still only has its placeholder option just spins until the whole test times out.
  await expect.poll(() => stateField.locator("option").count()).toBeGreaterThan(1);
  await stateField.selectOption({ index: 1 });

  const cityField = page.locator("#signup-home-city");
  await expect.poll(() => cityField.isEnabled()).toBe(true);
  if ((await cityField.evaluate((el) => el.tagName)) === "SELECT") {
    await cityField.selectOption({ index: 1 });
  } else {
    await cityField.fill("Test City");
  }

  const wardField = page.locator("#signup-home-ward");
  await expect.poll(() => wardField.isEnabled()).toBe(true);
  if ((await wardField.evaluate((el) => el.tagName)) === "SELECT") {
    await wardField.selectOption({ index: 1 });
  } else {
    await wardField.fill("Test Ward");
  }
}

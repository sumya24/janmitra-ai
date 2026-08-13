import { test, expect } from "@playwright/test";
import { uniquePhone } from "./helpers";

test("theme toggle cycles system -> light -> dark -> system and persists across reload", async ({ page }) => {
  await page.goto("/welcome");

  const html = page.locator("html");
  const toggle = page.locator(".theme-toggle");

  // Starts in "system" (no data-theme attribute).
  await expect(html).not.toHaveAttribute("data-theme", /.+/);

  await toggle.click();
  await expect(html).toHaveAttribute("data-theme", "light");

  await toggle.click();
  await expect(html).toHaveAttribute("data-theme", "dark");

  // Persists across a reload.
  await page.reload();
  await expect(html).toHaveAttribute("data-theme", "dark");

  await toggle.click();
  await expect(html).not.toHaveAttribute("data-theme", /.+/);
});

test("citizen can switch to voice input, record a complaint, and submit it", async ({ page }) => {
  // Playwright's default 30s per-test timeout is shorter than the up-to-30s the final
  // assertion below alone is allowed to wait -- the test would get killed before that
  // assertion's own timeout could ever be honored. Needs real headroom above it, plus the
  // signup/recording steps before it.
  test.setTimeout(90000);
  const phone = uniquePhone();

  await page.goto("/signup");
  await page.getByLabel("Full name").fill("Voice User");
  await page.getByLabel("Phone number").fill(phone);
  await page.getByLabel("Password").fill("voice-pass1");
  // Mandatory ward field -- see e2e/ask-janmitra.spec.ts's signUpAndReachCitizenHome for why
  // this waits for the async GET /complaints/wards fetch (Signup.tsx) to settle first.
  await page.waitForTimeout(600);
  const signupWardField = page.getByLabel("Area / ward");
  if ((await signupWardField.evaluate((el) => el.tagName)) === "SELECT") {
    await signupWardField.selectOption({ index: 1 });
  } else {
    await signupWardField.fill("Test Ward");
  }
  await page.getByRole("button", { name: "Create account" }).click();
  await expect(page).toHaveURL(/\/citizen$/);

  // The complaint form now lives in the Report an Issue wizard (Phase 1), not directly on the
  // citizen Home screen — get there first.
  // Scoped to the hero's own primary button -- a nav-drawer link with the same text also exists
  // on the page (see components/NavDrawer.tsx), so an unscoped role/name locator is ambiguous.
  await page.locator("a.btn-primary", { hasText: "Report an Issue" }).click();
  await expect(page).toHaveURL(/\/citizen\/report$/);

  // Location step: pick a ward if the list is non-empty (other specs sharing this dev db may
  // have already seeded one, which the step then requires); otherwise it's optional free text
  // and can be left blank either way.
  await page.getByRole("button", { name: "Select location" }).click();
  const wardField = page.locator("#wizard-ward");
  if ((await wardField.evaluate((el) => el.tagName)) === "SELECT") {
    await wardField.selectOption({ index: 1 });
  }
  await page.getByRole("button", { name: "Next" }).click();

  // Description step: text mode is the default; switching to Speak hides the textarea and
  // shows the recorder.
  await expect(page.locator("#complaint-text")).toBeVisible();
  await page.getByRole("button", { name: "🎙️ Speak" }).click();
  await expect(page.locator("#complaint-text")).not.toBeVisible();

  // Trying to move on without recording anything shows an inline error, not a crash.
  await page.getByRole("button", { name: "Next" }).click();
  await expect(page.locator(".banner-error")).toContainText("Please record your complaint");

  // Record a short voice note using the fake mic device configured in playwright.config.ts.
  await page.getByRole("button", { name: "🎙️ Start recording" }).click();
  await expect(page.getByRole("button", { name: "⏹ Stop" })).toBeVisible();
  await page.waitForTimeout(1200);
  await page.getByRole("button", { name: "⏹ Stop" }).click();

  // A playable recording and a "record again" option replace the record button.
  await expect(page.locator("audio")).toBeVisible();
  await expect(page.getByRole("button", { name: "🔁 Record again" })).toBeVisible();

  // Photo step (optional, skip) -> AI Understanding (brief client-side mock, wait for it to
  // finish) -> Preview -> submit.
  await page.getByRole("button", { name: "Next" }).click();
  await page.getByRole("button", { name: "Next" }).click();
  await expect(page.getByText(/Development preview/)).toBeVisible({ timeout: 3000 });
  await page.getByRole("button", { name: "Next" }).click();
  await page.getByRole("button", { name: "Submit complaint" }).click();

  // Submitting now reaches the backend's real AI pipeline. Whether this environment's
  // SARVAM_API_KEY is currently working determines success (JM-##### success screen) or a
  // graceful failure (banner-error) — both are acceptable here; what must never happen is a
  // crash or an indefinite hang. See MEMORY.md: this ambiguity predates this test's wizard
  // navigation and isn't something a UI change can resolve on its own.
  //
  // Widened from 45000 after measuring the real pipeline directly (integration/stability phase):
  // this path chains FOUR sequential real Sarvam calls (transcribe -> normalize -> translate ->
  // summarize, one more than the text-only path -- see backend/services/complaint_agent.py),
  // each genuinely dependent on the previous one's output. Three live timed runs of just the
  // three-call text-only chain measured 17.7s/28.5s/18.7s -- a ~60% swing -- so the four-call
  // voice chain has strictly more accumulated variance, not less. 45s (already a widening from an
  // original 20s, per this test's history) still flaked under full-suite load in this phase's own
  // validation runs; 60s gives real, measured headroom instead of guessing again.
  await expect(page.locator(".mono", { hasText: /^JM-\d{5}$/ }).or(page.locator(".banner-error"))).toBeVisible({
    timeout: 60000,
  });
});

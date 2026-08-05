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
  const phone = uniquePhone();

  await page.goto("/signup");
  await page.getByLabel("Full name").fill("Voice User");
  await page.getByLabel("Phone number").fill(phone);
  await page.getByLabel("Password").fill("voice-pass1");
  await page.getByRole("button", { name: "Create account" }).click();
  await expect(page).toHaveURL(/\/citizen$/);

  // Text mode is the default; switching to Speak hides the textarea and shows the recorder.
  await expect(page.locator("#complaint-text")).toBeVisible();
  await page.getByRole("button", { name: "🎙️ Speak" }).click();
  await expect(page.locator("#complaint-text")).not.toBeVisible();

  // Submitting without recording anything shows an inline error, not a crash.
  await page.getByRole("button", { name: "Submit complaint" }).click();
  await expect(page.locator(".banner-error")).toContainText("Please record your complaint");

  // Record a short voice note using the fake mic device configured in playwright.config.ts.
  await page.getByRole("button", { name: "🎙️ Start recording" }).click();
  await expect(page.getByRole("button", { name: "⏹ Stop" })).toBeVisible();
  await page.waitForTimeout(1200);
  await page.getByRole("button", { name: "⏹ Stop" }).click();

  // A playable recording and a "record again" option replace the record button.
  await expect(page.locator("audio")).toBeVisible();
  await expect(page.getByRole("button", { name: "🔁 Record again" })).toBeVisible();

  // Submitting now reaches the backend's AI pipeline. No Sarvam API key is
  // configured in this environment, so it fails gracefully — the UI must show
  // a clear error, never crash or hang.
  await page.getByRole("button", { name: "Submit complaint" }).click();
  await expect(page.locator(".banner-error")).toBeVisible({ timeout: 10000 });
});

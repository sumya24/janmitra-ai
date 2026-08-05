import { test, expect } from "@playwright/test";
import { uniquePhone } from "./helpers";

test("language gate -> landing -> signup validation -> citizen dashboard -> graceful complaint error", async ({ page }) => {
  await page.goto("/");

  // Language gate is the very first thing shown.
  await expect(page.getByText("Choose your language")).toBeVisible();
  await page.getByRole("button", { name: /मराठी/ }).click();

  // Landing page text should now be in Marathi.
  await expect(page).toHaveURL(/\/welcome$/);
  await expect(page.getByText("तुमच्या भाषेत तक्रार करा")).toBeVisible();

  await page.getByRole("link", { name: "साइन अप" }).click();
  await expect(page).toHaveURL(/\/signup$/);

  // Submitting empty should show inline validation errors, not crash.
  await page.getByRole("button", { name: "खाते तयार करा" }).click();
  await expect(page.getByText("This field is required.").first()).toBeVisible();

  // Fill in a valid signup and submit.
  const phone = uniquePhone();
  await page.getByLabel("पूर्ण नाव").fill("Priya Deshmukh");
  await page.getByLabel("फोन नंबर").fill(phone);
  await page.getByLabel("पासवर्ड").fill("secret123");
  await page.getByRole("button", { name: "खाते तयार करा" }).click();

  await expect(page).toHaveURL(/\/citizen$/);
  await expect(page.getByText("Priya Deshmukh")).toBeVisible();
  await expect(page.getByText("CITIZEN")).toBeVisible();

  // Submit a complaint — no Sarvam API key is configured in this environment,
  // so the backend fails the AI pipeline. The UI must show a clear error,
  // never crash or hang.
  await page.getByPlaceholder(/Garbage not collected/).fill("कचरा उचलला नाही");
  await page.getByRole("button", { name: "Submit complaint" }).click();
  await expect(page.locator(".banner-error")).toBeVisible({ timeout: 10000 });
});

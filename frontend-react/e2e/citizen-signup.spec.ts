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

  // Submitting empty should show inline validation errors, not crash. Signed up in Marathi,
  // so the validation message correctly renders in Marathi too, not English.
  await page.getByRole("button", { name: "खाते तयार करा" }).click();
  await expect(page.getByText("हे क्षेत्र आवश्यक आहे.").first()).toBeVisible();

  // Fill in a valid signup and submit.
  const phone = uniquePhone();
  await page.getByLabel("पूर्ण नाव").fill("Priya Deshmukh");
  await page.getByLabel("फोन नंबर").fill(phone);
  await page.getByLabel("पासवर्ड").fill("secret123");
  // Mandatory ward field -- the field starts as a text input and swaps to a <select> once the
  // async GET /complaints/wards fetch resolves (Signup.tsx), so wait for that to settle first
  // (same handling as e2e/ask-janmitra.spec.ts's signUpAndReachCitizenHome).
  await page.waitForTimeout(600);
  const wardField = page.getByLabel("क्षेत्र / प्रभाग");
  if ((await wardField.evaluate((el) => el.tagName)) === "SELECT") {
    await wardField.selectOption({ index: 1 });
  } else {
    await wardField.fill("Test Ward");
  }
  await page.getByRole("button", { name: "खाते तयार करा" }).click();

  await expect(page).toHaveURL(/\/citizen$/);
  await expect(page.getByText("Priya Deshmukh")).toBeVisible();
  await expect(page.getByText("नागरिक", { exact: true })).toBeVisible(); // role pill — also renders in Marathi

  // Start reporting an issue. The complaint form lives in the Report an Issue wizard (Phase 1),
  // still in Marathi since that's the signed-up language.
  // Scoped to the hero's own primary button -- a nav-drawer link with the same text also exists
  // on the page (see components/NavDrawer.tsx), so an unscoped role/name locator is ambiguous.
  await page.locator("a.btn-primary", { hasText: "समस्या नोंदवा" }).click();
  await expect(page).toHaveURL(/\/citizen\/report$/);

  // Try to skip straight through without filling anything in — whichever step's client-side
  // validation fires first (the ward, if other specs sharing this dev db already seeded one;
  // otherwise the empty-description check on the next step) must show a clear inline error in
  // Marathi, not crash or silently advance.
  await page.getByRole("button", { name: "पुढे" }).click();
  if (!(await page.locator(".banner-error").isVisible())) {
    await page.getByRole("button", { name: "पुढे" }).click();
  }
  await expect(page.locator(".banner-error")).toBeVisible({ timeout: 10000 });
});

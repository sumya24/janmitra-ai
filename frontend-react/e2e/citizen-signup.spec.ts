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
  await page.getByRole("button", { name: "खाते तयार करा" }).click();

  await expect(page).toHaveURL(/\/citizen$/);
  await expect(page.getByText("Priya Deshmukh")).toBeVisible();
  await expect(page.getByText("नागरिक", { exact: true })).toBeVisible(); // role pill — also renders in Marathi

  // Submit a complaint. The citizen dashboard is still in Marathi, so its placeholder text is
  // the Marathi translation, not the English original.
  await page.getByPlaceholder(/कचरा जमा झालेला नाही/).fill("कचरा उचलला नाही");
  await page.getByRole("button", { name: "तक्रार दाखल करा" }).click();
  // No ward is selected, so this now correctly fails client-side validation (in Marathi)
  // rather than reaching the AI pipeline at all.
  await expect(page.locator(".banner-error")).toBeVisible({ timeout: 10000 });
});

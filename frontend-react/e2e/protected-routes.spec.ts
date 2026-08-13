import { test, expect } from "@playwright/test";
import { uniquePhone } from "./helpers";

test("an unauthenticated visitor is redirected away from protected dashboards", async ({ page }) => {
  await page.goto("/citizen");
  await expect(page).toHaveURL(/\/login$/);

  await page.goto("/worker");
  await expect(page).toHaveURL(/\/login$/);

  await page.goto("/admin");
  await expect(page).toHaveURL(/\/login$/);
});

test("a citizen cannot reach the worker or admin dashboards by URL", async ({ page }) => {
  const phone = uniquePhone();
  await page.goto("/signup");
  await page.getByLabel("Full name").fill("Just A Citizen");
  await page.getByLabel("Phone number").fill(phone);
  await page.getByLabel("Password").fill("secret123");
  // Mandatory ward field -- see e2e/ask-janmitra.spec.ts's signUpAndReachCitizenHome for why
  // this waits for the async GET /complaints/wards fetch (Signup.tsx) to settle first.
  await page.waitForTimeout(600);
  const wardField = page.getByLabel("Area / ward");
  if ((await wardField.evaluate((el) => el.tagName)) === "SELECT") {
    await wardField.selectOption({ index: 1 });
  } else {
    await wardField.fill("Test Ward");
  }
  await page.getByRole("button", { name: "Create account" }).click();
  await expect(page).toHaveURL(/\/citizen$/);

  await page.goto("/worker");
  await expect(page).toHaveURL(/\/citizen$/);

  await page.goto("/admin");
  await expect(page).toHaveURL(/\/citizen$/);
});

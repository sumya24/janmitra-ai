import { test, expect } from "@playwright/test";
import { fillHomeLocationPicker, uniquePhone } from "./helpers";

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
  await page.getByLabel("Password", { exact: true }).fill("secret123");
  await page.locator("#signup-confirm-password").fill("secret123");
  await fillHomeLocationPicker(page);
  await page.getByRole("button", { name: "Create account" }).click();
  await expect(page).toHaveURL(/\/citizen$/);

  await page.goto("/worker");
  await expect(page).toHaveURL(/\/citizen$/);

  await page.goto("/admin");
  await expect(page).toHaveURL(/\/citizen$/);
});

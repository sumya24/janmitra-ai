import { test, expect } from "@playwright/test";
import { fillHomeLocationPicker, uniqueEmail, uniquePhone } from "./helpers";

/** Covers the email-OTP / login-by-email / forgot-password feature's FRONTEND wiring through the
 * real UI (unit coverage for the OTP/email logic itself lives in tests/test_email_otp.py). The
 * parts that need a real received email (completing add-and-verify-email, and a full
 * forgot-password round trip past the "code sent" step) aren't automatable here without real SMTP
 * credentials configured on the backend -- those need a live manual check once real credentials
 * are in place, same as this project's other "needs a real provider key" features. What IS
 * covered here works regardless of whether SMTP is configured: the login form's relabeled
 * identifier field, the forgot-password link, and forgot-password's no-enumeration behavior
 * (POST /auth/forgot-password always returns 204 and the UI always shows the same "code sent"
 * step, whether or not the email is actually registered -- see backend/routes/auth.py's
 * forgot_password). */

async function signUpCitizen(page: import("@playwright/test").Page, phone: string, password: string) {
  await page.goto("/signup");
  await page.getByLabel("Full name").fill("Email OTP Test Citizen");
  await page.getByLabel("Phone number").fill(phone);
  await page.getByLabel("Password", { exact: true }).fill(password);
  await page.locator("#signup-confirm-password").fill(password);
  await fillHomeLocationPicker(page);
  await page.getByRole("button", { name: "Create account" }).click();
  await expect(page).toHaveURL(/\/citizen$/);
}

test("login page accepts either a phone number or an email, and links to forgot-password", async ({ page }) => {
  await page.goto("/login");
  await expect(page.getByLabel("Phone number or email")).toBeVisible();

  await page.getByRole("link", { name: "Forgot password?" }).click();
  await expect(page).toHaveURL(/\/forgot-password$/);
});

test("forgot password shows the same code-sent step for an unregistered email as for a real one", async ({ page }) => {
  await page.goto("/forgot-password");
  await page.getByLabel("Email address").fill(uniqueEmail());
  await page.getByRole("button", { name: "Send code" }).click();

  // No-enumeration: this must succeed and move to the code step even though the email above was
  // never registered anywhere -- the UI has no way to tell the two cases apart, by design.
  await expect(page.getByText("If that email is registered and verified, a code has been sent.")).toBeVisible();
  await expect(page.getByLabel("Verification code")).toBeVisible();
  await expect(page.getByLabel("New password")).toBeVisible();
});

test("forgot password requires an email before sending a code", async ({ page }) => {
  await page.goto("/forgot-password");
  await page.getByRole("button", { name: "Send code" }).click();
  await expect(page.getByText("This field is required.")).toBeVisible();
  await expect(page).toHaveURL(/\/forgot-password$/);
});

test("settings shows an Email section for an account with no verified email yet", async ({ page }) => {
  const phone = uniquePhone();
  await signUpCitizen(page, phone, "otptest12345");

  await page.getByLabel("Settings").click();
  const emailSectionToggle = page.getByRole("button", { name: "Email", exact: true });
  await expect(emailSectionToggle).toBeVisible();
  await emailSectionToggle.click();

  await expect(page.getByLabel("Email address")).toBeVisible();
  await expect(page.getByRole("button", { name: "Send code" })).toBeVisible();
});

test("login still works with the phone number after the identifier field is relabeled", async ({ page }) => {
  const phone = uniquePhone();
  await signUpCitizen(page, phone, "otptest12345");
  await page.getByLabel("Settings").click();
  await page.getByRole("button", { name: "Log out" }).click();
  await expect(page).toHaveURL(/\/welcome$/);

  await page.goto("/login");
  await page.getByLabel("Phone number or email").fill(phone);
  await page.getByLabel("Password").fill("otptest12345");
  await page.getByRole("button", { name: "Log in" }).click();
  await expect(page).toHaveURL(/\/citizen$/);
});

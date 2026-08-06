import { test, expect } from "@playwright/test";
import { execSync } from "node:child_process";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { uniquePhone } from "./helpers";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const REPO_ROOT = path.resolve(__dirname, "../..");
const ADMIN_PHONE = "9999999999";
const ADMIN_PASSWORD = "adminpass123";

test.beforeAll(() => {
  // Simulates how a real deployment provisions its first Super Admin: seeded
  // directly into the database, never through sign-up.
  //
  // The python3 binary name isn't universal — Windows installs from python.org
  // only register "python", not "python3" — so pick per-platform.
  const pythonBin = process.platform === "win32" ? "python" : "python3";
  execSync(
    `${pythonBin} scripts/seed_admin.py --phone ${ADMIN_PHONE} --password ${ADMIN_PASSWORD} --name "Anjali Kulkarni"`,
    { cwd: REPO_ROOT, stdio: "pipe" }
  );
});

test("super admin creates a worker, who can then log in and see their (empty) queue", async ({ page }) => {
  const workerPhone = uniquePhone();

  await page.goto("/login");
  await page.getByLabel("Phone number").fill(ADMIN_PHONE);
  await page.getByLabel("Password").fill(ADMIN_PASSWORD);
  await page.getByRole("button", { name: "Log in" }).click();
  await expect(page).toHaveURL(/\/admin$/);
  await expect(page.getByText("Super Admin", { exact: true })).toBeVisible();

  await page.getByRole("button", { name: "+ Add worker" }).click();
  await page.getByLabel("Full name").fill("Ramesh Kadam");
  await page.getByLabel("Phone number").fill(workerPhone);
  await page.getByLabel("Temporary password").fill("workerpass123");
  await page.getByLabel("Assign to ward").fill("Ward 14 — Rukadi Road");
  await page.getByRole("button", { name: "Add worker", exact: true }).click();

  await expect(page.getByText("Ramesh Kadam")).toBeVisible();
  await expect(page.getByText("Ward 14 — Rukadi Road")).toBeVisible();

  // Log out, then log in as the newly created worker.
  await page.getByLabel("Settings").click();
  await page.getByRole("button", { name: "Log out" }).click();
  await expect(page).toHaveURL(/\/welcome$/);

  await page.goto("/login");
  await page.getByLabel("Phone number").fill(workerPhone);
  await page.getByLabel("Password").fill("workerpass123");
  await page.getByRole("button", { name: "Log in" }).click();

  await expect(page).toHaveURL(/\/worker$/);
  await expect(page.getByText("Ward: Ward 14 — Rukadi Road")).toBeVisible();
  await expect(page.getByText("Nothing here.")).toBeVisible();
});

test("a citizen cannot create a worker account (no such option exists)", async ({ page }) => {
  const phone = uniquePhone();
  await page.goto("/signup");
  await page.getByLabel("Full name").fill("Just A Citizen");
  await page.getByLabel("Phone number").fill(phone);
  await page.getByLabel("Password").fill("secret123");
  await page.getByRole("button", { name: "Create account" }).click();
  await expect(page).toHaveURL(/\/citizen$/);

  // There is no "Add worker" button, no role picker, nothing — a citizen's
  // only actions are reporting and viewing their own complaints.
  await expect(page.getByRole("button", { name: "+ Add worker" })).toHaveCount(0);
  await expect(page.getByText(/Super Admin/i)).toHaveCount(0);
});

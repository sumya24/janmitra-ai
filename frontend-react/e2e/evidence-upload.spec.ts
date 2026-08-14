import { test, expect } from "@playwright/test";
import { execSync } from "node:child_process";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { fillHomeLocationPicker, uniquePhone } from "./helpers";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const REPO_ROOT = path.resolve(__dirname, "../..");
const ADMIN_PHONE = uniquePhone();
const ADMIN_PASSWORD = "adminpass123";
const WARD = `Evidence Test Ward ${Date.now()}`;

// Minimal, genuinely valid 1x1 images (not just "fake bytes with a jpeg-ish prefix") -- real
// file content, so this test proves actual images survive the full upload -> storage -> gallery
// round trip, not just that some bytes made it through.
const JPEG_1PX = Buffer.from(
  "/9j/4AAQSkZJRgABAQEAYABgAAD/2wBDAAMCAgICAgMCAgIDAwMDBAYEBAQEBAgGBgUGCQgKCgkICQkKDA8MCgsOCwkJDRENDg8QEBEQCgwSExIQEw8QEBD/2wBDAQMDAwQDBAgEBAgQCwkLEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBD/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAj/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFQEBAQAAAAAAAAAAAAAAAAAAAAX/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIRAxEAPwCdABmX/9k=",
  "base64"
);
const PNG_1PX = Buffer.from(
  "iVBORw0KGgoAAAANSUhEUgAAAAIAAAACCAIAAAD91JpzAAAAEElEQVR4nGP8zwACTGCSAQANHQEDgslx/wAAAABJRU5ErkJggg==",
  "base64"
);

test.beforeAll(() => {
  const pythonBin = process.platform === "win32" ? "python" : "python3";
  execSync(
    `${pythonBin} scripts/seed_admin.py --phone ${ADMIN_PHONE} --password ${ADMIN_PASSWORD} --name "Evidence Test Admin"`,
    { cwd: REPO_ROOT, stdio: "pipe" }
  );
});

async function login(page: import("@playwright/test").Page, phone: string, password: string) {
  await page.goto("/login");
  await page.getByLabel("Phone number").fill(phone);
  await page.getByLabel("Password").fill(password);
  await page.getByRole("button", { name: "Log in" }).click();
  // Wait for the login itself to actually complete (token stored, redirected off /login) before
  // returning -- a caller that immediately does page.goto() right after this would otherwise
  // race the login POST and can navigate while still unauthenticated.
  await page.waitForURL(/\/(citizen|worker|admin)$/, { timeout: 15000 });
}

async function logout(page: import("@playwright/test").Page) {
  await page.evaluate(() => localStorage.clear());
  await page.goto("/welcome");
}

test("real multi-file evidence upload, end to end: select -> upload -> storage -> gallery -> report", async ({ page }) => {
  test.setTimeout(150000);

  const workerPhone = uniquePhone();
  const citizenPhone = uniquePhone();

  // --- Admin creates a worker. ---
  await login(page, ADMIN_PHONE, ADMIN_PASSWORD);
  await expect(page).toHaveURL(/\/admin$/);
  // Scoped to the dashboard's own button (class btn-ghost) -- a nav-drawer link with the same
  // text also exists on the page (see components/NavDrawer.tsx), so an unscoped role/name
  // locator is ambiguous.
  await page.locator("a.btn-ghost", { hasText: "Manage Workers" }).click();
  await expect(page).toHaveURL(/\/admin\/workers$/);
  await page.getByRole("button", { name: "+ Add worker" }).click();
  await page.getByLabel("Full name").fill("Evidence Test Worker");
  await page.getByLabel("Phone number").fill(workerPhone);
  await page.getByLabel("Temporary password").fill("workerpass123");
  await page.getByLabel("Assign to ward").fill(WARD);
  await page.getByRole("button", { name: "English", exact: true }).click();
  await page.getByRole("button", { name: "Add worker", exact: true }).click();
  await expect(page.getByText("Evidence Test Worker").first()).toBeVisible();
  await logout(page);

  // --- Citizen files a complaint with TWO real photos, selected via the actual file input. ---
  await page.goto("/signup");
  await page.getByLabel("Full name").fill("Evidence Test Citizen");
  await page.getByLabel("Phone number").fill(citizenPhone);
  await page.getByLabel("Password").fill("citizenpass123");
  await fillHomeLocationPicker(page);
  await page.getByRole("button", { name: "Create account" }).click();
  await expect(page).toHaveURL(/\/citizen$/);

  // Scoped to the hero's own primary button -- a nav-drawer link with the same text also exists
  // on the page (see components/NavDrawer.tsx), so an unscoped role/name locator is ambiguous.
  await page.locator("a.btn-primary", { hasText: "Report an Issue" }).click();
  await expect(page).toHaveURL(/\/citizen\/report$/);
  await page.getByRole("button", { name: "Select location" }).click();
  await page.locator("#wizard-ward").selectOption(WARD);
  await page.getByRole("button", { name: "Next" }).click();
  await page.getByPlaceholder(/Garbage not collected/).fill("Two photos of the same broken streetlight.");
  await page.getByRole("button", { name: "Next" }).click();

  // Media step: select two real files at once through the actual <input type=file multiple>.
  await page.locator('input[type="file"]').setInputFiles([
    { name: "streetlight-1.jpg", mimeType: "image/jpeg", buffer: JPEG_1PX },
    { name: "streetlight-2.png", mimeType: "image/png", buffer: PNG_1PX },
  ]);
  // Both thumbnails preview before submission.
  await expect(page.locator(".multi-photo-thumb")).toHaveCount(2);

  await page.getByRole("button", { name: "Next" }).click();
  await expect(page.getByText(/Development preview/)).toBeVisible({ timeout: 3000 });
  await page.getByRole("button", { name: "Next" }).click();
  await page.getByRole("button", { name: "Submit complaint" }).click();
  await expect(page.getByText("Complaint submitted successfully.")).toBeVisible({ timeout: 60000 });
  await page.getByRole("link", { name: "Track this complaint" }).click();
  await expect(page).toHaveURL(/\/citizen\/complaints$/);

  // The list dashboard is deliberately kept lightweight (no full gallery there, by design --
  // see CitizenDashboard.tsx) -- open the complaint's own detail page to see the real gallery.
  const citizenCard = page.locator(".surface-card").filter({ hasText: "Two photos of the same broken streetlight." });
  await citizenCard.getByText(/JM-\d+/).click();
  await page.waitForURL(/\/citizen\/complaints\/\d+$/);
  await expect(page.locator(".evidence-thumb")).toHaveCount(2);
  await logout(page);

  // --- Worker accepts, starts work with an evidence photo, completes with another. ---
  await login(page, workerPhone, "workerpass123");
  await expect(page).toHaveURL(/\/worker$/);
  const card = page.locator(".surface-card").filter({ hasText: "Two photos of the same broken streetlight." });
  await card.locator('button:has-text("Accept")').click();
  await page.waitForTimeout(1000);
  await card.getByText(/JM-\d+/).click();
  await page.waitForURL(/\/worker\/complaints\/\d+$/);
  const complaintUrl = page.url();

  await page.getByRole("button", { name: "Start Work" }).click();
  const startModal = page.locator(".modal");
  await page.getByLabel("Initial assessment").fill("Confirmed via both citizen photos -- bulb needs replacing.");
  await startModal.locator('input[type="file"]').setInputFiles({ name: "assessment.jpg", mimeType: "image/jpeg", buffer: JPEG_1PX });
  await expect(startModal.locator(".multi-photo-thumb")).toHaveCount(1);
  await startModal.getByRole("button", { name: "Start Work", exact: true }).click();
  await page.waitForTimeout(1000);

  await page.getByRole("button", { name: "Complete Complaint" }).click();
  const completeModal = page.locator(".modal");
  await page.getByLabel("Completion status").fill("Bulb replaced, tested working.");
  await completeModal.locator('input[type="file"]').setInputFiles([
    { name: "final-1.jpg", mimeType: "image/jpeg", buffer: JPEG_1PX },
    { name: "final-2.png", mimeType: "image/png", buffer: PNG_1PX },
  ]);
  await expect(completeModal.locator(".multi-photo-thumb")).toHaveCount(2);
  await completeModal.getByRole("button", { name: "Mark Resolved", exact: true }).click();
  await page.waitForTimeout(1000);

  // Detail page shows 5 distinct real files (2 citizen + 1 initial-assessment + 2 completion) --
  // rendered twice over, once in the Updates timeline and again in the Resolution Report section
  // below it (the report intentionally repeats the same real facts already shown above, exactly
  // like the PDF does -- see ComplaintReportView.tsx), so 10 thumbnails total.
  await expect(page.locator(".evidence-thumb")).toHaveCount(10);

  // Click a thumbnail -> lightbox opens with a real, loadable image.
  await page.locator(".evidence-thumb").first().click();
  const lightboxImg = page.locator(".evidence-lightbox-img");
  await expect(lightboxImg).toBeVisible();
  const naturalWidth = await lightboxImg.evaluate((img: HTMLImageElement) => img.naturalWidth);
  expect(naturalWidth).toBeGreaterThan(0); // the browser actually decoded a real image, not a broken link
  await page.keyboard.press("Escape");

  // Report (both JSON view and PDF) reflects the same evidence.
  await expect(page.getByText("Resolution Report", { exact: true })).toBeVisible();
  // 30s, not 15s: this report embeds 5 real images (reportlab reads + decodes each from disk),
  // legitimately slower to generate than the text-only report the shorter timeout elsewhere in
  // this suite was calibrated against.
  const [download] = await Promise.all([
    page.waitForEvent("download", { timeout: 30000 }),
    page.getByRole("button", { name: "Download Report" }).click(),
  ]);
  const fs = await import("node:fs");
  const downloadPath = await download.path();
  const pdfBytes = fs.readFileSync(downloadPath!);
  expect(pdfBytes.subarray(0, 4).toString()).toBe("%PDF");
  expect(pdfBytes.length).toBeGreaterThan(5000); // a report with 5 embedded images is not a tiny/empty PDF

  await logout(page);

  // --- Citizen sees the worker's evidence too, on their own detail page. Same 10 (5 real files,
  // shown twice -- Updates timeline + Resolution Report) as the worker's view above. ---
  await login(page, citizenPhone, "citizenpass123");
  await page.goto(complaintUrl.replace("/worker/", "/citizen/"));
  // Longer timeout here specifically: a fresh full navigation (page.goto, not client-side
  // routing) has to load the app shell, authenticate, and fetch the complaint detail before
  // anything renders -- the default 5s auto-retry window this matcher normally gets isn't
  // always enough for that first paint under load.
  await expect(page.locator(".evidence-thumb")).toHaveCount(10, { timeout: 15000 });
});

import { test, expect } from "@playwright/test";
import { uniquePhone } from "./helpers";

/**
 * E2E coverage for Ask JanMitra's image-attachment UI (phase 3 of the multimodal upgrade) against
 * the REAL backend (POST /ask-janmitra/image) -- not a mock. Phase 3 scope only: the image is
 * genuinely selected/previewed/removed and really uploaded, but does not yet influence the
 * answer (that's wired in a later phase) -- so the assertions here match ask-janmitra.spec.ts's
 * existing "grounded answer" expectations for the exact same question, proving the image upload
 * is real plumbing, not a UI-only mock, without yet claiming any image-understanding behavior.
 *
 * A minimal, genuinely valid 1x1 JPEG (not just fake bytes with a jpeg-ish prefix), same fixture
 * style already used by e2e/evidence-upload.spec.ts.
 */
const JPEG_1PX = Buffer.from(
  "/9j/4AAQSkZJRgABAQEAYABgAAD/2wBDAAMCAgICAgMCAgIDAwMDBAYEBAQEBAgGBgUGCQgKCgkICQkKDA8MCgsOCwkJDRENDg8QEBEQCgwSExIQEw8QEBD/2wBDAQMDAwQDBAgEBAgQCwkLEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBD/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAj/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFQEBAQAAAAAAAAAAAAAAAAAAAAX/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIRAxEAPwCdABmX/9k=",
  "base64"
);

async function signUpAndReachCitizenHome(page: import("@playwright/test").Page) {
  await page.goto("/");
  await page.getByRole("button", { name: "English" }).click();
  await expect(page).toHaveURL(/\/welcome$/);
  await page.getByRole("link", { name: "Sign up" }).click();
  await expect(page).toHaveURL(/\/signup$/);

  const phone = uniquePhone();
  await page.getByLabel("Full name").fill("Ask JanMitra Image Tester");
  await page.getByLabel("Phone number").fill(phone);
  await page.getByLabel("Password").fill("secret123");
  await page.getByRole("button", { name: "Create account" }).click();
  await expect(page).toHaveURL(/\/citizen$/);
}

test("Ask JanMitra: attaching a real photo previews it, removing it works, and sending with a question still returns a grounded answer", async ({ page }) => {
  // Real backend round-trip PLUS a real local vision-language model call (VisionService,
  // ~1.9B params, CPU inference) -- on a cold backend process this pays a genuine one-time model
  // load from disk (already-downloaded weights, not a network fetch) on top of the usual RAG
  // round-trip, so this needs a much larger budget than the plain-text ask-janmitra.spec.ts tests
  // (60s) -- measured directly: a cold load + one caption comfortably exceeded 35s on this
  // machine's CPU-only setup.
  test.setTimeout(180000);

  await signUpAndReachCitizenHome(page);
  await page.getByRole("button", { name: "Ask JanMitra" }).click();

  // Select a real image through the actual <input type=file> the MultiPhotoUpload component
  // renders -- not a mocked file object.
  await page.locator('input[type="file"]').setInputFiles({ name: "streetlight.jpg", mimeType: "image/jpeg", buffer: JPEG_1PX });
  await expect(page.locator(".multi-photo-thumb")).toHaveCount(1);

  // Remove it, then re-attach -- proves both the preview and the remove control are wired to
  // real state, not just a one-shot render.
  await page.locator(".multi-photo-remove").click();
  await expect(page.locator(".multi-photo-thumb")).toHaveCount(0);
  await page.locator('input[type="file"]').setInputFiles({ name: "streetlight.jpg", mimeType: "image/jpeg", buffer: JPEG_1PX });
  await expect(page.locator(".multi-photo-thumb")).toHaveCount(1);

  // Same TYPE_B (information) phrasing ask-janmitra.spec.ts's own grounded-answer test uses --
  // sending it with an attached image must still produce the same kind of real, sourced answer.
  await page.getByPlaceholder(/Ask about a civic service/i).fill("Who do I contact about street lights in Mohali?");
  await page.getByRole("button", { name: "Ask", exact: true }).click();

  // Larger than ask-janmitra.spec.ts's 30s -- a cold backend process pays a one-time real model
  // load (see the test-level comment above) on top of the usual RAG round-trip.
  await expect(page.locator(".ask-answer-text")).toBeVisible({ timeout: 150000 });
  await expect(page.getByText("Official source", { exact: true })).toBeVisible();

  // The attached photo is cleared after a successful send (see AskJanMitra.tsx's runQuery) --
  // not left behind to be silently resent on the next unrelated question.
  await expect(page.locator(".multi-photo-thumb")).toHaveCount(0);
});

test("Ask JanMitra: the submit button is enabled with only an image attached, no text typed", async ({ page }) => {
  await signUpAndReachCitizenHome(page);
  await page.getByRole("button", { name: "Ask JanMitra" }).click();

  const submitButton = page.getByRole("button", { name: "Ask", exact: true });
  await expect(submitButton).toBeDisabled();

  await page.locator('input[type="file"]').setInputFiles({ name: "photo.jpg", mimeType: "image/jpeg", buffer: JPEG_1PX });

  await expect(submitButton).toBeEnabled();
});

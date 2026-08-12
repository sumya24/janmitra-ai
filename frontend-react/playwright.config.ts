import { defineConfig, devices } from "@playwright/test";

export default defineConfig({
  testDir: "./e2e",
  fullyParallel: false,
  workers: 1,
  // One retry, locally too (not just CI's usual default). Justified by measurement, not blanket
  // flakiness tolerance: two suite runs in this project's integration/stability phase timed the
  // real (non-mocked) complaint-creation pipeline directly -- three sequential real Sarvam calls
  // (normalize -> translate -> summarize, four for the voice path) measured 17.7s/28.5s/18.7s in
  // one sample, then exceeded an already-evidence-based 60s timeout on a later run. That's a
  // long-tail external-API latency distribution this project doesn't control, not a bug in this
  // codebase (see e2e/complaint-tracking.spec.ts's and theme-and-voice.spec.ts's own submission-
  // assertion comments for the full data). A retry doesn't weaken what "pass" requires -- the
  // exact same strict assertions must still succeed -- it just gives a second real attempt
  // instead of failing the whole suite on one slow external call.
  retries: 1,
  reporter: "list",
  use: {
    // Use "localhost" rather than the literal 127.0.0.1: on some setups (notably seen
    // on Windows) the dev server ends up reachable only via the IPv6 loopback that
    // "localhost" resolves to, and a hardcoded IPv4 address fails to connect.
    baseURL: "http://localhost:5173",
    trace: "retain-on-failure",
  },
  projects: [
    {
      name: "chromium",
      use: {
        ...devices["Desktop Chrome"],
        // Fake mic device + auto-accept the permission prompt, so voice-recording
        // tests can exercise MediaRecorder without a real microphone or a human
        // clicking "Allow".
        permissions: ["microphone"],
        launchOptions: {
          // Only override the browser binary if PLAYWRIGHT_CHROMIUM_PATH is set (e.g. a
          // sandboxed CI image with a pre-installed build at a fixed path). Locally, leave
          // it undefined so Playwright launches the browser it installed via
          // `npx playwright install`, which works on any OS.
          executablePath: process.env.PLAYWRIGHT_CHROMIUM_PATH || undefined,
          args: ["--use-fake-device-for-media-stream", "--use-fake-ui-for-media-stream"],
        },
      },
    },
  ],
});

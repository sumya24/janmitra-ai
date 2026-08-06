import { defineConfig, devices } from "@playwright/test";

export default defineConfig({
  testDir: "./e2e",
  fullyParallel: false,
  workers: 1,
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

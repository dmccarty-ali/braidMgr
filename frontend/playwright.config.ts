// =============================================================================
// Playwright + BDD Configuration
// Uses playwright-bdd to run Gherkin feature files with Playwright
// Also supports regular Playwright tests for demo recording
// =============================================================================

import { defineConfig, devices } from "@playwright/test"
import { defineBddConfig } from "playwright-bdd"

// Configure BDD - tells playwright-bdd where to find features and steps
const bddTestDir = defineBddConfig({
  features: "e2e/features/**/*.feature",
  steps: "e2e/steps/**/*.ts",
})

export default defineConfig({
  // Directory containing generated test files (BDD)
  // Note: demo-recording project overrides this to use tests/ directory
  testDir: bddTestDir,

  // Run tests in parallel
  fullyParallel: true,

  // Fail the build on CI if you accidentally left test.only in the source code
  forbidOnly: !!process.env.CI,

  // Retry on CI only
  retries: process.env.CI ? 2 : 0,

  // Opt out of parallel tests on CI
  workers: process.env.CI ? 1 : undefined,

  // Reporter to use
  reporter: [
    ["html", { open: "never", outputFolder: "e2e-report" }],
    ["list"],
  ],

  // Shared settings for all the projects below
  use: {
    // Base URL to use in actions like `await page.goto('/')`
    // Using port 5174 to avoid conflicts with other dev servers
    baseURL: "http://localhost:5174",

    // Collect trace when retrying the failed test
    trace: "on-first-retry",

    // Take screenshot on failure
    screenshot: "only-on-failure",
  },

  // Configure projects for major browsers
  projects: [
    {
      name: "chromium",
      use: { ...devices["Desktop Chrome"] },
    },
    // Demo project - records video with larger viewport (for BDD features)
    {
      name: "demo",
      testMatch: /demo\.feature\.spec\.js/,
      use: {
        ...devices["Desktop Chrome"],
        // Larger viewport for better recording quality
        viewport: { width: 1920, height: 1080 },
        // Record video for demo
        video: {
          mode: "on",
          size: { width: 1920, height: 1080 },
        },
        // Longer timeout for demo with pauses
        actionTimeout: 60000,
      },
      // Longer test timeout for demo
      timeout: 300000, // 5 minutes
    },
    // Demo recording project - for standard Playwright tests with video
    {
      name: "demo-recording",
      testDir: "./tests",
      testMatch: /demo-walkthrough\.spec\.ts/,
      use: {
        ...devices["Desktop Chrome"],
        // 1080p viewport for high-quality recording
        viewport: { width: 1920, height: 1080 },
        // Always record video
        video: {
          mode: "on",
          size: { width: 1920, height: 1080 },
        },
        // Take screenshots
        screenshot: "on",
        // Full trace for debugging
        trace: "on",
        // Slow down actions for smoother demo
        launchOptions: {
          slowMo: 50,
        },
        // Longer timeout for demo with pauses
        actionTimeout: 60000,
      },
      // 5 minute timeout for demo walkthrough
      timeout: 300000,
    },
    // Uncomment to test on more browsers:
    // {
    //   name: "firefox",
    //   use: { ...devices["Desktop Firefox"] },
    // },
    // {
    //   name: "webkit",
    //   use: { ...devices["Desktop Safari"] },
    // },
  ],

  // Run local dev server before starting the tests
  // Always start a fresh server to avoid conflicts with other processes
  webServer: {
    command: "npm run dev -- --port 5174",
    url: "http://localhost:5174",
    reuseExistingServer: false,
    timeout: 120 * 1000,
  },
})

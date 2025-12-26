// =============================================================================
// Authentication Step Definitions (playwright-bdd)
// Steps specific to login, logout, and registration flows
// =============================================================================

import { expect } from "@playwright/test"
import { createBdd } from "playwright-bdd"

const { Given, When, Then } = createBdd()

// =============================================================================
// Test User Credentials
// =============================================================================
// These are test accounts that should exist in your test database.
// In a real project, you might load these from environment variables.

const TEST_USERS = {
  valid: {
    email: "e2e-test@example.com",
    password: "E2eTestPass123",
  },
  admin: {
    email: "e2e-test@example.com",
    password: "E2eTestPass123",
  },
}

// =============================================================================
// Login Steps
// =============================================================================

// Test project UUID - created by e2e test setup
const TEST_PROJECT_ID = "22222222-2222-2222-2222-222222222222"

Given("I am logged in", async ({ page }) => {
  // Navigate to login and authenticate with default test user
  await page.goto("/login")
  await page.waitForLoadState("networkidle")

  await page.getByLabel("Email").fill(TEST_USERS.valid.email)
  await page.getByLabel("Password").fill(TEST_USERS.valid.password)
  await page.getByRole("button", { name: /sign in|log in/i }).click()

  // Wait for redirect away from login page (to /projects)
  await page.waitForURL((url) => !url.pathname.includes("/login"), {
    timeout: 10000,
  })

  // Wait for projects page to load
  await page.waitForLoadState("networkidle")

  // Click on the test project to navigate (client-side routing preserves auth)
  // This keeps us in the SPA so in-memory tokens are preserved
  await page.getByText("Website Modernization").click()

  // Wait for project dashboard to load
  await page.waitForURL((url) => url.pathname.includes(TEST_PROJECT_ID), {
    timeout: 10000,
  })
  await page.waitForLoadState("networkidle")
})

Given("I am logged in as {string}", async ({ page }, userType: string) => {
  const user = TEST_USERS[userType as keyof typeof TEST_USERS] || TEST_USERS.valid

  await page.goto("/login")
  await page.getByLabel("Email").fill(user.email)
  await page.getByLabel("Password").fill(user.password)
  await page.getByRole("button", { name: /sign in|log in/i }).click()

  await page.waitForURL(/\/(projects|dashboard)/, { timeout: 10000 })
})

Given("I am not logged in", async ({ page, context }) => {
  // Clear any existing auth tokens
  await context.clearCookies()
  await page.goto("/")
  await page.evaluate(() => localStorage.clear())
})

When(
  "I log in with email {string} and password {string}",
  async ({ page }, email: string, password: string) => {
    await page.getByLabel("Email").fill(email)
    await page.getByLabel("Password").fill(password)
    await page.getByRole("button", { name: /sign in|log in/i }).click()
  }
)

When("I log in with valid credentials", async ({ page }) => {
  await page.getByLabel("Email").fill(TEST_USERS.valid.email)
  await page.getByLabel("Password").fill(TEST_USERS.valid.password)
  await page.getByRole("button", { name: /sign in|log in/i }).click()
})

When("I log in with invalid credentials", async ({ page }) => {
  await page.getByLabel("Email").fill("wrong@example.com")
  await page.getByLabel("Password").fill("WrongPassword123!")
  await page.getByRole("button", { name: /sign in|log in/i }).click()
})

// =============================================================================
// Logout Steps
// =============================================================================

When("I log out", async ({ page }) => {
  // Click logout button (might be in header or menu)
  const logoutButton = page.getByRole("button", { name: /log ?out|sign ?out/i })
  if (await logoutButton.isVisible()) {
    await logoutButton.click()
  } else {
    // Try opening a menu first
    const menuButton = page.getByRole("button", { name: /menu|profile|account/i })
    if (await menuButton.isVisible()) {
      await menuButton.click()
      await page.getByRole("menuitem", { name: /log ?out|sign ?out/i }).click()
    }
  }
})

// =============================================================================
// Registration Steps
// =============================================================================

When(
  "I register with email {string} and password {string}",
  async ({ page }, email: string, password: string) => {
    // Fill in name if field exists
    const nameField = page.getByLabel("Name")
    if (await nameField.isVisible({ timeout: 1000 }).catch(() => false)) {
      await nameField.fill("Test User")
    }

    await page.getByLabel("Email").fill(email)
    await page.getByLabel("Password").fill(password)

    // Look for confirm password field
    const confirmPassword = page.getByLabel(/confirm password/i)
    if (await confirmPassword.isVisible()) {
      await confirmPassword.fill(password)
    }

    await page.getByRole("button", { name: /sign up|register|create account/i }).click()
  }
)

When("I register with a unique email and valid password", async ({ page }) => {
  // Generate unique email using timestamp
  const timestamp = Date.now()
  const email = `e2e-test-${timestamp}@example.com`
  const password = "ValidTestPass123!"
  const name = `Test User ${timestamp}`

  // Wait for the form to be ready
  await page.waitForLoadState("networkidle")

  // Fill in all fields using id selectors for reliability
  await page.locator("#name").fill(name)
  await page.locator("#email").fill(email)
  await page.locator("#password").fill(password)
  await page.locator("#confirmPassword").fill(password)

  // Click submit and wait for navigation
  await page.getByRole("button", { name: "Create account" }).click()

  // Wait for API response
  await page.waitForLoadState("networkidle")
})

// =============================================================================
// Auth State Assertions
// =============================================================================

Then("I should be logged in", async ({ page }) => {
  // Check for logged-in indicators
  await expect(
    page.getByRole("button", { name: /log ?out|sign ?out|profile/i })
  ).toBeVisible({ timeout: 5000 })
})

Then("I should be logged out", async ({ page }) => {
  // Should see login link/button
  await expect(
    page.getByRole("link", { name: /log ?in|sign ?in/i })
  ).toBeVisible({ timeout: 5000 })
})

Then("I should see an authentication error", async ({ page }) => {
  // Look for error messages - wait a bit for async validation
  await page.waitForTimeout(500)

  // Check for common error patterns
  const errorLocator = page.locator('[role="alert"], .text-destructive, [class*="error"]')
  await expect(errorLocator.first()).toBeVisible({ timeout: 5000 })
})

Then("I should be redirected to the login page", async ({ page }) => {
  await expect(page).toHaveURL(/\/login/)
})

Then("I should be redirected to the dashboard", async ({ page }) => {
  await expect(page).toHaveURL(/\/(dashboard|projects)/)
})

Then("I should be redirected to the projects page", async ({ page }) => {
  await expect(page).toHaveURL(/\/projects/, { timeout: 10000 })
})

Then("I should see an error about password requirements", async ({ page }) => {
  // Wait for validation error about password strength
  await page.waitForTimeout(500)
  const errorLocator = page.locator('[role="alert"], .text-destructive, [class*="error"]')
  await expect(errorLocator.first()).toBeVisible({ timeout: 5000 })
})

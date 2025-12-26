// =============================================================================
// Common Step Definitions (playwright-bdd)
// Reusable steps for navigation, forms, and assertions
// =============================================================================
// These steps can be used in any feature file. They provide generic actions
// like navigating to pages, filling forms, clicking buttons, and checking text.
//
// Gherkin Pattern Syntax:
// - {string} captures quoted text: "login" in 'I am on the "login" page'
// - {int} captures numbers: 5 in "I wait 5 seconds"
// =============================================================================

import { expect } from "@playwright/test"
import { createBdd } from "playwright-bdd"

const { Given, When, Then } = createBdd()

// =============================================================================
// Page URL Mapping
// =============================================================================

// Test project UUID - created by e2e test setup
const TEST_PROJECT_ID = "22222222-2222-2222-2222-222222222222"

const pageUrls: Record<string, string> = {
  login: "/login",
  register: "/register",
  home: "/",
  projects: "/projects",
  dashboard: `/projects/${TEST_PROJECT_ID}/dashboard`,
  "all items": `/projects/${TEST_PROJECT_ID}/items`,
  "active items": `/projects/${TEST_PROJECT_ID}/active`,
  timeline: `/projects/${TEST_PROJECT_ID}/timeline`,
  chronology: `/projects/${TEST_PROJECT_ID}/chronology`,
  help: `/projects/${TEST_PROJECT_ID}/help`,
}

// =============================================================================
// Navigation Steps
// =============================================================================

Given("I am on the {string} page", async ({ page }, pageName: string) => {
  const targetUrl = pageUrls[pageName.toLowerCase()] || `/${pageName}`

  // If already on the target page (or close), skip navigation to preserve in-memory auth
  const currentUrl = page.url()
  if (currentUrl.includes(targetUrl.replace(/^\//, ""))) {
    return
  }

  // For auth-protected pages within a project, check if we're already in that project
  // to avoid full page reload that would wipe in-memory token
  if (targetUrl.includes(TEST_PROJECT_ID)) {
    const currentPath = new URL(currentUrl).pathname
    if (currentPath.includes(TEST_PROJECT_ID)) {
      // Already in the project, use navigation link instead of page.goto
      // Extract page name from URL (e.g., "dashboard", "items")
      const pagePart = targetUrl.split("/").pop()
      if (pagePart) {
        // Try to find and click navigation link
        const navLink = page.getByRole("link", { name: new RegExp(pagePart, "i") })
        if (await navLink.isVisible({ timeout: 1000 }).catch(() => false)) {
          await navLink.click()
          await page.waitForLoadState("networkidle")
          return
        }
      }
    }
  }

  // Fallback to standard navigation
  await page.goto(targetUrl)
})

Given("I navigate to {string}", async ({ page }, path: string) => {
  await page.goto(path)
})

When("I go back", async ({ page }) => {
  await page.goBack()
})

When("I refresh the page", async ({ page }) => {
  await page.reload()
})

// =============================================================================
// Form Interaction Steps
// =============================================================================

When(
  "I fill in {string} with {string}",
  async ({ page }, field: string, value: string) => {
    // Try multiple selectors to find the input
    const selectors = [
      `input[name="${field}"]`,
      `input[placeholder*="${field}" i]`,
      `textarea[name="${field}"]`,
      `[aria-label="${field}"]`,
    ]

    for (const selector of selectors) {
      const element = page.locator(selector).first()
      if (await element.isVisible().catch(() => false)) {
        await element.fill(value)
        return
      }
    }

    // If no specific selector works, try getByLabel
    await page.getByLabel(field).fill(value)
  }
)

When("I clear the {string} field", async ({ page }, field: string) => {
  await page.getByLabel(field).clear()
})

When("I check {string}", async ({ page }, label: string) => {
  await page.getByLabel(label).check()
})

When("I uncheck {string}", async ({ page }, label: string) => {
  await page.getByLabel(label).uncheck()
})

When(
  "I select {string} from {string}",
  async ({ page }, option: string, dropdown: string) => {
    await page.getByLabel(dropdown).selectOption(option)
  }
)

// =============================================================================
// Button and Link Steps
// =============================================================================

When("I click {string}", async ({ page }, text: string) => {
  await page.getByRole("button", { name: text }).click()
})

When("I click the {string} button", async ({ page }, text: string) => {
  await page.getByRole("button", { name: text }).click()
})

When("I click the {string} link", async ({ page }, text: string) => {
  await page.getByRole("link", { name: text }).click()
})

// =============================================================================
// Assertion Steps
// =============================================================================

Then("I should see {string}", async ({ page }, text: string) => {
  await expect(page.getByText(text)).toBeVisible()
})

Then("I should not see {string}", async ({ page }, text: string) => {
  await expect(page.getByText(text)).not.toBeVisible()
})

Then("I should see the {string} heading", async ({ page }, text: string) => {
  await expect(page.getByRole("heading", { name: text })).toBeVisible()
})

Then("the page title should be {string}", async ({ page }, title: string) => {
  await expect(page).toHaveTitle(title)
})

Then("the URL should contain {string}", async ({ page }, text: string) => {
  await expect(page).toHaveURL(new RegExp(text))
})

Then("the URL should be {string}", async ({ page }, url: string) => {
  await expect(page).toHaveURL(url)
})

Then(
  "the {string} field should have value {string}",
  async ({ page }, field: string, value: string) => {
    await expect(page.getByLabel(field)).toHaveValue(value)
  }
)

Then("the {string} button should be disabled", async ({ page }, text: string) => {
  await expect(page.getByRole("button", { name: text })).toBeDisabled()
})

Then("the {string} button should be enabled", async ({ page }, text: string) => {
  await expect(page.getByRole("button", { name: text })).toBeEnabled()
})

// =============================================================================
// Wait Steps
// =============================================================================

When("I wait for the page to load", async ({ page }) => {
  await page.waitForLoadState("networkidle")
})

When("I wait {int} seconds", async ({ page }, seconds: number) => {
  await page.waitForTimeout(seconds * 1000)
})

// =============================================================================
// Items Step Definitions
// Steps for item viewing and filtering tests
// =============================================================================

import { createBdd } from "playwright-bdd"
import { expect } from "@playwright/test"

const { Given, When, Then } = createBdd()

// =============================================================================
// Viewing Items
// =============================================================================

Then(
  "I should see a table with items",
  async ({ page }) => {
    await expect(page.locator("table")).toBeVisible()
    // Should have at least one row
    const rows = page.locator("table tbody tr")
    await expect(rows.first()).toBeVisible()
  }
)

Then(
  "I should see item numbers in the table",
  async ({ page }) => {
    // Item numbers appear in first column
    const firstCell = page.locator("table tbody tr:first-child td:first-child")
    await expect(firstCell).toBeVisible()
    // Should contain a number
    const text = await firstCell.textContent()
    expect(text).toMatch(/^\d+$/)
  }
)

Then(
  "I should see item types in the table",
  async ({ page }) => {
    // Look for known item types
    const validTypes = ["Budget", "Risk", "Action", "Issue", "Decision", "Deliverable", "Plan Item"]
    const table = page.locator("table")
    let foundType = false

    for (const type of validTypes) {
      const count = await table.locator(`text=${type}`).count()
      if (count > 0) {
        foundType = true
        break
      }
    }

    expect(foundType).toBe(true)
  }
)

Then(
  "I should see item titles in the table",
  async ({ page }) => {
    // Titles appear in the title column - should be non-empty text
    const titleCells = page.locator("table tbody tr td:nth-child(3)")
    const firstTitle = await titleCells.first().textContent()
    expect(firstTitle?.trim().length).toBeGreaterThan(0)
  }
)

// =============================================================================
// Filtering Items
// =============================================================================

When(
  "I select {string} from the type filter",
  async ({ page }, filterValue: string) => {
    // Click on the type filter dropdown
    await page.locator('[data-testid="type-filter"]').click()
    // Select the value
    await page.locator(`[role="option"]:has-text("${filterValue}")`).first().click()
    // Wait for filter to apply
    await page.waitForTimeout(500)
  }
)

Then(
  "all visible items should be of type {string}",
  async ({ page }, expectedType: string) => {
    const rows = page.locator("table tbody tr")
    const count = await rows.count()

    if (count > 0) {
      // Each row should contain the expected type
      for (let i = 0; i < Math.min(count, 5); i++) {
        const row = rows.nth(i)
        await expect(row).toContainText(expectedType)
      }
    }
  }
)

When(
  "I select {string} from the indicator filter",
  async ({ page }, filterValue: string) => {
    await page.locator('[data-testid="indicator-filter"]').click()
    await page.locator(`[role="option"]:has-text("${filterValue}")`).first().click()
    await page.waitForTimeout(500)
  }
)

Then(
  "all visible items should have indicator {string}",
  async ({ page }, expectedIndicator: string) => {
    const rows = page.locator("table tbody tr")
    const count = await rows.count()

    if (count > 0) {
      for (let i = 0; i < Math.min(count, 5); i++) {
        const row = rows.nth(i)
        await expect(row).toContainText(expectedIndicator)
      }
    }
  }
)

When(
  "I search for {string}",
  async ({ page }, searchTerm: string) => {
    const searchInput = page.locator('[placeholder*="Search"]')
    await searchInput.fill(searchTerm)
    await page.waitForTimeout(500)
  }
)

Then(
  "visible items should contain {string} in the title",
  async ({ page }, searchTerm: string) => {
    const rows = page.locator("table tbody tr")
    const count = await rows.count()

    if (count > 0) {
      for (let i = 0; i < count; i++) {
        const row = rows.nth(i)
        const text = await row.textContent()
        expect(text?.toLowerCase()).toContain(searchTerm.toLowerCase())
      }
    }
  }
)

Given(
  "I have applied filters",
  async ({ page }) => {
    // Apply a type filter
    await page.locator('[data-testid="type-filter"]').click()
    await page.locator('[role="option"]:has-text("Risk")').first().click()
    await page.waitForTimeout(500)
  }
)

Then(
  "all filters should be cleared",
  async ({ page }) => {
    // Verify the type filter is reset
    const typeFilter = page.locator('[data-testid="type-filter"]')
    await expect(typeFilter).toContainText("All Types")
  }
)

Then(
  "I should see all items",
  async ({ page }) => {
    const rows = page.locator("table tbody tr")
    const count = await rows.count()
    // Should see multiple items after clearing filters
    expect(count).toBeGreaterThan(0)
  }
)

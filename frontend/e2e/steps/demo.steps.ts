/**
 * Demo step definitions with narration overlays
 *
 * These steps inject styled overlay boxes onto the page to narrate
 * what's happening during the demo recording.
 */

import { Given, When, Then } from "@cucumber/cucumber"
import { createBdd } from "playwright-bdd"

const { Given: BddGiven, When: BddWhen, Then: BddThen } = createBdd()

// =============================================================================
// NARRATION OVERLAY
// =============================================================================

// Inject a narration overlay onto the page
async function showNarration(
  page: any,
  title: string,
  description: string
): Promise<void> {
  await page.evaluate(
    ({ title, description }: { title: string; description: string }) => {
      // Remove any existing narration
      const existing = document.getElementById("demo-narration")
      if (existing) existing.remove()

      // Create overlay container
      const overlay = document.createElement("div")
      overlay.id = "demo-narration"
      overlay.style.cssText = `
        position: fixed;
        bottom: 40px;
        left: 50%;
        transform: translateX(-50%);
        z-index: 99999;
        background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
        color: white;
        padding: 24px 40px;
        border-radius: 16px;
        box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
        max-width: 700px;
        text-align: center;
        font-family: system-ui, -apple-system, sans-serif;
        animation: slideUp 0.5s ease-out;
        border: 1px solid rgba(255, 255, 255, 0.1);
      `

      // Add animation keyframes
      const style = document.createElement("style")
      style.textContent = `
        @keyframes slideUp {
          from {
            opacity: 0;
            transform: translateX(-50%) translateY(30px);
          }
          to {
            opacity: 1;
            transform: translateX(-50%) translateY(0);
          }
        }
      `
      document.head.appendChild(style)

      // Title
      const titleEl = document.createElement("h2")
      titleEl.textContent = title
      titleEl.style.cssText = `
        margin: 0 0 12px 0;
        font-size: 28px;
        font-weight: 700;
        letter-spacing: -0.5px;
        background: linear-gradient(90deg, #60a5fa, #a78bfa);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
      `
      overlay.appendChild(titleEl)

      // Description
      const descEl = document.createElement("p")
      descEl.textContent = description
      descEl.style.cssText = `
        margin: 0;
        font-size: 16px;
        line-height: 1.6;
        color: #cbd5e1;
        font-weight: 400;
      `
      overlay.appendChild(descEl)

      document.body.appendChild(overlay)
    },
    { title, description }
  )
}

// Remove narration overlay
async function hideNarration(page: any): Promise<void> {
  await page.evaluate(() => {
    const existing = document.getElementById("demo-narration")
    if (existing) {
      existing.style.animation = "slideDown 0.3s ease-in forwards"
      setTimeout(() => existing.remove(), 300)
    }
  })
}

// =============================================================================
// DEMO STEP DEFINITIONS
// =============================================================================

BddGiven(
  "I show the narration {string} with description {string}",
  async ({ page }, title: string, description: string) => {
    await showNarration(page, title, description)
  }
)

BddWhen(
  "I hide the narration",
  async ({ page }) => {
    await hideNarration(page)
  }
)

BddWhen(
  "I wait for {string} seconds",
  async ({ page }, seconds: string) => {
    await page.waitForTimeout(parseInt(seconds) * 1000)
  }
)

BddWhen(
  "I click on project {string}",
  async ({ page }, projectName: string) => {
    // Hide narration before clicking
    await hideNarration(page)
    await page.waitForTimeout(300)

    // Click the project
    await page.getByText(projectName).click()

    // Wait for navigation
    await page.waitForLoadState("networkidle")
  }
)

// =============================================================================
// HIGHLIGHT STEP (optional - highlights elements during demo)
// =============================================================================

BddGiven(
  "I highlight the {string} element",
  async ({ page }, selector: string) => {
    await page.evaluate((sel: string) => {
      const el = document.querySelector(sel)
      if (el) {
        (el as HTMLElement).style.outline = "3px solid #60a5fa"
        ;(el as HTMLElement).style.outlineOffset = "4px"
        ;(el as HTMLElement).style.transition = "outline 0.3s ease"
      }
    }, selector)
  }
)

BddWhen(
  "I remove all highlights",
  async ({ page }) => {
    await page.evaluate(() => {
      document.querySelectorAll("[style*='outline']").forEach((el) => {
        ;(el as HTMLElement).style.outline = ""
        ;(el as HTMLElement).style.outlineOffset = ""
      })
    })
  }
)

// =============================================================================
// Indicator Configuration
// Colors and severity levels for RAID item status indicators
// =============================================================================

import type { Indicator } from "@/types"

// Indicator configuration with badge variant and severity
export interface IndicatorConfig {
  // Badge variant for styling
  variant: "destructive" | "warning" | "success" | "info" | "muted" | "default"
  // Severity level (10 = most severe, 1 = least severe)
  severity: number
  // Short description for tooltips
  description: string
}

// Configuration for each indicator type
export const indicatorConfig: Record<Indicator, IndicatorConfig> = {
  "Beyond Deadline!!!": {
    variant: "destructive",
    severity: 10,
    description: "Past deadline and not complete",
  },
  "Late Finish!!": {
    variant: "destructive",
    severity: 9,
    description: "Finish date has passed but not complete",
  },
  "Late Start!!": {
    variant: "destructive",
    severity: 8,
    description: "Start date has passed but not started",
  },
  "Trending Late!": {
    variant: "warning",
    severity: 7,
    description: "Progress behind schedule",
  },
  "Finishing Soon!": {
    variant: "warning",
    severity: 6,
    description: "Finish date approaching",
  },
  "Starting Soon!": {
    variant: "info",
    severity: 5,
    description: "Start date approaching",
  },
  "In Progress": {
    variant: "default",
    severity: 4,
    description: "Work is ongoing",
  },
  "Not Started": {
    variant: "muted",
    severity: 3,
    description: "Not yet begun",
  },
  "Completed Recently": {
    variant: "success",
    severity: 2,
    description: "Finished in the last 7 days",
  },
  "Completed": {
    variant: "muted",
    severity: 1,
    description: "Work is done",
  },
}

// Get config for an indicator (with fallback for null)
export function getIndicatorConfig(indicator: Indicator | null): IndicatorConfig {
  if (!indicator) {
    return { variant: "muted", severity: 0, description: "No status" }
  }
  return indicatorConfig[indicator]
}

// Get variant for an indicator
export function getIndicatorVariant(
  indicator: Indicator | null
): IndicatorConfig["variant"] {
  return getIndicatorConfig(indicator).variant
}

// Get severity for an indicator
export function getIndicatorSeverity(indicator: Indicator | null): number {
  return getIndicatorConfig(indicator).severity
}

// Sort items by indicator severity (most severe first)
export function sortByIndicatorSeverity<T extends { indicator: Indicator | null }>(
  items: T[]
): T[] {
  return [...items].sort((a, b) => {
    const severityA = getIndicatorSeverity(a.indicator)
    const severityB = getIndicatorSeverity(b.indicator)
    return severityB - severityA
  })
}

// Group items by indicator
export function groupByIndicator<T extends { indicator: Indicator | null }>(
  items: T[]
): Map<Indicator | null, T[]> {
  const groups = new Map<Indicator | null, T[]>()
  for (const item of items) {
    const key = item.indicator
    const existing = groups.get(key) || []
    groups.set(key, [...existing, item])
  }
  return groups
}

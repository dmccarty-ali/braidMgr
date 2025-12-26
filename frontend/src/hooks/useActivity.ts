// =============================================================================
// Activity React Query Hook
// Fetches project activity feed from the backend
// =============================================================================

import { useQuery } from "@tanstack/react-query"
import { apiGet } from "@/lib/api"

// =============================================================================
// Types
// =============================================================================

export interface ActivityEntry {
  id: string
  user_id: string | null
  user_name: string | null
  user_email: string | null
  action: string
  entity_type: string
  entity_id: string | null
  before_state: Record<string, unknown> | null
  after_state: Record<string, unknown> | null
  correlation_id: string | null
  created_at: string
}

export interface ActivityResponse {
  activity: ActivityEntry[]
  total: number
  limit: number
  offset: number
}

export interface ActivityFilters {
  days?: number
  limit?: number
  offset?: number
  entity_type?: string
  search?: string
}

// =============================================================================
// Query Keys
// =============================================================================

export const activityKeys = {
  all: ["activity"] as const,
  project: (projectId: string, filters?: ActivityFilters) =>
    [...activityKeys.all, projectId, filters] as const,
  itemHistory: (projectId: string, itemId: string) =>
    [...activityKeys.all, "item", projectId, itemId] as const,
}

// =============================================================================
// Build Query String
// =============================================================================

function buildQueryString(filters?: ActivityFilters): string {
  if (!filters) return ""

  const params = new URLSearchParams()
  if (filters.days) params.set("days", String(filters.days))
  if (filters.limit) params.set("limit", String(filters.limit))
  if (filters.offset) params.set("offset", String(filters.offset))
  if (filters.entity_type) params.set("entity_type", filters.entity_type)
  if (filters.search) params.set("search", filters.search)

  const queryString = params.toString()
  return queryString ? `?${queryString}` : ""
}

// =============================================================================
// Hooks
// =============================================================================

/**
 * Fetch project activity feed.
 */
export function useActivity(
  projectId: string | undefined,
  filters?: ActivityFilters
) {
  return useQuery({
    queryKey: activityKeys.project(projectId!, filters),
    queryFn: async () => {
      const query = buildQueryString(filters)
      const result = await apiGet<ActivityResponse>(
        `/projects/${projectId}/activity${query}`
      )
      if (result.error) {
        throw new Error(result.error.message)
      }
      return result.data!
    },
    enabled: !!projectId,
  })
}

/**
 * Fetch item change history.
 */
export function useItemHistory(
  projectId: string | undefined,
  itemId: string | undefined
) {
  return useQuery({
    queryKey: activityKeys.itemHistory(projectId!, itemId!),
    queryFn: async () => {
      const result = await apiGet<{ history: ActivityEntry[]; item_id: string }>(
        `/projects/${projectId}/items/${itemId}/history`
      )
      if (result.error) {
        throw new Error(result.error.message)
      }
      return result.data!
    },
    enabled: !!projectId && !!itemId,
  })
}

// =============================================================================
// Item React Query Hooks
// Server state management for RAID items
// =============================================================================

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import { apiGet, apiPost, apiPut, apiDelete } from "@/lib/api"
import type {
  Item,
  ItemCreate,
  ItemUpdate,
  ItemFilters,
  ItemListResponse,
} from "@/types"

// Query key factory for cache management
export const itemKeys = {
  all: ["items"] as const,
  lists: () => [...itemKeys.all, "list"] as const,
  list: (projectId: string, filters?: ItemFilters) =>
    [...itemKeys.lists(), projectId, filters] as const,
  details: () => [...itemKeys.all, "detail"] as const,
  detail: (projectId: string, itemId: string) =>
    [...itemKeys.details(), projectId, itemId] as const,
}

// Build query string from filters
function buildQueryString(filters?: ItemFilters): string {
  if (!filters) return ""

  const params = new URLSearchParams()
  if (filters.type) params.set("type", filters.type)
  if (filters.workstream_id) params.set("workstream_id", filters.workstream_id)
  if (filters.assigned_to) params.set("assigned_to", filters.assigned_to)
  if (filters.indicator) params.set("indicator", filters.indicator)
  if (filters.draft !== undefined) params.set("draft", String(filters.draft))
  if (filters.search) params.set("search", filters.search)
  if (filters.limit) params.set("limit", String(filters.limit))
  if (filters.offset) params.set("offset", String(filters.offset))

  const queryString = params.toString()
  return queryString ? `?${queryString}` : ""
}

// Fetch items for a project with optional filters
export function useItems(projectId: string | undefined, filters?: ItemFilters) {
  return useQuery({
    queryKey: itemKeys.list(projectId!, filters),
    queryFn: async () => {
      const query = buildQueryString(filters)
      const result = await apiGet<ItemListResponse>(
        `/projects/${projectId}/items${query}`
      )
      if (result.error) {
        throw new Error(result.error.message)
      }
      return result.data!
    },
    enabled: !!projectId,
  })
}

// Fetch a single item by ID
export function useItem(projectId: string | undefined, itemId: string | undefined) {
  return useQuery({
    queryKey: itemKeys.detail(projectId!, itemId!),
    queryFn: async () => {
      const result = await apiGet<Item>(
        `/projects/${projectId}/items/${itemId}`
      )
      if (result.error) {
        throw new Error(result.error.message)
      }
      return result.data!
    },
    enabled: !!projectId && !!itemId,
  })
}

// Create a new item
export function useCreateItem(projectId: string) {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (data: ItemCreate) => {
      const result = await apiPost<Item>(
        `/projects/${projectId}/items`,
        data
      )
      if (result.error) {
        throw new Error(result.error.message)
      }
      return result.data!
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: itemKeys.lists() })
    },
  })
}

// Update an existing item
export function useUpdateItem(projectId: string, itemId: string) {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (data: ItemUpdate) => {
      const result = await apiPut<Item>(
        `/projects/${projectId}/items/${itemId}`,
        data
      )
      if (result.error) {
        throw new Error(result.error.message)
      }
      return result.data!
    },
    onSuccess: (updatedItem) => {
      queryClient.setQueryData(
        itemKeys.detail(projectId, itemId),
        updatedItem
      )
      queryClient.invalidateQueries({ queryKey: itemKeys.lists() })
    },
  })
}

// Delete an item
export function useDeleteItem(projectId: string) {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (itemId: string) => {
      const result = await apiDelete(
        `/projects/${projectId}/items/${itemId}`
      )
      if (result.error) {
        throw new Error(result.error.message)
      }
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: itemKeys.lists() })
    },
  })
}

// Recalculate indicators for all items in a project
export function useUpdateIndicators(projectId: string) {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async () => {
      const result = await apiPost<{ updated_count: number }>(
        `/projects/${projectId}/update-indicators`
      )
      if (result.error) {
        throw new Error(result.error.message)
      }
      return result.data!
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: itemKeys.lists() })
    },
  })
}

// =============================================================================
// Workstream React Query Hooks
// Server state management for project workstreams
// =============================================================================

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import { apiGet, apiPost, apiPut, apiDelete } from "@/lib/api"
import type {
  Workstream,
  WorkstreamCreate,
  WorkstreamUpdate,
  WorkstreamReorder,
  WorkstreamListResponse,
} from "@/types"

// Query key factory for cache management
export const workstreamKeys = {
  all: ["workstreams"] as const,
  lists: () => [...workstreamKeys.all, "list"] as const,
  list: (projectId: string) => [...workstreamKeys.lists(), projectId] as const,
  details: () => [...workstreamKeys.all, "detail"] as const,
  detail: (projectId: string, workstreamId: string) =>
    [...workstreamKeys.details(), projectId, workstreamId] as const,
}

// Fetch workstreams for a project
export function useWorkstreams(projectId: string | undefined) {
  return useQuery({
    queryKey: workstreamKeys.list(projectId!),
    queryFn: async () => {
      const result = await apiGet<WorkstreamListResponse>(
        `/projects/${projectId}/workstreams`
      )
      if (result.error) {
        throw new Error(result.error.message)
      }
      return result.data!
    },
    enabled: !!projectId,
  })
}

// Create a new workstream
export function useCreateWorkstream(projectId: string) {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (data: WorkstreamCreate) => {
      const result = await apiPost<Workstream>(
        `/projects/${projectId}/workstreams`,
        data
      )
      if (result.error) {
        throw new Error(result.error.message)
      }
      return result.data!
    },
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: workstreamKeys.list(projectId),
      })
    },
  })
}

// Update a workstream
export function useUpdateWorkstream(projectId: string, workstreamId: string) {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (data: WorkstreamUpdate) => {
      const result = await apiPut<Workstream>(
        `/projects/${projectId}/workstreams/${workstreamId}`,
        data
      )
      if (result.error) {
        throw new Error(result.error.message)
      }
      return result.data!
    },
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: workstreamKeys.list(projectId),
      })
    },
  })
}

// Delete a workstream
export function useDeleteWorkstream(projectId: string) {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (workstreamId: string) => {
      const result = await apiDelete(
        `/projects/${projectId}/workstreams/${workstreamId}`
      )
      if (result.error) {
        throw new Error(result.error.message)
      }
    },
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: workstreamKeys.list(projectId),
      })
    },
  })
}

// Reorder workstreams
export function useReorderWorkstreams(projectId: string) {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (data: WorkstreamReorder) => {
      const result = await apiPost<{ success: boolean }>(
        `/projects/${projectId}/workstreams/reorder`,
        data
      )
      if (result.error) {
        throw new Error(result.error.message)
      }
      return result.data!
    },
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: workstreamKeys.list(projectId),
      })
    },
  })
}

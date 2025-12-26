// =============================================================================
// Project React Query Hooks
// Server state management for projects
// =============================================================================

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import { apiGet, apiPost, apiPut, apiDelete } from "@/lib/api"
import type {
  Project,
  ProjectCreate,
  ProjectUpdate,
  ProjectListResponse,
} from "@/types"

// Query key factory for cache management
export const projectKeys = {
  all: ["projects"] as const,
  lists: () => [...projectKeys.all, "list"] as const,
  list: () => projectKeys.lists(),
  details: () => [...projectKeys.all, "detail"] as const,
  detail: (id: string) => [...projectKeys.details(), id] as const,
}

// Fetch all projects for the current organization
export function useProjects() {
  return useQuery({
    queryKey: projectKeys.list(),
    queryFn: async () => {
      const result = await apiGet<ProjectListResponse>("/projects")
      if (result.error) {
        throw new Error(result.error.message)
      }
      return result.data!
    },
  })
}

// Fetch a single project by ID
export function useProject(projectId: string | undefined) {
  return useQuery({
    queryKey: projectKeys.detail(projectId!),
    queryFn: async () => {
      const result = await apiGet<Project>(`/projects/${projectId}`)
      if (result.error) {
        throw new Error(result.error.message)
      }
      return result.data!
    },
    enabled: !!projectId,
  })
}

// Create a new project
export function useCreateProject() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (data: ProjectCreate) => {
      const result = await apiPost<Project>("/projects", data)
      if (result.error) {
        throw new Error(result.error.message)
      }
      return result.data!
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: projectKeys.lists() })
    },
  })
}

// Update an existing project
export function useUpdateProject(projectId: string) {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (data: ProjectUpdate) => {
      const result = await apiPut<Project>(`/projects/${projectId}`, data)
      if (result.error) {
        throw new Error(result.error.message)
      }
      return result.data!
    },
    onSuccess: (updatedProject) => {
      queryClient.setQueryData(
        projectKeys.detail(projectId),
        updatedProject
      )
      queryClient.invalidateQueries({ queryKey: projectKeys.lists() })
    },
  })
}

// Delete a project
export function useDeleteProject() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (projectId: string) => {
      const result = await apiDelete(`/projects/${projectId}`)
      if (result.error) {
        throw new Error(result.error.message)
      }
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: projectKeys.lists() })
    },
  })
}

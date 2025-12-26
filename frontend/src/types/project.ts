// =============================================================================
// Project Types
// Matches backend src/api/schemas/projects.py
// =============================================================================

// Project response from API
export interface Project {
  id: string
  organization_id: string
  name: string
  client_name: string | null
  project_start: string | null  // ISO date string YYYY-MM-DD
  project_end: string | null    // ISO date string YYYY-MM-DD
  next_item_num: number
  indicators_updated: string | null  // ISO datetime string
  created_at: string | null
  updated_at: string | null
}

// Request body for creating a project
export interface ProjectCreate {
  name: string
  client_name?: string | null
  project_start?: string | null
  project_end?: string | null
  workstreams?: string[]
}

// Request body for updating a project
export interface ProjectUpdate {
  name?: string
  client_name?: string | null
  project_start?: string | null
  project_end?: string | null
}

// Response from listing projects
export interface ProjectListResponse {
  projects: Project[]
  total: number
}

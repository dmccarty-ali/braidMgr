// =============================================================================
// Workstream Types
// Matches backend src/api/schemas/workstreams.py
// =============================================================================

// Workstream response from API
export interface Workstream {
  id: string
  project_id: string
  name: string
  sort_order: number
}

// Request body for creating a workstream
export interface WorkstreamCreate {
  name: string
}

// Request body for updating a workstream
export interface WorkstreamUpdate {
  name?: string
}

// Request body for reordering workstreams
export interface WorkstreamReorder {
  workstream_ids: string[]
}

// Response from listing workstreams
export interface WorkstreamListResponse {
  workstreams: Workstream[]
}

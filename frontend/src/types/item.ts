// =============================================================================
// Item Types
// Matches backend src/api/schemas/items.py and src/domain/core.py
// =============================================================================

// Item type enum - the seven RAID+ item types
export type ItemType =
  | "Budget"
  | "Risk"
  | "Action Item"
  | "Issue"
  | "Decision"
  | "Deliverable"
  | "Plan Item"

// All item types as array for dropdowns
export const ITEM_TYPES: ItemType[] = [
  "Budget",
  "Risk",
  "Action Item",
  "Issue",
  "Decision",
  "Deliverable",
  "Plan Item",
]

// Indicator enum - calculated status indicators (ordered by severity)
export type Indicator =
  | "Beyond Deadline!!!"
  | "Late Finish!!"
  | "Late Start!!"
  | "Trending Late!"
  | "Finishing Soon!"
  | "Starting Soon!"
  | "In Progress"
  | "Not Started"
  | "Completed Recently"
  | "Completed"

// All indicators ordered by severity (most severe first)
export const INDICATORS: Indicator[] = [
  "Beyond Deadline!!!",
  "Late Finish!!",
  "Late Start!!",
  "Trending Late!",
  "Finishing Soon!",
  "Starting Soon!",
  "In Progress",
  "Not Started",
  "Completed Recently",
  "Completed",
]

// Item response from API
export interface Item {
  id: string
  project_id: string
  item_num: number
  type: ItemType
  title: string
  description: string | null
  workstream_id: string | null
  assigned_to: string | null
  start_date: string | null      // ISO date string YYYY-MM-DD
  finish_date: string | null     // ISO date string YYYY-MM-DD
  duration_days: number | null
  deadline: string | null        // ISO date string YYYY-MM-DD
  draft: boolean
  client_visible: boolean
  percent_complete: number
  indicator: Indicator | null
  priority: string | null
  rpt_out: string[] | null
  budget_amount: number | null   // Decimal as number
  created_at: string | null
  updated_at: string | null
}

// Request body for creating an item
export interface ItemCreate {
  type: ItemType
  title: string
  description?: string | null
  workstream_id?: string | null
  assigned_to?: string | null
  start_date?: string | null
  finish_date?: string | null
  duration_days?: number | null
  deadline?: string | null
  draft?: boolean
  client_visible?: boolean
  percent_complete?: number
  priority?: string | null
  rpt_out?: string[] | null
  budget_amount?: number | null
}

// Request body for updating an item
export interface ItemUpdate {
  title?: string
  description?: string | null
  workstream_id?: string | null
  assigned_to?: string | null
  start_date?: string | null
  finish_date?: string | null
  duration_days?: number | null
  deadline?: string | null
  draft?: boolean
  client_visible?: boolean
  percent_complete?: number
  priority?: string | null
  rpt_out?: string[] | null
  budget_amount?: number | null
}

// Query parameters for filtering items
export interface ItemFilters {
  type?: ItemType
  workstream_id?: string
  assigned_to?: string
  indicator?: Indicator
  draft?: boolean
  search?: string
  limit?: number
  offset?: number
}

// Response from listing items
export interface ItemListResponse {
  items: Item[]
  total: number
}

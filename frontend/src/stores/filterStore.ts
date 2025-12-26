// =============================================================================
// Filter Store
// Persists filter state for each view using React useState
// Using a simple React approach instead of external state management
// =============================================================================

import { useState, useCallback } from "react"
import type { ItemType, Indicator } from "@/types"

// Filter state for All Items view
export interface ItemFilterState {
  type: ItemType | null
  workstream_id: string | null
  search: string
  indicator: Indicator | null
}

// Default filter state
const defaultFilters: ItemFilterState = {
  type: null,
  workstream_id: null,
  search: "",
  indicator: null,
}

// Hook to manage filter state
export function useFilterState(initialState: Partial<ItemFilterState> = {}) {
  const [filters, setFilters] = useState<ItemFilterState>({
    ...defaultFilters,
    ...initialState,
  })

  const setFilter = useCallback(
    <K extends keyof ItemFilterState>(key: K, value: ItemFilterState[K]) => {
      setFilters((prev) => ({ ...prev, [key]: value }))
    },
    []
  )

  const clearFilters = useCallback(() => {
    setFilters(defaultFilters)
  }, [])

  const hasActiveFilters =
    filters.type !== null ||
    filters.workstream_id !== null ||
    filters.search !== "" ||
    filters.indicator !== null

  return {
    filters,
    setFilter,
    clearFilters,
    hasActiveFilters,
  }
}

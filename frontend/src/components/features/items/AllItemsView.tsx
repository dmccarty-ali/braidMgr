// =============================================================================
// AllItemsView Component
// Table view of all project items with filtering and edit dialog
// =============================================================================

import { useMemo, useState } from "react"
import { useParams } from "react-router-dom"
import { useItems } from "@/hooks/useItems"
import { useWorkstreams } from "@/hooks/useWorkstreams"
import { useFilterState } from "@/stores/filterStore"
import { ItemTable } from "./ItemTable"
import { ItemFilters } from "./ItemFilters"
import { EditItemDialog } from "./EditItemDialog"
import { Skeleton } from "@/components/ui/skeleton"
import { Button } from "@/components/ui/button"
import type { Item } from "@/types"

export function AllItemsView() {
  const { projectId } = useParams<{ projectId: string }>()
  const { data: itemsData, isLoading: itemsLoading } = useItems(projectId)
  const { data: workstreamsData, isLoading: workstreamsLoading } =
    useWorkstreams(projectId)

  const { filters, setFilter, clearFilters, hasActiveFilters } = useFilterState()

  // Dialog state
  const [dialogOpen, setDialogOpen] = useState(false)
  const [selectedItem, setSelectedItem] = useState<Item | null>(null)

  const items = itemsData?.items || []
  const workstreams = workstreamsData?.workstreams || []
  const isLoading = itemsLoading || workstreamsLoading

  // Apply client-side filters
  const filteredItems = useMemo(() => {
    return items.filter((item: Item) => {
      // Type filter
      if (filters.type && item.type !== filters.type) {
        return false
      }

      // Workstream filter
      if (filters.workstream_id && item.workstream_id !== filters.workstream_id) {
        return false
      }

      // Indicator filter
      if (filters.indicator && item.indicator !== filters.indicator) {
        return false
      }

      // Search filter (title and description)
      if (filters.search) {
        const searchLower = filters.search.toLowerCase()
        const titleMatch = item.title.toLowerCase().includes(searchLower)
        const descMatch = item.description?.toLowerCase().includes(searchLower)
        if (!titleMatch && !descMatch) {
          return false
        }
      }

      return true
    })
  }, [items, filters])

  // Handle row click to open edit dialog
  const handleRowClick = (item: Item) => {
    setSelectedItem(item)
    setDialogOpen(true)
  }

  // Handle create new item
  const handleCreateClick = () => {
    setSelectedItem(null)
    setDialogOpen(true)
  }

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div>
          <Skeleton className="h-8 w-32" />
          <Skeleton className="h-4 w-48 mt-2" />
        </div>
        <Skeleton className="h-10 w-full" />
        <Skeleton className="h-64 w-full" />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-bold">All Items</h1>
          <p className="text-muted-foreground">
            {filteredItems.length} of {items.length} items
            {hasActiveFilters && " (filtered)"}
          </p>
        </div>
        <Button onClick={handleCreateClick}>
          + New Item
        </Button>
      </div>

      {/* Filters */}
      <div data-tour="filter-sidebar">
        <ItemFilters
          filters={filters}
          workstreams={workstreams}
          onFilterChange={setFilter}
          onClearFilters={clearFilters}
          hasActiveFilters={hasActiveFilters}
        />
      </div>

      {/* Table */}
      <div className="border rounded-lg" data-tour="items-table">
        <ItemTable
          items={filteredItems}
          workstreams={workstreams}
          onRowClick={handleRowClick}
        />
      </div>

      {/* Edit/Create Dialog */}
      {projectId && (
        <EditItemDialog
          open={dialogOpen}
          onOpenChange={setDialogOpen}
          projectId={projectId}
          item={selectedItem}
          workstreams={workstreams}
        />
      )}
    </div>
  )
}

export default AllItemsView

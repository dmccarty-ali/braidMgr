// =============================================================================
// ActiveItemsView Component
// Items grouped by severity indicator
// =============================================================================

import { useMemo, useState } from "react"
import { useParams } from "react-router-dom"
import { useItems } from "@/hooks/useItems"
import { useWorkstreams } from "@/hooks/useWorkstreams"
import { SeverityGroup } from "./SeverityGroup"
import { EditItemDialog } from "./EditItemDialog"
import { Skeleton } from "@/components/ui/skeleton"
import { sortByIndicatorSeverity } from "@/lib/indicators"
import type { Item, Indicator } from "@/types"
import { INDICATORS } from "@/types"

export function ActiveItemsView() {
  const { projectId } = useParams<{ projectId: string }>()
  const { data: itemsData, isLoading: itemsLoading } = useItems(projectId)
  const { data: workstreamsData, isLoading: workstreamsLoading } =
    useWorkstreams(projectId)

  // Dialog state
  const [dialogOpen, setDialogOpen] = useState(false)
  const [selectedItem, setSelectedItem] = useState<Item | null>(null)

  const items = itemsData?.items || []
  const workstreams = workstreamsData?.workstreams || []
  const isLoading = itemsLoading || workstreamsLoading

  // Filter to only active (non-completed) items and sort by severity
  const activeItems = useMemo(() => {
    const filtered = items.filter(
      (item) => item.percent_complete < 100 && !item.draft
    )
    return sortByIndicatorSeverity(filtered)
  }, [items])

  // Group items by indicator
  const groupedItems = useMemo(() => {
    const groups = new Map<Indicator | null, Item[]>()

    // Initialize groups in severity order
    for (const indicator of INDICATORS) {
      groups.set(indicator, [])
    }
    groups.set(null, [])

    // Populate groups
    for (const item of activeItems) {
      const key = item.indicator
      const existing = groups.get(key) || []
      groups.set(key, [...existing, item])
    }

    // Filter out empty groups
    return Array.from(groups.entries()).filter(([, items]) => items.length > 0)
  }, [activeItems])

  // Handle item click
  const handleItemClick = (item: Item) => {
    setSelectedItem(item)
    setDialogOpen(true)
  }

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div>
          <Skeleton className="h-8 w-40" />
          <Skeleton className="h-4 w-32 mt-2" />
        </div>
        <Skeleton className="h-32 w-full" />
        <Skeleton className="h-32 w-full" />
        <Skeleton className="h-32 w-full" />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold">Active Items</h1>
        <p className="text-muted-foreground">
          {activeItems.length} active items grouped by status
        </p>
      </div>

      {/* Grouped items */}
      {groupedItems.length === 0 ? (
        <div className="text-center py-12 text-muted-foreground">
          No active items found
        </div>
      ) : (
        <div className="space-y-4" data-tour="severity-groups">
          {groupedItems.map(([indicator, groupItems]) => (
            <SeverityGroup
              key={indicator || "none"}
              indicator={indicator}
              items={groupItems}
              workstreams={workstreams}
              onItemClick={handleItemClick}
              // Auto-collapse low-severity groups
              defaultExpanded={
                indicator !== "Completed Recently" &&
                indicator !== "Not Started"
              }
            />
          ))}
        </div>
      )}

      {/* Edit Dialog */}
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

export default ActiveItemsView

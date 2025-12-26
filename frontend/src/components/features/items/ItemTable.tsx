// =============================================================================
// ItemTable Component
// Sortable table for displaying project items
// =============================================================================

import { useState, useMemo } from "react"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import { Badge } from "@/components/ui/badge"
import { getIndicatorVariant } from "@/lib/indicators"
import type { Item, Workstream } from "@/types"

interface ItemTableProps {
  items: Item[]
  workstreams: Workstream[]
  onRowClick?: (item: Item) => void
}

// Sort direction type
type SortDirection = "asc" | "desc" | null

// Column keys that can be sorted
type SortableColumn = "item_num" | "type" | "title" | "assigned_to" | "indicator" | "percent_complete"

export function ItemTable({ items, workstreams, onRowClick }: ItemTableProps) {
  const [sortColumn, setSortColumn] = useState<SortableColumn | null>(null)
  const [sortDirection, setSortDirection] = useState<SortDirection>(null)

  // Create workstream lookup map
  const workstreamMap = useMemo(() => {
    const map = new Map<string, string>()
    workstreams.forEach((ws) => map.set(ws.id, ws.name))
    return map
  }, [workstreams])

  // Handle column header click for sorting
  const handleSort = (column: SortableColumn) => {
    if (sortColumn === column) {
      // Cycle through: asc -> desc -> null
      if (sortDirection === "asc") {
        setSortDirection("desc")
      } else if (sortDirection === "desc") {
        setSortColumn(null)
        setSortDirection(null)
      }
    } else {
      setSortColumn(column)
      setSortDirection("asc")
    }
  }

  // Sort items based on current sort state
  const sortedItems = useMemo(() => {
    if (!sortColumn || !sortDirection) {
      return items
    }

    return [...items].sort((a, b) => {
      let aVal: string | number | null = null
      let bVal: string | number | null = null

      switch (sortColumn) {
        case "item_num":
          aVal = a.item_num
          bVal = b.item_num
          break
        case "type":
          aVal = a.type
          bVal = b.type
          break
        case "title":
          aVal = a.title.toLowerCase()
          bVal = b.title.toLowerCase()
          break
        case "assigned_to":
          aVal = a.assigned_to?.toLowerCase() || ""
          bVal = b.assigned_to?.toLowerCase() || ""
          break
        case "indicator":
          aVal = a.indicator || ""
          bVal = b.indicator || ""
          break
        case "percent_complete":
          aVal = a.percent_complete
          bVal = b.percent_complete
          break
      }

      if (aVal === null || bVal === null) return 0
      if (aVal < bVal) return sortDirection === "asc" ? -1 : 1
      if (aVal > bVal) return sortDirection === "asc" ? 1 : -1
      return 0
    })
  }, [items, sortColumn, sortDirection])

  // Render sort indicator
  const getSortIndicator = (column: SortableColumn) => {
    if (sortColumn !== column) return null
    return sortDirection === "asc" ? " ↑" : " ↓"
  }

  // Render sortable header
  const SortableHeader = ({
    column,
    children,
  }: {
    column: SortableColumn
    children: React.ReactNode
  }) => (
    <TableHead
      className="cursor-pointer hover:bg-muted/50 select-none"
      onClick={() => handleSort(column)}
    >
      {children}
      {getSortIndicator(column)}
    </TableHead>
  )

  if (items.length === 0) {
    return (
      <div className="text-center py-8 text-muted-foreground">
        No items found
      </div>
    )
  }

  return (
    <Table>
      <TableHeader>
        <TableRow>
          <SortableHeader column="item_num">#</SortableHeader>
          <SortableHeader column="type">Type</SortableHeader>
          <SortableHeader column="title">Title</SortableHeader>
          <TableHead>Workstream</TableHead>
          <SortableHeader column="assigned_to">Assigned To</SortableHeader>
          <SortableHeader column="indicator">Status</SortableHeader>
          <SortableHeader column="percent_complete">Progress</SortableHeader>
        </TableRow>
      </TableHeader>
      <TableBody>
        {sortedItems.map((item) => (
          <TableRow
            key={item.id}
            className={onRowClick ? "cursor-pointer" : ""}
            onClick={() => onRowClick?.(item)}
          >
            <TableCell className="font-medium">{item.item_num}</TableCell>
            <TableCell>
              <Badge variant="outline">{item.type}</Badge>
            </TableCell>
            <TableCell className="max-w-[300px] truncate">
              {item.title}
            </TableCell>
            <TableCell className="text-muted-foreground">
              {item.workstream_id
                ? workstreamMap.get(item.workstream_id) || "-"
                : "-"}
            </TableCell>
            <TableCell>{item.assigned_to || "-"}</TableCell>
            <TableCell>
              {item.indicator ? (
                <Badge variant={getIndicatorVariant(item.indicator)}>
                  {item.indicator}
                </Badge>
              ) : (
                "-"
              )}
            </TableCell>
            <TableCell>
              <div className="flex items-center gap-2">
                <div className="flex-1 h-2 bg-muted rounded-full overflow-hidden max-w-[80px]">
                  <div
                    className="h-full bg-primary transition-all"
                    style={{ width: `${item.percent_complete}%` }}
                  />
                </div>
                <span className="text-xs text-muted-foreground w-8">
                  {item.percent_complete}%
                </span>
              </div>
            </TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  )
}

export default ItemTable

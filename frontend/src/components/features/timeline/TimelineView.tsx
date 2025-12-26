// =============================================================================
// TimelineView Component
// Gantt-style timeline view with workstream swimlanes, zoom, and filters
// =============================================================================

import { useMemo, useState, useRef, useEffect } from "react"
import { useParams } from "react-router-dom"
import { useItems } from "@/hooks/useItems"
import { useWorkstreams } from "@/hooks/useWorkstreams"
import { useProject } from "@/hooks/useProjects"
import { EditItemDialog } from "../items/EditItemDialog"
import { Skeleton } from "@/components/ui/skeleton"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import type { Item, ItemType, Workstream } from "@/types"
import { ITEM_TYPES } from "@/types"

// =============================================================================
// Helper Functions
// =============================================================================

function parseDate(dateStr: string | null): Date | null {
  if (!dateStr) return null
  const date = new Date(dateStr)
  return isNaN(date.getTime()) ? null : date
}

function daysBetween(start: Date, end: Date): number {
  const diffTime = end.getTime() - start.getTime()
  return Math.ceil(diffTime / (1000 * 60 * 60 * 24))
}

function formatDate(date: Date): string {
  return date.toLocaleDateString("en-US", { month: "short", day: "numeric" })
}

// Item type colors for visual distinction
const typeColors: Record<ItemType, string> = {
  "Budget": "#8b5cf6",      // purple
  "Risk": "#ef4444",        // red
  "Action Item": "#3b82f6", // blue
  "Issue": "#f97316",       // orange
  "Decision": "#06b6d4",    // cyan
  "Deliverable": "#10b981", // green
  "Plan Item": "#6366f1",   // indigo
}

// =============================================================================
// TimelineBar Component - Individual item bar on the Gantt chart
// =============================================================================

interface TimelineBarProps {
  item: Item
  timelineStart: Date
  dayWidth: number
  onClick: () => void
}

function TimelineBar({ item, timelineStart, dayWidth, onClick }: TimelineBarProps) {
  const startDate = parseDate(item.start_date)
  const finishDate = parseDate(item.finish_date)

  if (!startDate || !finishDate) return null

  const offsetDays = daysBetween(timelineStart, startDate)
  const durationDays = Math.max(1, daysBetween(startDate, finishDate) + 1)

  const left = Math.max(0, offsetDays * dayWidth)
  const width = Math.max(40, durationDays * dayWidth)
  const isComplete = item.percent_complete >= 100

  // Progress indicator width
  const progressWidth = (item.percent_complete / 100) * width

  return (
    <div
      className="absolute h-7 rounded cursor-pointer hover:ring-2 ring-white/50 transition-all group"
      style={{
        left: `${left}px`,
        width: `${width}px`,
        backgroundColor: isComplete ? "#6b7280" : typeColors[item.type],
        opacity: isComplete ? 0.6 : 1,
      }}
      onClick={onClick}
      title={`#${item.item_num}: ${item.title}\n${item.start_date} → ${item.finish_date}\n${item.percent_complete}% complete`}
    >
      {/* Progress fill */}
      {!isComplete && item.percent_complete > 0 && (
        <div
          className="absolute top-0 left-0 h-full rounded-l bg-black/20"
          style={{ width: `${progressWidth}px` }}
        />
      )}

      {/* Label */}
      <div className="relative h-full flex items-center px-2 text-xs font-medium text-white overflow-hidden">
        <span className="truncate">
          #{item.item_num}: {item.title}
        </span>
      </div>

      {/* Tooltip on hover - shows more detail */}
      <div className="absolute bottom-full left-0 mb-1 px-2 py-1 bg-popover text-popover-foreground text-xs rounded shadow-lg opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none whitespace-nowrap z-20">
        <div className="font-medium">#{item.item_num}: {item.title}</div>
        <div className="text-muted-foreground">{item.type} • {item.percent_complete}%</div>
        <div className="text-muted-foreground">
          {formatDate(startDate)} → {formatDate(finishDate)}
        </div>
      </div>
    </div>
  )
}

// =============================================================================
// SwimLane Component - Groups items by workstream
// =============================================================================

interface SwimLaneProps {
  workstream: Workstream | null
  items: Item[]
  timelineStart: Date
  dayWidth: number
  timelineWidth: number
  onItemClick: (item: Item) => void
  isCollapsed: boolean
  onToggle: () => void
}

function SwimLane({
  workstream,
  items,
  timelineStart,
  dayWidth,
  timelineWidth,
  onItemClick,
  isCollapsed,
  onToggle,
}: SwimLaneProps) {
  const laneName = workstream?.name || "Unassigned"
  const rowHeight = 36 // Height per item row

  return (
    <div className="border-b border-border/50">
      {/* Lane header - sticky on the left */}
      <div className="flex">
        <button
          className="sticky left-0 z-10 w-48 shrink-0 flex items-center gap-2 px-3 py-2 bg-muted/50 border-r text-sm font-medium hover:bg-muted transition-colors"
          onClick={onToggle}
        >
          <span className="text-xs">{isCollapsed ? "▶" : "▼"}</span>
          <span className="truncate">{laneName}</span>
          <Badge variant="secondary" className="ml-auto text-xs">
            {items.length}
          </Badge>
        </button>

        {/* Items area */}
        {!isCollapsed && (
          <div
            className="relative bg-background/50"
            style={{
              width: `${timelineWidth}px`,
              height: `${Math.max(1, items.length) * rowHeight + 8}px`,
            }}
          >
            {items.map((item, index) => (
              <div
                key={item.id}
                className="absolute left-0 right-0"
                style={{ top: `${index * rowHeight + 4}px`, height: `${rowHeight - 4}px` }}
              >
                <TimelineBar
                  item={item}
                  timelineStart={timelineStart}
                  dayWidth={dayWidth}
                  onClick={() => onItemClick(item)}
                />
              </div>
            ))}
          </div>
        )}

        {/* Collapsed state - just show count */}
        {isCollapsed && (
          <div
            className="flex items-center px-4 text-sm text-muted-foreground"
            style={{ width: `${timelineWidth}px`, height: "40px" }}
          >
            {items.length} items hidden
          </div>
        )}
      </div>
    </div>
  )
}

// =============================================================================
// TimelineHeader Component - Date markers and today line
// =============================================================================

interface TimelineHeaderProps {
  timelineStart: Date
  timelineEnd: Date
  dayWidth: number
  timelineWidth: number
}

function TimelineHeader({ timelineStart, timelineEnd, dayWidth, timelineWidth }: TimelineHeaderProps) {
  // Generate week markers
  const weekMarkers = useMemo(() => {
    const markers: { date: Date; label: string; left: number }[] = []
    const current = new Date(timelineStart)

    // Start from next Monday
    const dayOfWeek = current.getDay()
    const daysToMonday = dayOfWeek === 0 ? 1 : 8 - dayOfWeek
    current.setDate(current.getDate() + daysToMonday)

    while (current <= timelineEnd) {
      const offset = daysBetween(timelineStart, current)
      markers.push({
        date: new Date(current),
        label: formatDate(current),
        left: offset * dayWidth,
      })
      current.setDate(current.getDate() + 7)
    }

    return markers
  }, [timelineStart, timelineEnd, dayWidth])

  // Month markers
  const monthMarkers = useMemo(() => {
    const markers: { date: Date; label: string; left: number }[] = []
    const current = new Date(timelineStart)
    current.setDate(1)
    current.setMonth(current.getMonth() + 1)

    while (current <= timelineEnd) {
      const offset = daysBetween(timelineStart, current)
      markers.push({
        date: new Date(current),
        label: current.toLocaleDateString("en-US", { month: "short", year: "2-digit" }),
        left: offset * dayWidth,
      })
      current.setMonth(current.getMonth() + 1)
    }

    return markers
  }, [timelineStart, timelineEnd, dayWidth])

  // Today marker
  const todayOffset = useMemo(() => {
    const today = new Date()
    if (today < timelineStart || today > timelineEnd) return null
    return daysBetween(timelineStart, today) * dayWidth
  }, [timelineStart, timelineEnd, dayWidth])

  return (
    <div className="flex border-b">
      {/* Left spacer for lane names */}
      <div className="sticky left-0 z-10 w-48 shrink-0 bg-muted border-r" />

      {/* Timeline header */}
      <div
        className="relative h-12 bg-muted/30"
        style={{ width: `${timelineWidth}px` }}
      >
        {/* Month markers */}
        {monthMarkers.map((marker, i) => (
          <div
            key={`month-${i}`}
            className="absolute top-0 h-full border-l border-border"
            style={{ left: `${marker.left}px` }}
          >
            <span className="absolute top-1 left-1 text-xs font-medium text-foreground bg-background/80 px-1 rounded">
              {marker.label}
            </span>
          </div>
        ))}

        {/* Week markers (lighter) */}
        {weekMarkers.map((marker, i) => (
          <div
            key={`week-${i}`}
            className="absolute top-0 h-full border-l border-dashed border-border/40"
            style={{ left: `${marker.left}px` }}
          >
            <span className="absolute bottom-1 left-1 text-[10px] text-muted-foreground">
              {marker.label}
            </span>
          </div>
        ))}

        {/* Today marker */}
        {todayOffset !== null && (
          <div
            className="absolute top-0 h-full w-0.5 bg-red-500 z-10"
            style={{ left: `${todayOffset}px` }}
          >
            <span className="absolute -top-0 left-1 text-[10px] font-medium text-red-500 bg-background px-1 rounded">
              Today
            </span>
          </div>
        )}
      </div>
    </div>
  )
}

// =============================================================================
// Main TimelineView Component
// =============================================================================

export function TimelineView() {
  const { projectId } = useParams<{ projectId: string }>()
  const { data: project } = useProject(projectId)
  const { data: itemsData, isLoading: itemsLoading } = useItems(projectId)
  const { data: workstreamsData, isLoading: workstreamsLoading } = useWorkstreams(projectId)

  // Dialog state
  const [dialogOpen, setDialogOpen] = useState(false)
  const [selectedItem, setSelectedItem] = useState<Item | null>(null)

  // Filter state
  const [typeFilter, setTypeFilter] = useState<string>("all")
  const [workstreamFilter, setWorkstreamFilter] = useState<string>("all")
  const [showCompleted, setShowCompleted] = useState(true)

  // Zoom state (day width in pixels)
  const [dayWidth, setDayWidth] = useState(20)

  // Collapsed lanes state
  const [collapsedLanes, setCollapsedLanes] = useState<Set<string>>(new Set())

  // Scroll container ref for "Today" button
  const scrollRef = useRef<HTMLDivElement>(null)

  const items = itemsData?.items || []
  const workstreams = workstreamsData?.workstreams || []
  const isLoading = itemsLoading || workstreamsLoading

  // Filter and prepare items with dates
  const filteredItems = useMemo(() => {
    return items.filter((item) => {
      // Must have dates for timeline
      if (!item.start_date || !item.finish_date) return false

      // Type filter
      if (typeFilter !== "all" && item.type !== typeFilter) return false

      // Workstream filter
      if (workstreamFilter !== "all") {
        if (workstreamFilter === "unassigned" && item.workstream_id) return false
        if (workstreamFilter !== "unassigned" && item.workstream_id !== workstreamFilter) return false
      }

      // Completed filter
      if (!showCompleted && item.percent_complete >= 100) return false

      return true
    })
  }, [items, typeFilter, workstreamFilter, showCompleted])

  // Group items by workstream for swimlanes
  const itemsByWorkstream = useMemo(() => {
    const groups = new Map<string | null, Item[]>()

    filteredItems.forEach((item) => {
      const key = item.workstream_id
      const existing = groups.get(key) || []
      groups.set(key, [...existing, item])
    })

    // Sort items within each group by start date
    groups.forEach((groupItems, key) => {
      groups.set(
        key,
        groupItems.sort((a, b) => {
          const dateA = parseDate(a.start_date)?.getTime() || 0
          const dateB = parseDate(b.start_date)?.getTime() || 0
          return dateA - dateB
        })
      )
    })

    return groups
  }, [filteredItems])

  // Calculate timeline range
  const { timelineStart, timelineEnd, totalDays } = useMemo(() => {
    if (filteredItems.length === 0) {
      const now = new Date()
      const end = new Date(now)
      end.setMonth(end.getMonth() + 3)
      return { timelineStart: now, timelineEnd: end, totalDays: 90 }
    }

    let minDate = new Date()
    let maxDate = new Date()

    filteredItems.forEach((item) => {
      const start = parseDate(item.start_date)
      const finish = parseDate(item.finish_date)
      if (start && start < minDate) minDate = new Date(start)
      if (finish && finish > maxDate) maxDate = new Date(finish)
    })

    // Add padding
    minDate.setDate(minDate.getDate() - 7)
    maxDate.setDate(maxDate.getDate() + 14)

    return {
      timelineStart: minDate,
      timelineEnd: maxDate,
      totalDays: daysBetween(minDate, maxDate),
    }
  }, [filteredItems])

  const timelineWidth = totalDays * dayWidth

  // Scroll to today on mount
  useEffect(() => {
    if (scrollRef.current && filteredItems.length > 0) {
      const today = new Date()
      const todayOffset = daysBetween(timelineStart, today) * dayWidth
      // Center today in the view
      scrollRef.current.scrollLeft = Math.max(0, todayOffset - 300)
    }
  }, []) // Only on mount

  const handleItemClick = (item: Item) => {
    setSelectedItem(item)
    setDialogOpen(true)
  }

  const toggleLane = (workstreamId: string | null) => {
    const key = workstreamId || "unassigned"
    setCollapsedLanes((prev) => {
      const next = new Set(prev)
      if (next.has(key)) {
        next.delete(key)
      } else {
        next.add(key)
      }
      return next
    })
  }

  const scrollToToday = () => {
    if (scrollRef.current) {
      const today = new Date()
      const todayOffset = daysBetween(timelineStart, today) * dayWidth
      scrollRef.current.scrollTo({
        left: Math.max(0, todayOffset - 300),
        behavior: "smooth",
      })
    }
  }

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div>
          <Skeleton className="h-8 w-32" />
          <Skeleton className="h-4 w-48 mt-2" />
        </div>
        <Skeleton className="h-64 w-full" />
      </div>
    )
  }

  // Order workstreams - put assigned ones first (by sort_order), unassigned last
  const orderedWorkstreamIds: (string | null)[] = [
    ...workstreams.sort((a, b) => a.sort_order - b.sort_order).map((w) => w.id),
  ]
  if (itemsByWorkstream.has(null)) {
    orderedWorkstreamIds.push(null)
  }

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-bold">Timeline</h1>
          <p className="text-muted-foreground">
            {filteredItems.length} items with dates
            {project?.project_start && ` • Project: ${project.project_start} to ${project.project_end}`}
          </p>
        </div>
      </div>

      {/* Controls bar */}
      <div className="flex flex-wrap items-center gap-3">
        {/* Type filter */}
        <Select value={typeFilter} onValueChange={setTypeFilter}>
          <SelectTrigger className="w-36">
            <SelectValue placeholder="All Types" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Types</SelectItem>
            {ITEM_TYPES.map((type) => (
              <SelectItem key={type} value={type}>
                <div className="flex items-center gap-2">
                  <div
                    className="w-3 h-3 rounded"
                    style={{ backgroundColor: typeColors[type] }}
                  />
                  {type}
                </div>
              </SelectItem>
            ))}
          </SelectContent>
        </Select>

        {/* Workstream filter */}
        <Select value={workstreamFilter} onValueChange={setWorkstreamFilter}>
          <SelectTrigger className="w-44">
            <SelectValue placeholder="All Workstreams" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Workstreams</SelectItem>
            <SelectItem value="unassigned">Unassigned</SelectItem>
            {workstreams.map((ws) => (
              <SelectItem key={ws.id} value={ws.id}>
                {ws.name}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>

        {/* Show completed toggle */}
        <label className="flex items-center gap-2 text-sm cursor-pointer">
          <input
            type="checkbox"
            checked={showCompleted}
            onChange={(e) => setShowCompleted(e.target.checked)}
            className="rounded"
          />
          Show completed
        </label>

        <div className="flex-1" />

        {/* Zoom controls */}
        <div className="flex items-center gap-2">
          <span className="text-sm text-muted-foreground">Zoom:</span>
          <Button
            variant="outline"
            size="sm"
            onClick={() => setDayWidth((w) => Math.max(8, w - 4))}
            disabled={dayWidth <= 8}
          >
            −
          </Button>
          <span className="text-sm w-8 text-center">{dayWidth}px</span>
          <Button
            variant="outline"
            size="sm"
            onClick={() => setDayWidth((w) => Math.min(40, w + 4))}
            disabled={dayWidth >= 40}
          >
            +
          </Button>
        </div>

        {/* Today button */}
        <Button variant="outline" size="sm" onClick={scrollToToday}>
          Today
        </Button>
      </div>

      {/* Legend */}
      <div className="flex flex-wrap gap-3 text-sm">
        {ITEM_TYPES.map((type) => (
          <div key={type} className="flex items-center gap-1.5">
            <div
              className="w-3 h-3 rounded"
              style={{ backgroundColor: typeColors[type] }}
            />
            <span className="text-muted-foreground">{type}</span>
          </div>
        ))}
        <div className="flex items-center gap-1.5">
          <div className="w-3 h-3 rounded bg-gray-500 opacity-60" />
          <span className="text-muted-foreground">Completed</span>
        </div>
        <div className="flex items-center gap-1.5">
          <div className="w-0.5 h-4 bg-red-500" />
          <span className="text-muted-foreground">Today</span>
        </div>
      </div>

      {/* Timeline container */}
      {filteredItems.length === 0 ? (
        <div className="text-center py-12 text-muted-foreground border rounded-lg">
          No items with dates to display on the timeline.
          {items.length > filteredItems.length && (
            <div className="mt-2 text-sm">
              Try adjusting your filters to see more items.
            </div>
          )}
        </div>
      ) : (
        <div
          ref={scrollRef}
          className="border rounded-lg overflow-auto"
          style={{ maxHeight: "calc(100vh - 320px)" }}
          data-tour="timeline-container"
        >
          {/* Header with dates */}
          <TimelineHeader
            timelineStart={timelineStart}
            timelineEnd={timelineEnd}
            dayWidth={dayWidth}
            timelineWidth={timelineWidth}
          />

          {/* Swimlanes */}
          {orderedWorkstreamIds.map((wsId) => {
            const wsItems = itemsByWorkstream.get(wsId) || []
            if (wsItems.length === 0) return null

            const ws = wsId ? workstreams.find((w) => w.id === wsId) : null
            const isCollapsed = collapsedLanes.has(wsId || "unassigned")

            return (
              <SwimLane
                key={wsId || "unassigned"}
                workstream={ws || null}
                items={wsItems}
                timelineStart={timelineStart}
                dayWidth={dayWidth}
                timelineWidth={timelineWidth}
                onItemClick={handleItemClick}
                isCollapsed={isCollapsed}
                onToggle={() => toggleLane(wsId)}
              />
            )
          })}
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

export default TimelineView

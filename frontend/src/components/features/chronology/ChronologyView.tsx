// =============================================================================
// ChronologyView Component
// Activity feed showing project changes with collapsible months and search
// =============================================================================

import { useMemo, useState, useRef } from "react"
import { useParams } from "react-router-dom"
import { useActivity, type ActivityEntry } from "@/hooks/useActivity"
import { Skeleton } from "@/components/ui/skeleton"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"

// =============================================================================
// Helper Functions
// =============================================================================

function getMonthKey(dateStr: string): string {
  const date = new Date(dateStr)
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, "0")}`
}

function formatMonthLabel(monthKey: string): string {
  const [year, month] = monthKey.split("-")
  const date = new Date(parseInt(year!), parseInt(month!) - 1, 1)
  return date.toLocaleDateString("en-US", { month: "long", year: "numeric" })
}

function getCurrentMonthKey(): string {
  const now = new Date()
  return `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, "0")}`
}

function formatTime(dateStr: string): string {
  const date = new Date(dateStr)
  return date.toLocaleTimeString("en-US", {
    hour: "numeric",
    minute: "2-digit",
    hour12: true,
  })
}

function formatDate(dateStr: string): string {
  const date = new Date(dateStr)
  return date.toLocaleDateString("en-US", {
    weekday: "short",
    month: "short",
    day: "numeric",
  })
}

function getActionIcon(action: string): string {
  switch (action.toLowerCase()) {
    case "create":
    case "created":
      return "+"
    case "update":
    case "updated":
      return "~"
    case "delete":
    case "deleted":
      return "-"
    case "status_change":
      return "!"
    default:
      return "o"
  }
}

function getActionColor(action: string): string {
  switch (action.toLowerCase()) {
    case "create":
    case "created":
      return "bg-green-500"
    case "update":
    case "updated":
      return "bg-blue-500"
    case "delete":
    case "deleted":
      return "bg-red-500"
    case "status_change":
      return "bg-yellow-500"
    default:
      return "bg-gray-500"
  }
}

function describeChange(entry: ActivityEntry): string {
  const entityLabel = entry.entity_type === "item" ? "Item" : entry.entity_type
  const entityName = entry.after_state?.title || entry.before_state?.title || `#${entry.entity_id?.slice(0, 8)}`

  switch (entry.action.toLowerCase()) {
    case "create":
    case "created":
      return `Created ${entityLabel}: ${entityName}`
    case "delete":
    case "deleted":
      return `Deleted ${entityLabel}: ${entityName}`
    case "update":
    case "updated":
      // Try to identify what changed
      if (entry.before_state && entry.after_state) {
        const changes: string[] = []
        const before = entry.before_state as Record<string, unknown>
        const after = entry.after_state as Record<string, unknown>

        if (before.indicator !== after.indicator) {
          changes.push(`status: ${before.indicator} → ${after.indicator}`)
        }
        if (before.percent_complete !== after.percent_complete) {
          changes.push(`progress: ${before.percent_complete}% → ${after.percent_complete}%`)
        }
        if (before.title !== after.title) {
          changes.push("title")
        }
        if (before.assigned_to !== after.assigned_to) {
          changes.push("assignee")
        }

        if (changes.length > 0) {
          return `Updated ${entityLabel} "${entityName}": ${changes.join(", ")}`
        }
      }
      return `Updated ${entityLabel}: ${entityName}`
    default:
      return `${entry.action} on ${entityLabel}: ${entityName}`
  }
}

// =============================================================================
// ActivityCard Component
// =============================================================================

interface ActivityCardProps {
  entry: ActivityEntry
}

function ActivityCard({ entry }: ActivityCardProps) {
  const [expanded, setExpanded] = useState(false)

  return (
    <div className="flex gap-3 py-3 px-4 hover:bg-muted/30 transition-colors rounded-lg">
      {/* Icon */}
      <div
        className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center text-white text-sm font-bold ${getActionColor(entry.action)}`}
      >
        {getActionIcon(entry.action)}
      </div>

      {/* Content */}
      <div className="flex-1 min-w-0">
        <div className="flex items-start justify-between gap-2">
          <div className="flex-1">
            <p className="text-sm font-medium">{describeChange(entry)}</p>
            <p className="text-xs text-muted-foreground mt-0.5">
              {entry.user_name || entry.user_email || "System"} • {formatTime(entry.created_at)}
            </p>
          </div>

          <div className="flex items-center gap-2">
            <Badge variant="secondary" className="text-xs capitalize">
              {entry.entity_type}
            </Badge>

            {(entry.before_state || entry.after_state) && (
              <Button
                variant="ghost"
                size="sm"
                className="h-6 px-2 text-xs"
                onClick={() => setExpanded(!expanded)}
              >
                {expanded ? "Hide" : "Details"}
              </Button>
            )}
          </div>
        </div>

        {/* Expanded details */}
        {expanded && (entry.before_state || entry.after_state) && (
          <div className="mt-2 p-2 bg-muted rounded text-xs font-mono overflow-x-auto">
            {entry.before_state && entry.after_state ? (
              <div className="space-y-1">
                <div className="text-muted-foreground">Changes:</div>
                {Object.keys(entry.after_state).map((key) => {
                  const before = (entry.before_state as Record<string, unknown>)?.[key]
                  const after = (entry.after_state as Record<string, unknown>)?.[key]
                  if (JSON.stringify(before) !== JSON.stringify(after)) {
                    return (
                      <div key={key}>
                        <span className="text-muted-foreground">{key}:</span>{" "}
                        <span className="text-red-500 line-through">{JSON.stringify(before)}</span>{" "}
                        <span className="text-green-500">{JSON.stringify(after)}</span>
                      </div>
                    )
                  }
                  return null
                })}
              </div>
            ) : (
              <pre className="whitespace-pre-wrap">
                {JSON.stringify(entry.after_state || entry.before_state, null, 2)}
              </pre>
            )}
          </div>
        )}
      </div>
    </div>
  )
}

// =============================================================================
// MonthGroup Component
// =============================================================================

interface MonthGroupProps {
  monthKey: string
  entries: ActivityEntry[]
  defaultExpanded?: boolean
}

function MonthGroup({ monthKey, entries, defaultExpanded = true }: MonthGroupProps) {
  const [isExpanded, setIsExpanded] = useState(defaultExpanded)
  const isCurrent = monthKey === getCurrentMonthKey()

  // Group entries by date within the month
  const entriesByDate = useMemo(() => {
    const groups = new Map<string, ActivityEntry[]>()
    entries.forEach((entry) => {
      const dateKey = entry.created_at.split("T")[0]!
      const existing = groups.get(dateKey) || []
      groups.set(dateKey, [...existing, entry])
    })
    return Array.from(groups.entries()).sort((a, b) => b[0].localeCompare(a[0]))
  }, [entries])

  return (
    <div
      id={`month-${monthKey}`}
      className={`border rounded-lg overflow-hidden ${isCurrent ? "border-primary" : ""}`}
    >
      {/* Header */}
      <button
        className={`w-full flex items-center justify-between p-4 hover:bg-muted/50 transition-colors text-left ${
          isCurrent ? "bg-primary/5" : "bg-muted/30"
        }`}
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <div className="flex items-center gap-3">
          <span className="text-lg">{isExpanded ? "▼" : "▶"}</span>
          <span className="font-medium">{formatMonthLabel(monthKey)}</span>
          {isCurrent && (
            <Badge variant="default" className="text-xs">
              Current
            </Badge>
          )}
        </div>
        <span className="text-sm font-medium bg-background px-2 py-0.5 rounded">
          {entries.length} {entries.length === 1 ? "event" : "events"}
        </span>
      </button>

      {/* Entries grouped by date */}
      {isExpanded && (
        <div className="divide-y">
          {entriesByDate.map(([dateKey, dateEntries]) => (
            <div key={dateKey}>
              <div className="px-4 py-2 bg-muted/20 text-xs font-medium text-muted-foreground sticky top-0">
                {formatDate(dateKey)}
              </div>
              <div className="divide-y divide-border/50">
                {dateEntries.map((entry) => (
                  <ActivityCard key={entry.id} entry={entry} />
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

// =============================================================================
// Main Component
// =============================================================================

export function ChronologyView() {
  const { projectId } = useParams<{ projectId: string }>()
  const [days, setDays] = useState(30)
  const [search, setSearch] = useState("")
  const [entityFilter, setEntityFilter] = useState<string>("all")
  const containerRef = useRef<HTMLDivElement>(null)

  const { data, isLoading, error } = useActivity(projectId, {
    days,
    limit: 500,
    entity_type: entityFilter !== "all" ? entityFilter : undefined,
    search: search || undefined,
  })

  const activity = data?.activity || []

  // Group by month
  const groupedByMonth = useMemo(() => {
    const groups = new Map<string, ActivityEntry[]>()

    activity.forEach((entry) => {
      const monthKey = getMonthKey(entry.created_at)
      const existing = groups.get(monthKey) || []
      groups.set(monthKey, [...existing, entry])
    })

    // Sort by month (most recent first)
    return Array.from(groups.entries()).sort((a, b) => b[0].localeCompare(a[0]))
  }, [activity])

  // Get list of months for jump-to
  const availableMonths = useMemo(() => {
    return groupedByMonth.map(([monthKey]) => ({
      key: monthKey,
      label: formatMonthLabel(monthKey),
    }))
  }, [groupedByMonth])

  const handleJumpToMonth = (monthKey: string) => {
    const element = document.getElementById(`month-${monthKey}`)
    if (element) {
      element.scrollIntoView({ behavior: "smooth", block: "start" })
    }
  }

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div>
          <Skeleton className="h-8 w-40" />
          <Skeleton className="h-4 w-32 mt-2" />
        </div>
        <Skeleton className="h-10 w-full" />
        <Skeleton className="h-32 w-full" />
        <Skeleton className="h-32 w-full" />
      </div>
    )
  }

  if (error) {
    return (
      <div className="text-center py-12 text-destructive">
        Failed to load activity: {error.message}
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-bold">Chronology</h1>
          <p className="text-muted-foreground">
            {data?.total || 0} events in the last {days} days
          </p>
        </div>
      </div>

      {/* Filters bar */}
      <div className="flex flex-wrap items-center gap-3">
        {/* Search */}
        <div className="flex-1 min-w-[200px] max-w-md">
          <Input
            placeholder="Search activity..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="h-9"
          />
        </div>

        {/* Entity type filter */}
        <Select value={entityFilter} onValueChange={setEntityFilter}>
          <SelectTrigger className="w-32">
            <SelectValue placeholder="All types" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All types</SelectItem>
            <SelectItem value="item">Items</SelectItem>
            <SelectItem value="workstream">Workstreams</SelectItem>
            <SelectItem value="project">Project</SelectItem>
          </SelectContent>
        </Select>

        {/* Days filter */}
        <Select value={String(days)} onValueChange={(v) => setDays(parseInt(v))}>
          <SelectTrigger className="w-32">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="7">Last 7 days</SelectItem>
            <SelectItem value="30">Last 30 days</SelectItem>
            <SelectItem value="90">Last 90 days</SelectItem>
            <SelectItem value="365">Last year</SelectItem>
          </SelectContent>
        </Select>

        {/* Jump to month */}
        {availableMonths.length > 1 && (
          <Select onValueChange={handleJumpToMonth}>
            <SelectTrigger className="w-40">
              <SelectValue placeholder="Jump to..." />
            </SelectTrigger>
            <SelectContent>
              {availableMonths.map(({ key, label }) => (
                <SelectItem key={key} value={key}>
                  {label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        )}
      </div>

      {/* Activity feed */}
      <div ref={containerRef} className="space-y-4">
        {groupedByMonth.length === 0 ? (
          <div className="text-center py-12 text-muted-foreground border rounded-lg">
            No activity found.
            {search && " Try adjusting your search."}
          </div>
        ) : (
          groupedByMonth.map(([monthKey, monthEntries], index) => (
            <MonthGroup
              key={monthKey}
              monthKey={monthKey}
              entries={monthEntries}
              // Expand current month and first month by default
              defaultExpanded={monthKey === getCurrentMonthKey() || index === 0}
            />
          ))
        )}
      </div>
    </div>
  )
}

export default ChronologyView

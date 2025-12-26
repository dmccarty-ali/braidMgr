// =============================================================================
// SeverityGroup Component
// Collapsible group of items by indicator/severity
// =============================================================================

import { useState } from "react"
import { Badge } from "@/components/ui/badge"
import { getIndicatorVariant, getIndicatorConfig } from "@/lib/indicators"
import { ItemCard } from "./ItemCard"
import type { Item, Indicator, Workstream } from "@/types"

interface SeverityGroupProps {
  indicator: Indicator | null
  items: Item[]
  workstreams: Workstream[]
  onItemClick: (item: Item) => void
  defaultExpanded?: boolean
}

export function SeverityGroup({
  indicator,
  items,
  workstreams,
  onItemClick,
  defaultExpanded = true,
}: SeverityGroupProps) {
  const [isExpanded, setIsExpanded] = useState(defaultExpanded)

  const config = getIndicatorConfig(indicator)
  const displayName = indicator || "No Status"

  return (
    <div className="border rounded-lg overflow-hidden" data-testid="severity-group">
      {/* Header */}
      <button
        className="w-full flex items-center justify-between p-4 bg-muted/30 hover:bg-muted/50 transition-colors text-left"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <div className="flex items-center gap-3">
          <span className="text-lg">{isExpanded ? "▼" : "▶"}</span>
          <Badge variant={getIndicatorVariant(indicator)} className="text-sm">
            {displayName}
          </Badge>
          <span className="text-sm text-muted-foreground">
            {config.description}
          </span>
        </div>
        <span className="text-sm font-medium bg-background px-2 py-0.5 rounded">
          {items.length} {items.length === 1 ? "item" : "items"}
        </span>
      </button>

      {/* Items */}
      {isExpanded && (
        <div className="p-4 grid gap-3 md:grid-cols-2 lg:grid-cols-3">
          {items.map((item) => (
            <ItemCard
              key={item.id}
              item={item}
              workstreams={workstreams}
              onClick={() => onItemClick(item)}
            />
          ))}
        </div>
      )}
    </div>
  )
}

export default SeverityGroup

// =============================================================================
// ItemCard Component
// Compact card for displaying an item in grouped views
// =============================================================================

import { Badge } from "@/components/ui/badge"
import { Card, CardContent } from "@/components/ui/card"
import { getIndicatorVariant } from "@/lib/indicators"
import type { Item, Workstream } from "@/types"

interface ItemCardProps {
  item: Item
  workstreams: Workstream[]
  onClick?: () => void
}

export function ItemCard({ item, workstreams, onClick }: ItemCardProps) {
  // Get workstream name
  const workstreamName = workstreams.find(
    (ws) => ws.id === item.workstream_id
  )?.name

  return (
    <Card
      className="cursor-pointer hover:border-primary transition-colors"
      onClick={onClick}
    >
      <CardContent className="p-4">
        {/* Header row */}
        <div className="flex items-start justify-between gap-2 mb-2">
          <div className="flex items-center gap-2 flex-wrap">
            <span className="font-mono text-sm text-muted-foreground">
              #{item.item_num}
            </span>
            <Badge variant="outline" className="text-xs">
              {item.type}
            </Badge>
            {item.priority && (
              <Badge
                variant={
                  item.priority === "High" || item.priority === "Critical"
                    ? "destructive"
                    : "secondary"
                }
                className="text-xs"
              >
                {item.priority}
              </Badge>
            )}
          </div>
          {item.indicator && (
            <Badge variant={getIndicatorVariant(item.indicator)} className="shrink-0">
              {item.indicator}
            </Badge>
          )}
        </div>

        {/* Title */}
        <h3 className="font-medium text-sm line-clamp-2 mb-2">{item.title}</h3>

        {/* Meta row */}
        <div className="flex items-center justify-between text-xs text-muted-foreground">
          <div className="flex items-center gap-2">
            {item.assigned_to && <span>{item.assigned_to}</span>}
            {workstreamName && (
              <>
                {item.assigned_to && <span>•</span>}
                <span>{workstreamName}</span>
              </>
            )}
          </div>
          <div className="flex items-center gap-2">
            <div className="w-16 h-1.5 bg-muted rounded-full overflow-hidden">
              <div
                className="h-full bg-primary"
                style={{ width: `${item.percent_complete}%` }}
              />
            </div>
            <span>{item.percent_complete}%</span>
          </div>
        </div>

        {/* Dates row */}
        {(item.start_date || item.finish_date || item.deadline) && (
          <div className="flex items-center gap-3 text-xs text-muted-foreground mt-2 pt-2 border-t">
            {item.start_date && <span>Start: {item.start_date}</span>}
            {item.finish_date && <span>Finish: {item.finish_date}</span>}
            {item.deadline && (
              <span className="text-destructive">Due: {item.deadline}</span>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  )
}

export default ItemCard

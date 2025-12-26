// =============================================================================
// ItemFilters Component
// Filter controls for the All Items view
// =============================================================================

import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import type { ItemFilterState } from "@/stores/filterStore"
import type { Workstream } from "@/types"
import { ITEM_TYPES, INDICATORS } from "@/types"

interface ItemFiltersProps {
  filters: ItemFilterState
  workstreams: Workstream[]
  onFilterChange: <K extends keyof ItemFilterState>(
    key: K,
    value: ItemFilterState[K]
  ) => void
  onClearFilters: () => void
  hasActiveFilters: boolean
}

export function ItemFilters({
  filters,
  workstreams,
  onFilterChange,
  onClearFilters,
  hasActiveFilters,
}: ItemFiltersProps) {
  return (
    <div className="flex flex-wrap gap-3 items-center">
      {/* Search input */}
      <div className="flex-1 min-w-[200px] max-w-[300px]">
        <Input
          placeholder="Search items..."
          value={filters.search}
          onChange={(e) => onFilterChange("search", e.target.value)}
          data-testid="search-input"
        />
      </div>

      {/* Type filter */}
      <Select
        value={filters.type || "all"}
        onValueChange={(value) =>
          onFilterChange("type", value === "all" ? null : (value as typeof filters.type))
        }
      >
        <SelectTrigger className="w-[140px]" data-testid="type-filter">
          <SelectValue placeholder="All Types" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="all">All Types</SelectItem>
          {ITEM_TYPES.map((type) => (
            <SelectItem key={type} value={type}>
              {type}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>

      {/* Workstream filter */}
      <Select
        value={filters.workstream_id || "all"}
        onValueChange={(value) =>
          onFilterChange("workstream_id", value === "all" ? null : value)
        }
      >
        <SelectTrigger className="w-[160px]">
          <SelectValue placeholder="All Workstreams" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="all">All Workstreams</SelectItem>
          {workstreams.map((ws) => (
            <SelectItem key={ws.id} value={ws.id}>
              {ws.name}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>

      {/* Indicator filter */}
      <Select
        value={filters.indicator || "all"}
        onValueChange={(value) =>
          onFilterChange("indicator", value === "all" ? null : (value as typeof filters.indicator))
        }
      >
        <SelectTrigger className="w-[160px]" data-testid="indicator-filter">
          <SelectValue placeholder="All Statuses" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="all">All Statuses</SelectItem>
          {INDICATORS.map((indicator) => (
            <SelectItem key={indicator} value={indicator}>
              {indicator}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>

      {/* Clear filters button */}
      {hasActiveFilters && (
        <Button variant="outline" size="sm" onClick={onClearFilters}>
          Clear Filters
        </Button>
      )}
    </div>
  )
}

export default ItemFilters

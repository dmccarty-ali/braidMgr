// =============================================================================
// DashboardView Component
// Project dashboard with summary cards and quick stats
// =============================================================================

import { useParams } from "react-router-dom";
import { useItems } from "@/hooks/useItems";
import { useWorkstreams } from "@/hooks/useWorkstreams";
import { useProject } from "@/hooks/useProjects";
import { SummaryCard } from "./SummaryCard";
import { Badge } from "@/components/ui/badge";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { getIndicatorVariant } from "@/lib/indicators";
import type { Item, ItemType, Indicator } from "@/types";

export function DashboardView() {
  const { projectId } = useParams<{ projectId: string }>();
  const { data: project, isLoading: projectLoading } = useProject(projectId);
  const { data: itemsData, isLoading: itemsLoading } = useItems(projectId);
  const { data: workstreamsData, isLoading: workstreamsLoading } = useWorkstreams(projectId);

  const items = itemsData?.items || [];
  const workstreams = workstreamsData?.workstreams || [];
  const isLoading = projectLoading || itemsLoading || workstreamsLoading;

  // Calculate item type counts
  const typeCounts = items.reduce((acc, item) => {
    acc[item.type] = (acc[item.type] || 0) + 1;
    return acc;
  }, {} as Record<ItemType, number>);

  // Calculate indicator counts (for active items)
  const indicatorCounts = items.reduce((acc, item) => {
    if (item.indicator) {
      acc[item.indicator] = (acc[item.indicator] || 0) + 1;
    }
    return acc;
  }, {} as Record<Indicator, number>);

  // Filter attention items (severe indicators)
  const attentionItems = items.filter(
    (item) =>
      item.indicator &&
      ["Beyond Deadline!!!", "Late Finish!!", "Late Start!!", "Trending Late!"].includes(
        item.indicator
      )
  );

  return (
    <div className="space-y-6">
      {/* Page header */}
      <div>
        <h1 className="text-2xl font-bold">Dashboard</h1>
        {project && (
          <p className="text-muted-foreground">
            {project.client_name && `${project.client_name} - `}
            {project.name}
          </p>
        )}
      </div>

      {/* Summary cards row - BRAID order: Budget, Risks, Actions, Issues, Decisions + extras */}
      <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-4" data-tour="summary-cards">
        <SummaryCard
          title="Budget"
          count={typeCounts["Budget"] || 0}
          icon="💰"
          isLoading={isLoading}
        />
        <SummaryCard
          title="Risks"
          count={typeCounts["Risk"] || 0}
          icon="⚠️"
          isLoading={isLoading}
        />
        <SummaryCard
          title="Actions"
          count={typeCounts["Action Item"] || 0}
          icon="✓"
          isLoading={isLoading}
        />
        <SummaryCard
          title="Issues"
          count={typeCounts["Issue"] || 0}
          icon="🔴"
          isLoading={isLoading}
        />
        <SummaryCard
          title="Decisions"
          count={typeCounts["Decision"] || 0}
          icon="📝"
          isLoading={isLoading}
        />
        <SummaryCard
          title="Deliverables"
          count={typeCounts["Deliverable"] || 0}
          icon="📦"
          isLoading={isLoading}
        />
        <SummaryCard
          title="Plan Items"
          count={typeCounts["Plan Item"] || 0}
          icon="📅"
          isLoading={isLoading}
        />
      </div>

      {/* Two column layout */}
      <div className="grid md:grid-cols-2 gap-6">
        {/* Attention needed */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Attention Needed</CardTitle>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <div className="text-muted-foreground">Loading...</div>
            ) : attentionItems.length === 0 ? (
              <div className="text-muted-foreground">
                No items need attention
              </div>
            ) : (
              <div className="space-y-3">
                {attentionItems.slice(0, 5).map((item) => (
                  <AttentionItemRow key={item.id} item={item} />
                ))}
                {attentionItems.length > 5 && (
                  <p className="text-sm text-muted-foreground">
                    +{attentionItems.length - 5} more items
                  </p>
                )}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Status breakdown */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Status Overview</CardTitle>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <div className="text-muted-foreground">Loading...</div>
            ) : (
              <div className="space-y-2">
                {Object.entries(indicatorCounts)
                  .sort((a, b) => b[1] - a[1])
                  .map(([indicator, count]) => (
                    <div
                      key={indicator}
                      className="flex items-center gap-3"
                    >
                      <Badge
                      variant={getIndicatorVariant(indicator as Indicator)}
                      data-tour="indicator-badge"
                    >
                        {indicator}
                      </Badge>
                      <span className="text-sm text-muted-foreground">{count}</span>
                    </div>
                  ))}
                {Object.keys(indicatorCounts).length === 0 && (
                  <p className="text-muted-foreground">No status data</p>
                )}
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Workstreams summary */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Workstreams</CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="text-muted-foreground">Loading...</div>
          ) : workstreams.length === 0 ? (
            <div className="text-muted-foreground">No workstreams defined</div>
          ) : (
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {workstreams.map((ws) => {
                const wsItemCount = items.filter(
                  (item) => item.workstream_id === ws.id
                ).length;
                return (
                  <div
                    key={ws.id}
                    className="p-3 rounded-md bg-muted/50 border"
                  >
                    <div className="font-medium">{ws.name}</div>
                    <div className="text-sm text-muted-foreground">
                      {wsItemCount} items
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

// Attention item row sub-component
function AttentionItemRow({ item }: { item: Item }) {
  return (
    <div className="flex items-start gap-3 p-2 rounded-md bg-muted/50">
      <Badge variant={getIndicatorVariant(item.indicator)} className="shrink-0">
        {item.indicator}
      </Badge>
      <div className="min-w-0 flex-1">
        <div className="font-medium text-sm truncate">
          #{item.item_num}: {item.title}
        </div>
        <div className="text-xs text-muted-foreground">
          {item.type} {item.assigned_to && `- ${item.assigned_to}`}
        </div>
      </div>
    </div>
  );
}

export default DashboardView;

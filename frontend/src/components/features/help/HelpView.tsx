// =============================================================================
// HelpView Component
// Help documentation and quick reference
// =============================================================================

import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"

export function HelpView() {
  return (
    <div className="space-y-6 max-w-4xl">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold">Help</h1>
        <p className="text-muted-foreground">
          Documentation and quick reference for braidMgr
        </p>
      </div>

      {/* Item Types */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Item Types</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="grid gap-3">
            <TypeDescription
              type="Risk"
              description="Potential problems that could impact the project. Track likelihood, impact, and mitigation strategies."
            />
            <TypeDescription
              type="Action Item"
              description="Tasks that need to be completed. Assign to team members and track progress."
            />
            <TypeDescription
              type="Issue"
              description="Problems that have occurred and need resolution. Track status and resolution."
            />
            <TypeDescription
              type="Decision"
              description="Choices that have been made or need to be made. Document the decision and rationale."
            />
            <TypeDescription
              type="Deliverable"
              description="Outputs or artifacts that need to be produced. Track completion and deadlines."
            />
            <TypeDescription
              type="Plan Item"
              description="Milestones and key dates in the project plan. Use for timeline tracking."
            />
            <TypeDescription
              type="Budget"
              description="Financial items including costs, budgets, and expenditures."
            />
          </div>
        </CardContent>
      </Card>

      {/* Status Indicators */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Status Indicators</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground mb-4">
            Status indicators are automatically calculated based on dates and progress.
          </p>
          <div className="grid gap-2">
            <IndicatorDescription
              indicator="Beyond Deadline!!!"
              variant="destructive"
              description="Past deadline and not complete"
            />
            <IndicatorDescription
              indicator="Late Finish!!"
              variant="destructive"
              description="Finish date has passed but not complete"
            />
            <IndicatorDescription
              indicator="Late Start!!"
              variant="destructive"
              description="Start date has passed but not started"
            />
            <IndicatorDescription
              indicator="Trending Late!"
              variant="warning"
              description="Progress is behind schedule"
            />
            <IndicatorDescription
              indicator="Finishing Soon!"
              variant="warning"
              description="Finish date is approaching"
            />
            <IndicatorDescription
              indicator="Starting Soon!"
              variant="info"
              description="Start date is approaching"
            />
            <IndicatorDescription
              indicator="In Progress"
              variant="default"
              description="Work is actively ongoing"
            />
            <IndicatorDescription
              indicator="Not Started"
              variant="muted"
              description="Not yet begun"
            />
            <IndicatorDescription
              indicator="Completed Recently"
              variant="success"
              description="Finished within the last 7 days"
            />
            <IndicatorDescription
              indicator="Completed"
              variant="muted"
              description="Work is done"
            />
          </div>
        </CardContent>
      </Card>

      {/* Views */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Views</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <ViewDescription
            name="Dashboard"
            description="Overview of your project with summary counts and items needing attention."
          />
          <ViewDescription
            name="All Items"
            description="Complete list of all items with filtering, sorting, and search capabilities."
          />
          <ViewDescription
            name="Active Items"
            description="Items grouped by status severity. Focus on what needs attention first."
          />
          <ViewDescription
            name="Timeline"
            description="Gantt-style view showing items with dates on a timeline."
          />
          <ViewDescription
            name="Chronology"
            description="Items organized by month for chronological planning and review."
          />
        </CardContent>
      </Card>

      {/* Tips */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Tips</CardTitle>
        </CardHeader>
        <CardContent>
          <ul className="space-y-2 text-sm">
            <li className="flex gap-2">
              <span className="text-primary">•</span>
              <span>Click on any item to open the edit dialog</span>
            </li>
            <li className="flex gap-2">
              <span className="text-primary">•</span>
              <span>Use the search box in All Items to quickly find specific items</span>
            </li>
            <li className="flex gap-2">
              <span className="text-primary">•</span>
              <span>Set both start and finish dates to see items in the Timeline view</span>
            </li>
            <li className="flex gap-2">
              <span className="text-primary">•</span>
              <span>Mark items as Draft to hide them from most views</span>
            </li>
            <li className="flex gap-2">
              <span className="text-primary">•</span>
              <span>Indicators update automatically when you change dates or progress</span>
            </li>
          </ul>
        </CardContent>
      </Card>
    </div>
  )
}

// Sub-components
function TypeDescription({ type, description }: { type: string; description: string }) {
  return (
    <div className="flex gap-3">
      <Badge variant="outline" className="shrink-0">
        {type}
      </Badge>
      <span className="text-sm text-muted-foreground">{description}</span>
    </div>
  )
}

function IndicatorDescription({
  indicator,
  variant,
  description,
}: {
  indicator: string
  variant: "destructive" | "warning" | "success" | "info" | "muted" | "default"
  description: string
}) {
  return (
    <div className="flex gap-3 items-center">
      <Badge variant={variant} className="shrink-0 min-w-[140px] justify-center">
        {indicator}
      </Badge>
      <span className="text-sm text-muted-foreground">{description}</span>
    </div>
  )
}

function ViewDescription({ name, description }: { name: string; description: string }) {
  return (
    <div>
      <span className="font-medium">{name}</span>
      <span className="text-muted-foreground"> - {description}</span>
    </div>
  )
}

export default HelpView

/**
 * Tour Steps Configuration
 *
 * Defines the steps for the braidMgr demo tour.
 * Each step highlights key features and workflows.
 *
 * Target audience: Business partners / stakeholders
 */

// =============================================================================
// TYPES
// =============================================================================

export interface TourStep {
  /** Unique step identifier */
  id: string;
  /** CSS selector for element to highlight (null for center modal) */
  target: string | null;
  /** Step title */
  title: string;
  /** Step description (supports markdown-like formatting) */
  content: string;
  /** Position of tooltip relative to target */
  placement: "top" | "bottom" | "left" | "right" | "center";
  /** Route to navigate to before showing step (optional) */
  route?: string;
  /** Whether to wait for target element before showing */
  waitForTarget?: boolean;
  /** Spotlight padding around target in pixels */
  spotlightPadding?: number;
  /** Duration to show this step in milliseconds (default: 6000) */
  duration?: number;
  /** Key talking point for this step */
  talkingPoint?: string;
}

// =============================================================================
// TOUR STEPS - braidMgr Demo Walkthrough
// =============================================================================

export const DEMO_TOUR_STEPS: TourStep[] = [
  // -------------------------------------------------------------------------
  // Step 1: Welcome (Center Modal)
  // -------------------------------------------------------------------------
  {
    id: "welcome",
    target: null,
    title: "Welcome to braidMgr",
    content: `
**Your Project Management Command Center**

braidMgr helps you manage complex projects with:

- **Risks, Actions, Issues, and Decisions** tracking
- **Visual status indicators** for at-a-glance health
- **Multiple views** to see data the way you need it

Let's take a tour of the key features.
    `.trim(),
    placement: "center",
    duration: 8000,
    talkingPoint: "One platform for complete project visibility",
  },

  // -------------------------------------------------------------------------
  // Step 2: Project Selection
  // -------------------------------------------------------------------------
  {
    id: "project-selection",
    target: "[data-tour='project-list']",
    title: "Project Selection",
    content: `
Start by selecting a project from your portfolio.

Each project card shows:
- Project name and client
- Date range
- Quick status summary

Click any project to dive into the details.
    `.trim(),
    placement: "bottom",
    route: "/projects",
    waitForTarget: true,
    spotlightPadding: 16,
    duration: 7000,
    talkingPoint: "Quick access to all your projects",
  },

  // -------------------------------------------------------------------------
  // Step 3: Dashboard Overview
  // -------------------------------------------------------------------------
  {
    id: "dashboard-overview",
    target: "[data-tour='summary-cards']",
    title: "Dashboard Summary Cards",
    content: `
Your command center at a glance.

**Seven item types tracked:**
- Risks, Actions, Issues, Decisions
- Deliverables, Plan Items, Budget

Each card shows the count and can be clicked to filter.
    `.trim(),
    placement: "bottom",
    route: "/projects/1/dashboard",
    waitForTarget: true,
    spotlightPadding: 16,
    duration: 8000,
    talkingPoint: "See everything important in one place",
  },

  // -------------------------------------------------------------------------
  // Step 4: Navigation Sidebar
  // -------------------------------------------------------------------------
  {
    id: "sidebar-navigation",
    target: "[data-tour='sidebar-nav']",
    title: "Multiple Views",
    content: `
**Six ways to view your data:**

- **Dashboard** - Summary overview
- **All Items** - Complete item table
- **Active Items** - Grouped by severity
- **Timeline** - Gantt-style visualization
- **Chronology** - Monthly organization
- **Help** - Reference guide

Each view serves a different purpose.
    `.trim(),
    placement: "right",
    waitForTarget: true,
    spotlightPadding: 8,
    duration: 8000,
    talkingPoint: "The right view for every situation",
  },

  // -------------------------------------------------------------------------
  // Step 5: All Items View
  // -------------------------------------------------------------------------
  {
    id: "all-items-view",
    target: "[data-tour='items-table']",
    title: "All Items Table",
    content: `
A complete list of every item in the project.

**Features:**
- Sortable columns
- Click any row to edit
- Visual status indicators
- Quick reference item numbers

This is your master list.
    `.trim(),
    placement: "top",
    route: "/projects/1/items",
    waitForTarget: true,
    spotlightPadding: 8,
    duration: 7000,
    talkingPoint: "Complete visibility into every item",
  },

  // -------------------------------------------------------------------------
  // Step 6: Filtering
  // -------------------------------------------------------------------------
  {
    id: "filtering",
    target: "[data-tour='filter-sidebar']",
    title: "Powerful Filtering",
    content: `
Find exactly what you need.

**Filter by:**
- Item type (Risk, Action, etc.)
- Workstream
- Status indicator
- Search text

Filters apply instantly to narrow your view.
    `.trim(),
    placement: "left",
    waitForTarget: true,
    spotlightPadding: 8,
    duration: 7000,
    talkingPoint: "Find any item in seconds",
  },

  // -------------------------------------------------------------------------
  // Step 7: Status Indicators
  // -------------------------------------------------------------------------
  {
    id: "status-indicators",
    target: "[data-tour='indicator-badge']",
    title: "Status Indicators",
    content: `
**Color-coded status at a glance:**

- **Red** - Critical: Beyond deadline, late
- **Amber** - Warning: Trending late, finishing soon
- **Blue** - Info: In progress, starting soon
- **Green** - Good: Completed recently
- **Gray** - Neutral: Completed, not started

Indicators auto-calculate based on dates.
    `.trim(),
    placement: "left",
    waitForTarget: true,
    spotlightPadding: 4,
    duration: 8000,
    talkingPoint: "Visual alerts prevent surprises",
  },

  // -------------------------------------------------------------------------
  // Step 8: Active Items View
  // -------------------------------------------------------------------------
  {
    id: "active-items-view",
    target: "[data-tour='severity-groups']",
    title: "Active Items by Severity",
    content: `
Items grouped by urgency.

**Priority order:**
1. Beyond Deadline - needs immediate attention
2. Late items - address soon
3. Trending issues - proactive management
4. In Progress - current work

Critical items always appear first.
    `.trim(),
    placement: "top",
    route: "/projects/1/active",
    waitForTarget: true,
    spotlightPadding: 8,
    duration: 8000,
    talkingPoint: "Focus on what matters most",
  },

  // -------------------------------------------------------------------------
  // Step 9: Timeline View
  // -------------------------------------------------------------------------
  {
    id: "timeline-view",
    target: "[data-tour='timeline-container']",
    title: "Timeline Visualization",
    content: `
See your project schedule visually.

**Gantt-style display showing:**
- Item duration bars
- Start and finish dates
- Overlapping activities
- Critical path visibility

Perfect for planning and status meetings.
    `.trim(),
    placement: "top",
    route: "/projects/1/timeline",
    waitForTarget: true,
    spotlightPadding: 8,
    duration: 8000,
    talkingPoint: "Visualize the entire project timeline",
  },

  // -------------------------------------------------------------------------
  // Step 10: Command Palette
  // -------------------------------------------------------------------------
  {
    id: "command-palette",
    target: null,
    title: "Quick Navigation",
    content: `
**Press Cmd+K (or Ctrl+K) anytime**

The command palette provides:
- Quick navigation to any view
- Search across items
- Fast access to common actions

Power users love this feature.
    `.trim(),
    placement: "center",
    duration: 6000,
    talkingPoint: "Navigate anywhere in seconds",
  },

  // -------------------------------------------------------------------------
  // Step 11: Tour Complete
  // -------------------------------------------------------------------------
  {
    id: "tour-complete",
    target: null,
    title: "Tour Complete!",
    content: `
**You've seen the key features:**

- Dashboard summary cards
- Multiple data views
- Powerful filtering
- Visual status indicators
- Timeline visualization
- Quick command palette

**braidMgr keeps your projects on track.**

Thanks for taking the tour!
    `.trim(),
    placement: "center",
    duration: 10000,
    talkingPoint: "Ready to manage projects with confidence",
  },
];

// =============================================================================
// HELPER FUNCTIONS
// =============================================================================

/**
 * Get a step by ID
 */
export function getTourStep(stepId: string): TourStep | undefined {
  return DEMO_TOUR_STEPS.find((step) => step.id === stepId);
}

/**
 * Get the index of a step by ID
 */
export function getTourStepIndex(stepId: string): number {
  return DEMO_TOUR_STEPS.findIndex((step) => step.id === stepId);
}

/**
 * Get total number of steps
 */
export function getTourStepCount(): number {
  return DEMO_TOUR_STEPS.length;
}

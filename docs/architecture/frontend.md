# Frontend Architecture

*Parent: [ARCHITECTURE.md](../ARCHITECTURE.md)*
*Last updated: 2025-12-26*

React + Vite frontend architecture with TypeScript.

**Key Concepts**:
- React Query for server state
- React Hook Form + Zod for forms
- shadcn/ui components with Tailwind styling
- Feature-based component organization
- React Router for navigation

---

## Current Implementation

### Views (Sequence 4)

| View | Route | Description |
|------|-------|-------------|
| Dashboard | `/projects/:id/dashboard` | Summary cards, attention items, workstream overview |
| All Items | `/projects/:id/items` | Sortable table with filters |
| Active Items | `/projects/:id/active` | Items grouped by severity indicator |
| Timeline | `/projects/:id/timeline` | Gantt chart with workstream swimlanes, zoom, filters |
| Chronology | `/projects/:id/chronology` | Activity feed with collapsible months, search, jump-to-date |
| Help | `/projects/:id/help` | Documentation and quick reference |

### Chat Interface

The chatbot is available on all project pages via:
- **Floating button** (bottom-right) opens a slide-out drawer
- **Cmd+K** opens a command palette with search and chat modes

See [ai-integration.md](ai-integration.md) for backend details.

### Tour/Demo System

An interactive guided tour for demonstrating the application:

**Trigger**: Add `?demo=true` to any URL to start the tour automatically.

**Features**:
- Auto-advancing narrated steps (6 seconds default)
- Spotlight overlay highlights target elements
- Route navigation between pages
- Keyboard controls: Space (pause), arrows (prev/next), Escape (exit)
- Progress bar and step counter

**Components** (in `components/tour/`):

| Component | Purpose |
|-----------|---------|
| `TourProvider.tsx` | React Context for tour state |
| `useTour.ts` | Hook with auto-advance timer, keyboard handling |
| `TourOverlay.tsx` | Spotlight backdrop + tooltip UI |
| `TourNavigation.tsx` | Prev/Next/Pause controls |
| `tourSteps.ts` | Step definitions with targets, content, routes |

**Tour Steps**:
1. Welcome (center modal)
2. Project Selection
3. Dashboard Overview
4. BRAID Summary Cards (Budget, Risks, Actions, Issues, Decisions)
5. Navigation Sidebar
6. All Items Table
7. Filtering Sidebar
8. Active Items (severity grouping)
9. Timeline View
10. Completion

**Usage in App.tsx**:

```tsx
// Wrap app with TourProvider in main.tsx
<TourProvider>
  <App />
</TourProvider>

// Render overlay and detect demo mode in App.tsx
<DemoModeDetector />
<TourOverlay />
```

### Component Structure

```
frontend/src/
├── App.tsx                    # Main app with routing
├── main.tsx                   # Entry point with providers
├── types/
│   ├── project.ts             # Project types
│   ├── item.ts                # Item, ItemType, Indicator types
│   └── workstream.ts          # Workstream types
├── hooks/
│   ├── useProjects.ts         # Project queries/mutations
│   ├── useItems.ts            # Item queries/mutations
│   ├── useWorkstreams.ts      # Workstream queries
│   ├── useActivity.ts         # Activity feed queries
│   └── useChat.ts             # Chat state and WebSocket
├── stores/
│   └── filterStore.ts         # Filter state hook
├── lib/
│   ├── api.ts                 # API client with auth
│   ├── auth.tsx               # Auth context
│   ├── indicators.ts          # Indicator colors/utilities
│   └── utils.ts               # cn() for Tailwind
├── components/
│   ├── ui/                    # shadcn/ui primitives
│   │   ├── button.tsx
│   │   ├── card.tsx
│   │   ├── badge.tsx
│   │   ├── skeleton.tsx
│   │   ├── table.tsx
│   │   ├── input.tsx
│   │   ├── select.tsx
│   │   ├── dialog.tsx
│   │   ├── label.tsx
│   │   ├── textarea.tsx
│   │   └── slider.tsx
│   ├── layout/
│   │   ├── AppLayout.tsx      # Main layout wrapper
│   │   ├── Sidebar.tsx        # Navigation sidebar
│   │   └── Header.tsx         # Top header bar
│   ├── auth/
│   │   ├── LoginForm.tsx
│   │   ├── RegisterForm.tsx
│   │   └── ForgotPasswordForm.tsx
│   └── features/
│       ├── dashboard/
│       │   ├── DashboardView.tsx
│       │   └── SummaryCard.tsx
│       ├── items/
│       │   ├── AllItemsView.tsx
│       │   ├── ActiveItemsView.tsx
│       │   ├── ItemTable.tsx
│       │   ├── ItemFilters.tsx
│       │   ├── ItemCard.tsx
│       │   ├── SeverityGroup.tsx
│       │   └── EditItemDialog.tsx
│       ├── timeline/
│       │   └── TimelineView.tsx
│       ├── chronology/
│       │   └── ChronologyView.tsx
│       ├── chat/
│       │   ├── ChatContext.tsx    # Shared chat state provider
│       │   ├── ChatDrawer.tsx     # Floating button + drawer
│       │   ├── CommandPalette.tsx # Cmd+K interface
│       │   ├── ChatMessage.tsx    # Message bubble component
│       │   └── ChatInput.tsx      # Input with send button
│       └── help/
│           └── HelpView.tsx
├── components/tour/               # Demo tour system
│   ├── TourProvider.tsx           # React Context for tour state
│   ├── useTour.ts                 # Auto-advance timer, keyboard controls
│   ├── TourOverlay.tsx            # Spotlight + tooltip overlay
│   ├── TourNavigation.tsx         # Navigation controls
│   ├── tourSteps.ts               # Step definitions
│   └── index.ts                   # Exports
```

---

## State Management

| Type | Tool | Purpose |
|------|------|---------|
| Server state | React Query | API data, caching, sync |
| Filter state | useState hook | Per-view filter persistence |
| Form state | React Hook Form | Form validation |

### React Query Configuration

```typescript
// main.tsx
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 minutes
      retry: 1,
      refetchOnWindowFocus: true,
    },
  },
});
```

---

## Data Fetching Hooks

```typescript
// hooks/useItems.ts
export function useItems(projectId: string | undefined, filters?: ItemFilters) {
  return useQuery({
    queryKey: ['projects', projectId, 'items', filters],
    queryFn: async () => {
      const result = await apiGet<ItemListResponse>(`/projects/${projectId}/items`);
      if (result.error) throw new Error(result.error.message);
      return result.data!;
    },
    enabled: !!projectId,
  });
}

export function useCreateItem(projectId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (data: ItemCreate) => {
      const result = await apiPost<Item>(`/projects/${projectId}/items`, data);
      if (result.error) throw new Error(result.error.message);
      return result.data!;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['items'] });
    },
  });
}
```

---

## Indicator System

Status indicators are calculated server-side and displayed with severity-based colors:

```typescript
// lib/indicators.ts
export const indicatorConfig: Record<Indicator, IndicatorConfig> = {
  "Beyond Deadline!!!": { variant: "destructive", severity: 10 },
  "Late Finish!!": { variant: "destructive", severity: 9 },
  "Late Start!!": { variant: "destructive", severity: 8 },
  "Trending Late!": { variant: "warning", severity: 7 },
  "Finishing Soon!": { variant: "warning", severity: 6 },
  "Starting Soon!": { variant: "info", severity: 5 },
  "In Progress": { variant: "default", severity: 4 },
  "Not Started": { variant: "muted", severity: 3 },
  "Completed Recently": { variant: "success", severity: 2 },
  "Completed": { variant: "muted", severity: 1 },
};
```

---

## Routing

```typescript
// App.tsx routes
<Routes>
  {/* Public routes */}
  <Route element={<PublicOnlyRoute />}>
    <Route path="/login" element={<AuthContainer />} />
    <Route path="/register" element={<AuthContainer />} />
  </Route>

  {/* Protected routes */}
  <Route element={<ProtectedRoute />}>
    <Route path="/" element={<Navigate to="/projects" />} />
    <Route path="/projects" element={<ProjectListPage />} />

    <Route path="/projects/:projectId" element={<ProjectLayout />}>
      <Route index element={<Navigate to="dashboard" />} />
      <Route path="dashboard" element={<DashboardView />} />
      <Route path="items" element={<AllItemsView />} />
      <Route path="active" element={<ActiveItemsView />} />
      <Route path="timeline" element={<TimelineView />} />
      <Route path="chronology" element={<ChronologyView />} />
      <Route path="help" element={<HelpView />} />
    </Route>
  </Route>
</Routes>
```

---

## API Client

```typescript
// lib/api.ts
const API_BASE_URL = "/api/v1";

export async function apiFetch<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<ApiResponse<T>> {
  // Adds Authorization header if token exists
  // Handles 401 by attempting token refresh
  // Converts errors to ApiError format
}

export const apiGet = <T>(endpoint: string) => apiFetch<T>(endpoint, { method: "GET" });
export const apiPost = <T>(endpoint: string, body?: unknown) =>
  apiFetch<T>(endpoint, { method: "POST", body: JSON.stringify(body) });
export const apiPut = <T>(endpoint: string, body?: unknown) =>
  apiFetch<T>(endpoint, { method: "PUT", body: JSON.stringify(body) });
export const apiDelete = <T>(endpoint: string) =>
  apiFetch<T>(endpoint, { method: "DELETE" });
```

---

## Form Validation

Edit dialogs use React Hook Form with Zod schemas:

```typescript
// EditItemDialog.tsx
const itemSchema = z.object({
  type: z.enum(["Budget", "Risk", "Action Item", "Issue", "Decision", "Deliverable", "Plan Item"]),
  title: z.string().min(1, "Title is required").max(500),
  description: z.string().optional(),
  workstream_id: z.string().nullable(),
  percent_complete: z.number().min(0).max(100),
  // ... other fields
});

const { register, handleSubmit, formState: { errors } } = useForm<ItemFormData>({
  resolver: zodResolver(itemSchema),
});
```

---

## Testing

### Unit Tests

Unit tests use Vitest + React Testing Library:

```bash
npm run test          # Watch mode
npm run test -- --run # Single run
```

Current unit test coverage:
- Auth context (5 tests)
- LoginForm (7 tests)
- RegisterForm (8 tests)
- ForgotPasswordForm (7 tests)

### E2E Tests

E2E tests use Playwright with Gherkin/BDD syntax via playwright-bdd:

```bash
npm run test:e2e      # Run all e2e tests
```

**Test files**:
- `e2e/features/*.feature` - Gherkin feature files
- `e2e/steps/*.ts` - Step definitions

**Configuration**: `playwright.config.ts`
- Uses dedicated port 5174 (not 5173) to avoid conflicts
- WebServer auto-starts frontend before tests
- Tests run in Chromium by default

**Test data requirements**:
- Backend must be running on port 8000
- Test user: `e2e-test@example.com` / `E2eTestPass123`
- Test organization and project must exist in database
- See SQL setup in `backend/scripts/` or create via API

**Authentication note**: The frontend stores access tokens in memory (not localStorage) for security. E2E tests use client-side navigation after login to preserve auth state, avoiding full page reloads that would clear the in-memory token.

Current e2e test coverage:
- Login scenarios (4 tests)
- Dashboard navigation (7 tests)

---

## Dependencies

| Package | Purpose |
|---------|---------|
| @tanstack/react-query | Server state management |
| react-hook-form | Form state |
| @hookform/resolvers | Zod integration |
| zod | Schema validation |
| react-router-dom | Routing |
| @radix-ui/* | UI primitives |
| class-variance-authority | Component variants |
| clsx + tailwind-merge | Class utilities |

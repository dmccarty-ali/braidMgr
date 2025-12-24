# braidMgr Process Flows

*Last updated: 2024-12-24*

This document defines state machines and process flows for braidMgr entities.

---

## 1. Item Lifecycle

### 1.1 State Machine

```mermaid
stateDiagram-v2
    [*] --> Draft: Create (draft=true)
    [*] --> NotStarted: Create (draft=false)

    Draft --> NotStarted: Publish

    NotStarted --> StartingSoon: Start date approaching
    NotStarted --> LateStart: Start date passed

    StartingSoon --> InProgress: Work begins
    LateStart --> InProgress: Work begins

    InProgress --> TrendingLate: Behind schedule
    InProgress --> FinishingSoon: Finish date approaching
    InProgress --> CompletedRecently: 100% complete

    TrendingLate --> InProgress: Back on track
    TrendingLate --> LateFinish: Finish date passed
    TrendingLate --> CompletedRecently: 100% complete

    FinishingSoon --> CompletedRecently: 100% complete
    FinishingSoon --> LateFinish: Finish date passed

    LateFinish --> CompletedRecently: 100% complete

    NotStarted --> BeyondDeadline: Deadline passed
    InProgress --> BeyondDeadline: Deadline passed
    TrendingLate --> BeyondDeadline: Deadline passed
    LateStart --> BeyondDeadline: Deadline passed
    LateFinish --> BeyondDeadline: Deadline passed

    BeyondDeadline --> CompletedRecently: 100% complete

    CompletedRecently --> Completed: 2 weeks elapsed

    Completed --> [*]
```

### 1.2 State Definitions

| State | Indicator | Severity | Trigger |
|-------|-----------|----------|---------|
| Draft | (none) | - | draft=true |
| Not Started | Not Started | upcoming | 0%, has dates |
| Starting Soon | Starting Soon! | upcoming | Start within 2 weeks |
| Late Start | Late Start!! | critical | Start date passed, 0% |
| In Progress | In Progress | active | 1-99% complete |
| Trending Late | Trending Late! | warning | Remaining work > remaining time |
| Finishing Soon | Finishing Soon! | active | Finish within 2 weeks |
| Late Finish | Late Finish!! | critical | Finish passed, < 100% |
| Beyond Deadline | Beyond Deadline!!! | critical | Deadline passed |
| Completed Recently | Completed Recently | completed | 100%, within 2 weeks |
| Completed | Completed | done | 100%, > 2 weeks ago |

### 1.3 Indicator Calculation Rules

```python
def calculate_indicator(item: Item, today: date) -> str:
    """Calculate indicator based on precedence."""

    # Draft items get no indicator
    if item.draft:
        return None

    # Precedence order (highest to lowest):

    # 1. Completed Recently
    if item.percent_complete == 100:
        if item.finish and item.finish >= today - timedelta(days=14):
            return "Completed Recently"
        return "Completed"

    # 2. Beyond Deadline
    if item.deadline and item.deadline < today:
        return "Beyond Deadline!!!"

    # 3. Late Finish
    if item.finish and item.finish < today:
        return "Late Finish!!"

    # 4. Late Start
    if item.start and item.start < today and item.percent_complete == 0:
        return "Late Start!!"

    # 5. Trending Late
    if item.start and item.finish and item.duration:
        remaining_days = (item.finish - today).days
        remaining_work = (1 - item.percent_complete / 100) * item.duration
        if remaining_work > remaining_days:
            return "Trending Late!"

    # 6. Finishing Soon
    if item.finish and item.finish <= today + timedelta(days=14):
        return "Finishing Soon!"

    # 7. Starting Soon
    if item.percent_complete == 0 and item.start:
        if today <= item.start <= today + timedelta(days=14):
            return "Starting Soon!"

    # 8. In Progress
    if 0 < item.percent_complete < 100:
        return "In Progress"

    # 9. Not Started (has dates but 0%)
    if item.start or item.finish:
        return "Not Started"

    return None
```

---

## 2. Authentication Flow

### 2.1 Email/Password Login

```mermaid
sequenceDiagram
    participant U as User
    participant F as Frontend
    participant A as API
    participant D as Database

    U->>F: Enter email/password
    F->>A: POST /auth/login
    A->>D: Find user by email
    D-->>A: User record
    A->>A: Verify password (bcrypt)
    alt Password valid
        A->>A: Generate JWT access token
        A->>A: Generate refresh token
        A->>D: Store refresh token
        A-->>F: {access_token, refresh_token}
        F->>F: Store tokens
        F-->>U: Redirect to dashboard
    else Password invalid
        A-->>F: 401 Unauthorized
        F-->>U: Show error
    end
```

### 2.2 OAuth Flow

```mermaid
sequenceDiagram
    participant U as User
    participant F as Frontend
    participant A as API
    participant O as OAuth Provider

    U->>F: Click "Sign in with Google"
    F->>O: Redirect to OAuth consent
    U->>O: Grant consent
    O->>F: Redirect with auth code
    F->>A: POST /auth/oauth/callback
    A->>O: Exchange code for tokens
    O-->>A: {access_token, id_token}
    A->>A: Validate id_token
    A->>D: Find or create user
    A->>A: Generate JWT tokens
    A-->>F: {access_token, refresh_token}
    F-->>U: Redirect to dashboard
```

### 2.3 Token Refresh

```mermaid
sequenceDiagram
    participant F as Frontend
    participant A as API
    participant D as Database

    F->>F: Access token expiring
    F->>A: POST /auth/refresh
    A->>D: Validate refresh token
    alt Token valid
        A->>A: Generate new access token
        A-->>F: {access_token}
        F->>F: Update stored token
    else Token invalid/expired
        A-->>F: 401 Unauthorized
        F->>F: Clear tokens
        F-->>U: Redirect to login
    end
```

---

## 3. Item CRUD Flow

### 3.1 Create Item

```mermaid
sequenceDiagram
    participant U as User
    participant F as Frontend
    participant A as API
    participant D as Database

    U->>F: Click "Add Item"
    F->>F: Open create dialog
    U->>F: Fill form, submit
    F->>A: POST /projects/{id}/items
    A->>A: Validate request (Pydantic)
    A->>A: Check permissions (RBAC)
    A->>D: Get next_item_num
    D-->>A: next_item_num
    A->>D: INSERT item
    A->>D: UPDATE project.next_item_num
    A->>D: INSERT audit_log
    D-->>A: Created item
    A->>A: Calculate indicator
    A-->>F: Item response
    F->>F: Close dialog, refresh list
    F-->>U: Show success toast
```

### 3.2 Update Item

```mermaid
sequenceDiagram
    participant U as User
    participant F as Frontend
    participant A as API
    participant D as Database

    U->>F: Edit item, save
    F->>A: PUT /projects/{pid}/items/{id}
    A->>A: Validate request
    A->>A: Check permissions
    A->>D: Get current item
    D-->>A: Current state
    A->>D: UPDATE item
    A->>D: INSERT audit_log (with before/after)
    D-->>A: Updated item
    A->>A: Recalculate indicator
    A-->>F: Item response
    F->>F: Update UI
    F-->>U: Show success toast
```

---

## 4. Budget Calculation Flow

### 4.1 Calculate Metrics

```mermaid
flowchart TD
    A[Load Budget Data] --> B{Has Timesheet Data?}
    B -->|No| C[Return empty metrics]
    B -->|Yes| D[Filter complete weeks]
    D --> E[Calculate burn_to_date]
    E --> F[Calculate weeks_completed]
    F --> G[Calculate weekly_avg_burn]
    G --> H[Calculate remaining_burn]
    H --> I[Calculate est_total_burn]
    I --> J[Calculate budget_remaining]
    J --> K{budget_remaining < 0?}
    K -->|Yes| L[Status: Over Budget]
    K -->|No| M{< 15% remaining?}
    M -->|Yes| N[Status: Within 15%]
    M -->|No| O[Status: Under Budget]
    L --> P[Return BudgetMetrics]
    N --> P
    O --> P
```

### 4.2 Weekly Burn Calculation

```python
def calculate_weekly_burn(timesheet_entries: list) -> list[WeeklyBurn]:
    """Calculate weekly burn with cumulative."""
    by_week = defaultdict(float)

    for entry in timesheet_entries:
        if entry.complete_week:
            by_week[entry.week_ending] += entry.cost

    weekly_burn = []
    cumulative = 0.0

    for week in sorted(by_week.keys()):
        cost = round(by_week[week], 2)
        cumulative = round(cumulative + cost, 2)
        weekly_burn.append(WeeklyBurn(
            week_ending=week,
            cost=cost,
            cumulative=cumulative
        ))

    return weekly_burn
```

---

## 5. AI Chat Flow

### 5.1 Send Message

```mermaid
sequenceDiagram
    participant U as User
    participant F as Frontend
    participant A as API
    participant C as Claude API
    participant D as Database

    U->>F: Type message, send
    F->>A: POST /chat/sessions/{id}/messages
    A->>A: Check permissions
    A->>D: Get session with history
    D-->>A: Session + messages
    A->>D: Get project context
    D-->>A: Project, items, budget
    A->>A: Build system prompt
    A->>C: Send to Claude API
    C-->>A: Response
    A->>D: Store user message
    A->>D: Store assistant message
    A-->>F: Message response
    F->>F: Display message
    F-->>U: Show response
```

### 5.2 Context Building

```mermaid
flowchart TD
    A[User Message] --> B{Check scope request}
    B -->|Current project| C[Load project context]
    B -->|Portfolio| D[Load portfolio projects]
    B -->|All projects| E[Load all accessible projects]

    C --> F[Get project metadata]
    D --> F
    E --> F

    F --> G[Get open items]
    G --> H[Get critical items]
    H --> I[Get budget metrics]
    I --> J[Format for Claude]
    J --> K[Build system prompt]
    K --> L[Send to Claude]
```

### 5.3 RBAC Enforcement

```python
async def get_chat_context(
    user_id: UUID,
    project_id: UUID,
    scope: str
) -> ChatContext:
    """Get context respecting RBAC."""

    if scope == "current":
        # Verify access to project
        if not await has_project_access(user_id, project_id):
            raise AuthorizationError("No access to project")
        return await build_project_context(project_id)

    elif scope == "portfolio":
        # Get portfolio and verify access to all projects
        portfolio = await get_portfolio_for_project(project_id)
        projects = await get_accessible_portfolio_projects(user_id, portfolio.id)
        return await build_portfolio_context(projects)

    elif scope == "all":
        # Get all user's accessible projects
        projects = await get_user_accessible_projects(user_id)
        return await build_multi_project_context(projects)
```

---

## 6. Multi-Tenancy Flow

### 6.1 Request Routing

```mermaid
flowchart TD
    A[Incoming Request] --> B[Extract JWT]
    B --> C[Validate token]
    C --> D[Get org_id from token]
    D --> E{Org exists?}
    E -->|No| F[401 Unauthorized]
    E -->|Yes| G[Get org database name]
    G --> H[Get/create connection pool]
    H --> I[Bind connection to request]
    I --> J[Process request]
    J --> K[Return response]
```

### 6.2 Organization Database Selection

```python
async def get_org_connection(org_id: UUID) -> asyncpg.Pool:
    """Get database connection for organization."""
    # Check cache
    if org_id in connection_pools:
        return connection_pools[org_id]

    # Get org from central DB
    org = await central_db.get_organization(org_id)
    if not org:
        raise NotFoundError("Organization", str(org_id))

    # Create pool for org database
    pool = await asyncpg.create_pool(
        database=org.database_name,
        **connection_settings
    )

    connection_pools[org_id] = pool
    return pool
```

---

## 7. Export Flow

### 7.1 Generate Export

```mermaid
flowchart TD
    A[Export Request] --> B{Format?}
    B -->|Markdown| C[Build Markdown]
    B -->|CSV| D[Build CSV]

    C --> E{Report Type?}
    E -->|Active| F[Filter active items]
    E -->|Summary| G[Calculate stats]
    E -->|Table| H[Format table]

    D --> I[Get columns]
    I --> J[Format rows]

    F --> K[Generate content]
    G --> K
    H --> K
    J --> K

    K --> L[Return file]
```

---

## 8. Permission Check Flow

### 8.1 API Endpoint Check

```mermaid
flowchart TD
    A[API Request] --> B[Extract user from JWT]
    B --> C[Get requested resource]
    C --> D{Resource type?}

    D -->|Organization| E[Check org role]
    D -->|Project| F[Check project role]
    D -->|Item| G[Get item's project]

    E --> H{Has permission?}
    F --> H
    G --> F

    H -->|Yes| I[Continue to handler]
    H -->|No| J[403 Forbidden]
```

### 8.2 Permission Matrix

| Action | Admin | Project Manager | Team Member | Viewer |
|--------|-------|-----------------|-------------|--------|
| View project | Yes | Yes | Yes | Yes |
| Create item | Yes | Yes | Assigned only | No |
| Edit item | Yes | Yes | Assigned only | No |
| Delete item | Yes | Yes | No | No |
| Edit project | Yes | Yes | No | No |
| Manage team | Yes | No | No | No |
| View budget | Yes | Yes | Yes | Yes |
| Edit budget | Yes | Yes | No | No |

---

## Related Documentation

| Document | Purpose |
|----------|---------|
| [REQUIREMENTS.md](REQUIREMENTS.md) | Business requirements |
| [USER_STORIES.md](USER_STORIES.md) | Implementation stories |
| [DATA_MODEL.md](DATA_MODEL.md) | Database schema |
| [ARCHITECTURE.md](ARCHITECTURE.md) | System design |
| [PATTERNS.md](PATTERNS.md) | Code patterns |

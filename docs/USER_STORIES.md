# braidMgr User Stories

*Last updated: 2024-12-24 (v1)*

This document organizes braidMgr v1.5 and v2 implementation into user stories, sequenced by dependencies. Stories trace to requirements in REQUIREMENTS.md.

---

## Story Format

Each story includes:
- **ID**: Unique identifier (S1-001 = Sequence 1, Story 001)
- **Title**: Brief description
- **Story**: As a [role], I want [goal], so that [benefit]
- **Acceptance Criteria**: Testable conditions
- **Traces**: Requirement IDs from REQUIREMENTS.md

---

## Sequence Overview

### v1.5 - Web Conversion

| Seq | Name | Stories | Dependencies | Priority |
|-----|------|---------|--------------|----------|
| 1 | Foundation | 8 | None | MVP |
| 2 | Authentication | 6 | Seq 1 | MVP |
| 3 | Core Data | 8 | Seq 1, 2 | MVP |
| 4 | Views | 8 | Seq 3 | MVP |
| 5 | Budget | 4 | Seq 3 | MVP |
| 6 | PWA | 3 | Seq 4, 5 | MVP |

### v2.0 - Enterprise Features

| Seq | Name | Stories | Dependencies | Priority |
|-----|------|---------|--------------|----------|
| 7 | Multi-User | 6 | Seq 2 | MVP |
| 8 | Multi-Org | 4 | Seq 7 | MVP |
| 9 | Portfolios | 3 | Seq 7, 8 | MVP |
| 10 | AI Chat | 5 | Seq 3, 7 | MVP |
| 11 | Attachments | 3 | Seq 3, 8 | Post-MVP |
| 12 | Exports | 3 | Seq 4, 5 | MVP |
| 13 | SSO | 2 | Seq 7, 8 | Post-MVP |
| 14 | Global Search | 2 | Seq 3, 11 | Post-MVP |

---

## Sequence 1: Foundation

Infrastructure and project scaffolding.

Depends on: None

### S1-001: FastAPI Project Setup

**Story**: As a developer, I want the FastAPI backend scaffolded with proper structure, so that I can build API endpoints following established patterns.

**Acceptance Criteria**:
- Project structure created (src/api, src/services, src/repositories, src/domain)
- FastAPI app configured with CORS, middleware
- Health check endpoint /health returns status
- OpenAPI docs available at /docs
- uvicorn configured for development

**Traces**: WEB-004

---

### S1-002: React Project Setup

**Story**: As a developer, I want the React frontend scaffolded with Vite and TypeScript, so that I can build UI components.

**Acceptance Criteria**:
- Vite + React 18 + TypeScript project created
- Tailwind CSS configured
- shadcn/ui initialized with base components
- ESLint + Prettier configured
- Development server runs with hot reload

**Traces**: WEB-003, WEB-008

---

### S1-003: PostgreSQL Schema Setup

**Story**: As a developer, I want the PostgreSQL schema created with migrations, so that data can be persisted.

**Acceptance Criteria**:
- Alembic configured for migrations
- Initial migration creates all v1.5 tables
- Enum types created (item_type, indicator, role)
- Indexes on frequently queried columns
- Connection pooling configured

**Traces**: WEB-005

---

### S1-004: Service Centralization

**Story**: As a developer, I want a centralized service registry, so that all external service access goes through a single interface.

**Acceptance Criteria**:
- ServiceRegistry singleton implemented
- BaseService abstract class with logging, retry
- AuroraService (database) implemented
- Services validate connections at startup
- Health checks for all services

**Traces**: WEB-004, ENT-008

---

### S1-005: Error Handling Framework

**Story**: As a developer, I want consistent error handling, so that all errors return predictable responses.

**Acceptance Criteria**:
- Custom exception hierarchy (AppError base)
- ValidationError, NotFoundError, AuthenticationError, etc.
- Error handler middleware maps exceptions to HTTP responses
- Correlation ID included in error responses
- No sensitive data in error messages

**Traces**: WEB-007

---

### S1-006: Structured Logging

**Story**: As a developer, I want structured logging with correlation IDs, so that requests can be traced across logs.

**Acceptance Criteria**:
- structlog configured
- Correlation ID middleware adds ID to all logs
- Request logging middleware (start, complete, timing)
- Log levels by layer (API=INFO, Repository=DEBUG)
- JSON format in production, console in dev

**Traces**: ENT-008

---

### S1-007: Configuration Management

**Story**: As a developer, I want centralized configuration, so that settings are consistent and environment-aware.

**Acceptance Criteria**:
- config.yaml with all settings
- Environment variable substitution ${VAR}
- Pydantic settings for validation
- Secrets loaded from environment (not in config)
- Defaults for local development

**Traces**: WEB-004

---

### S1-008: Docker Development Environment

**Story**: As a developer, I want Docker Compose for local development, so that I can run all services locally.

**Acceptance Criteria**:
- docker-compose.yml with PostgreSQL, API, frontend
- Volume mounts for hot reload
- Environment variables configured
- Single command startup (docker compose up)
- Database initialization on first run

**Traces**: WEB-005

---

## Sequence 2: Authentication

User authentication and session management.

Depends on: Sequence 1

### S2-001: User Registration

**Story**: As a new user, I want to register with email and password, so that I can access the application.

**Acceptance Criteria**:
- Registration form (email, password, name)
- Password strength validation (8+ chars, mixed case, number)
- Email uniqueness check
- Confirmation email sent (optional for MVP)
- User created in database with hashed password

**Traces**: WEB-006

---

### S2-002: Email/Password Login

**Story**: As a registered user, I want to log in with email and password, so that I can access my data.

**Acceptance Criteria**:
- Login form (email, password)
- Password verification with bcrypt
- JWT access token issued (15 min expiry)
- Refresh token issued (7 day expiry)
- Tokens stored securely (httpOnly cookies or secure storage)

**Traces**: WEB-006

---

### S2-003: OAuth - Google

**Story**: As a user, I want to log in with Google, so that I don't need a separate password.

**Acceptance Criteria**:
- "Sign in with Google" button
- OAuth 2.0 flow implemented
- User created or linked on first OAuth login
- Email verified flag set from Google
- JWT tokens issued after OAuth success

**Traces**: WEB-006

---

### S2-004: OAuth - Microsoft

**Story**: As a user, I want to log in with Microsoft, so that I can use my work account.

**Acceptance Criteria**:
- "Sign in with Microsoft" button
- Azure AD OAuth 2.0 flow
- User created or linked on first login
- Works with personal and work accounts
- JWT tokens issued after OAuth success

**Traces**: WEB-006

---

### S2-005: Token Refresh

**Story**: As a logged-in user, I want my session to stay active, so that I don't have to log in repeatedly.

**Acceptance Criteria**:
- Refresh token endpoint
- Access token refreshed automatically before expiry
- Refresh token rotation (optional)
- Invalid refresh token requires re-login
- Logout invalidates refresh token

**Traces**: WEB-006

---

### S2-006: Password Reset

**Story**: As a user who forgot my password, I want to reset it, so that I can regain access.

**Acceptance Criteria**:
- "Forgot password" link on login
- Email sent with reset link (1 hour expiry)
- Reset form validates new password
- Old password invalidated
- User notified of password change

**Traces**: WEB-006

---

## Sequence 3: Core Data

RAID item and project data management.

Depends on: Sequences 1, 2

### S3-001: Project CRUD

**Story**: As a project manager, I want to create and manage projects, so that I can organize my RAID items.

**Acceptance Criteria**:
- Create project (name, client, dates, workstreams)
- Edit project metadata
- Delete project (soft delete with confirmation)
- List projects for current user
- Project assigned to organization

**Traces**: PAR-004, WEB-005

---

### S3-002: Item CRUD

**Story**: As a team member, I want to create and edit RAID items, so that I can track project work.

**Acceptance Criteria**:
- Create item with all fields from PAR-002
- Edit item via modal dialog
- Delete item (soft delete)
- Item number auto-assigned
- created_date and last_updated tracked

**Traces**: PAR-002, PAR-012

---

### S3-003: Item Types

**Story**: As a team member, I want to categorize items by type, so that I can distinguish risks from actions.

**Acceptance Criteria**:
- All 7 item types available in dropdown
- Type-specific styling/colors
- Filter by type in list view
- Type stored and persisted correctly

**Traces**: PAR-001

---

### S3-004: Indicator Calculation

**Story**: As a user, I want status indicators calculated automatically, so that I can see item health at a glance.

**Acceptance Criteria**:
- All 10 indicators calculate per PAR-003 rules
- Indicators update on item save
- Batch update action available
- Draft items excluded from indicators
- Severity ordering correct

**Traces**: PAR-003, PAR-018

---

### S3-005: Workstream Management

**Story**: As a project manager, I want to define workstreams, so that I can organize items by area.

**Acceptance Criteria**:
- Add/remove workstreams in project settings
- Workstream dropdown populated from project
- Items can be assigned to workstream
- Workstream filter in list view

**Traces**: PAR-004, PAR-016

---

### S3-006: Item Filtering

**Story**: As a user, I want to filter items by various criteria, so that I can find what I need.

**Acceptance Criteria**:
- Filter by type, workstream, assignee, status
- Search by title and description
- Filters combine with AND logic
- Clear all filters option
- Filter state persists in session

**Traces**: PAR-016

---

### S3-007: YAML Import

**Story**: As an admin (Don), I want to import existing YAML files, so that v1 data is migrated.

**Acceptance Criteria**:
- Import RAID-Log-*.yaml files
- Import Budget-*.yaml files
- Data maps to new schema correctly
- Validation errors reported clearly
- One-time migration script (not user-facing)

**Traces**: PAR-013

---

### S3-008: Data Validation

**Story**: As a user, I want form validation, so that I enter valid data.

**Acceptance Criteria**:
- Required fields validated (title)
- Date format validation
- Percent complete 0-100
- Field-level error messages
- Submit blocked until valid

**Traces**: PAR-002, WEB-007

---

## Sequence 4: Views

UI views matching v1 functionality.

Depends on: Sequence 3

### S4-001: Dashboard View

**Story**: As a user, I want a dashboard overview, so that I can see project health at a glance.

**Acceptance Criteria**:
- Summary cards (Critical, Warning, Active, Completed, Total)
- Counts accurate and update on data changes
- Clickable cards navigate to filtered list
- Budget status indicator displayed
- Loads within 1 second

**Traces**: PAR-005

---

### S4-002: All Items View

**Story**: As a user, I want a tabular list of all items, so that I can browse and manage them.

**Acceptance Criteria**:
- Table with columns per PAR-006
- Sortable columns (click header)
- Filter controls (type, workstream, status, search)
- Double-click opens edit dialog
- Responsive on tablet/mobile

**Traces**: PAR-006, WEB-002

---

### S4-003: Active Items View

**Story**: As a user, I want to see only active items grouped by severity, so that I can focus on what needs attention.

**Acceptance Criteria**:
- Excludes completed items
- Groups by severity (Critical, Warning, Active)
- Collapsible group cards
- Color-coded by severity
- Double-click opens edit dialog

**Traces**: PAR-007

---

### S4-004: Timeline View

**Story**: As a user, I want a Gantt-style timeline, so that I can visualize item schedules.

**Acceptance Criteria**:
- Items plotted by start/finish dates
- Color-coded by indicator status
- Today line visible
- Hover shows item details
- Scroll/zoom controls

**Traces**: PAR-008

---

### S4-005: Chronology View

**Story**: As a user, I want a monthly timeline, so that I can see items by month.

**Acceptance Criteria**:
- Items grouped by month
- Collapsible month sections
- Current month highlighted
- Items sorted by date within month

**Traces**: PAR-009

---

### S4-006: Help View

**Story**: As a user, I want in-app help, so that I can learn how to use the application.

**Acceptance Criteria**:
- Documentation displayed in app
- Keyboard shortcuts listed
- Searchable or indexed
- Contact/feedback link

**Traces**: PAR-017

---

### S4-007: Edit Item Dialog

**Story**: As a user, I want a modal dialog for editing items, so that I can update item details.

**Acceptance Criteria**:
- All fields editable per PAR-012
- Date pickers for date fields
- Slider or numeric for percent complete
- Save and Cancel buttons
- Validation errors displayed

**Traces**: PAR-012

---

### S4-008: Onboarding & Contextual Help

**Story**: As a new user, I want guided onboarding and contextual help, so that I can learn the app quickly without reading documentation.

**Acceptance Criteria**:
- First-time user tour (3-5 key features)
- Tooltips on complex fields (hover for explanation)
- Empty state guidance ("No items yet - click here to add your first")
- Keyboard shortcut hints in menus
- Skip/dismiss option for experienced users
- Tour can be restarted from Help menu

**Traces**: PAR-017

---

## Sequence 5: Budget

Budget tracking and visualization.

Depends on: Sequence 3

### S5-001: Budget Data Model

**Story**: As a developer, I want an optimized budget schema, so that budget data is flexible and complete.

**Acceptance Criteria**:
- Rate card table (resource, role, rate, dates)
- Timesheet/actuals table
- Budget allocation by workstream/phase
- Variance tracking (planned vs actual)
- Schema documented in DATA_MODEL.md

**Traces**: PAR-011

---

### S5-002: Budget View

**Story**: As a user, I want to see budget metrics, so that I can track financial health.

**Acceptance Criteria**:
- Metric cards per PAR-010
- Progress bar for burn percentage
- Status indicator (over/under/within 15%)
- Loads within 1 second

**Traces**: PAR-010

---

### S5-003: Weekly Burn Chart

**Story**: As a user, I want a weekly burn chart, so that I can see spend trends.

**Acceptance Criteria**:
- Bar chart showing weekly costs
- Cumulative line optional
- Interactive (hover shows values)
- Responsive sizing

**Traces**: PAR-010

---

### S5-004: Resource Breakdown

**Story**: As a user, I want a resource cost breakdown, so that I can see who is consuming budget.

**Acceptance Criteria**:
- Table with resource, hours, cost
- Sorted by cost descending
- Percentage of total column
- Exportable to CSV

**Traces**: PAR-010

---

## Sequence 6: PWA

Progressive Web App capabilities.

Depends on: Sequences 4, 5

### S6-001: Service Worker

**Story**: As a user, I want the app to work offline, so that I can access data without internet.

**Acceptance Criteria**:
- Service worker caches app shell
- Previously viewed data available offline
- Offline indicator visible
- Sync when connection restored

**Traces**: WEB-001

---

### S6-002: App Manifest

**Story**: As a user, I want to install the app, so that I can launch it like a native app.

**Acceptance Criteria**:
- manifest.json with name, icons, colors
- Install prompt appears on supported browsers
- App launches in standalone mode
- Icons display correctly on all platforms

**Traces**: WEB-001

---

### S6-003: Responsive Design

**Story**: As a user, I want the app to work on any device, so that I can use it on mobile.

**Acceptance Criteria**:
- Desktop, tablet, mobile layouts work
- Navigation adapts (sidebar collapses)
- Touch-friendly controls on mobile
- Tables scroll horizontally on narrow screens

**Traces**: WEB-002

---

## Sequence 7: Multi-User

User roles and permissions.

Depends on: Sequence 2

### S7-001: User Profile

**Story**: As a user, I want to manage my profile, so that my information is current.

**Acceptance Criteria**:
- View/edit name, email
- Change password
- Profile picture (optional)
- Notification preferences

**Traces**: ENT-002

---

### S7-002: Role Definition

**Story**: As an admin, I want predefined roles, so that permissions are consistent.

**Acceptance Criteria**:
- Admin: Full access
- ProjectManager: Create/edit projects
- TeamMember: View/edit assigned items
- Viewer: Read-only
- Roles documented

**Traces**: ENT-002

---

### S7-003: Role Assignment

**Story**: As an admin, I want to assign roles to users, so that they have appropriate access.

**Acceptance Criteria**:
- Assign role per project
- Users can have different roles per project
- Role changes take effect immediately
- Audit log of role changes

**Traces**: ENT-002

---

### S7-004: Permission Enforcement

**Story**: As the system, I want to enforce permissions, so that users can only do what they're allowed.

**Acceptance Criteria**:
- API endpoints check permissions
- UI hides unauthorized actions
- 403 returned for denied requests
- Permission check on every request

**Traces**: ENT-002

---

### S7-005: User Invitation

**Story**: As an admin, I want to invite users, so that team members can join.

**Acceptance Criteria**:
- Invite by email
- Invitation email with link
- Role assigned on invitation
- Invitation expires after 7 days

**Traces**: ENT-002

---

### S7-006: Real-Time Collaboration

**Story**: As a team member, I want to see changes made by others, so that I work with current data.

**Acceptance Criteria**:
- Changes by others visible within 30 seconds
- Edit conflict detection and notification
- Data refresh on focus or via manual button
- Optional user presence indicators (Post-MVP)

**Traces**: ENT-009

---

## Sequence 8: Multi-Org

Organization-level isolation.

Depends on: Sequence 7

### S8-001: Organization Creation

**Story**: As a super-admin, I want to create organizations, so that tenants are isolated.

**Acceptance Criteria**:
- Create org with name, settings
- Separate database provisioned
- Admin user assigned
- Organization-level branding (optional)

**Traces**: ENT-001

---

### S8-002: Database Isolation

**Story**: As the system, I want database-per-org isolation, so that data never leaks.

**Acceptance Criteria**:
- Connection routes to correct database
- Org ID validated on every request
- No cross-org queries possible
- Audit logging per org

**Traces**: ENT-001

---

### S8-003: Organization Settings

**Story**: As an org admin, I want to manage org settings, so that the org is configured correctly.

**Acceptance Criteria**:
- Edit org name, logo
- Manage default settings
- View org members
- Configure org-level features

**Traces**: ENT-001

---

### S8-004: Organization Member Management

**Story**: As an org admin, I want to manage org members, so that I control who has access.

**Acceptance Criteria**:
- Add/remove members
- Set org-level role
- View member list
- Deactivate members

**Traces**: ENT-001

---

## Sequence 9: Portfolios

Flexible project grouping.

Depends on: Sequences 7, 8

### S9-001: Portfolio CRUD

**Story**: As a user, I want to create portfolios, so that I can group related projects.

**Acceptance Criteria**:
- Create portfolio (name, description)
- Edit portfolio details
- Delete portfolio (projects remain)
- List user's portfolios

**Traces**: ENT-003

---

### S9-002: Portfolio Assignment

**Story**: As a user, I want to add projects to portfolios, so that they're organized.

**Acceptance Criteria**:
- Add project to portfolio
- Remove project from portfolio
- Project can be in multiple portfolios
- Drag-drop organization (optional)

**Traces**: ENT-003

---

### S9-003: Portfolio Dashboard

**Story**: As a user, I want a portfolio dashboard, so that I see aggregated metrics.

**Acceptance Criteria**:
- Aggregated item counts
- Aggregated budget totals
- List of included projects
- Drill-down to project

**Traces**: ENT-003

---

## Sequence 10: AI Chat

Claude integration for natural language interface.

Depends on: Sequences 3, 7

### S10-001: Chat Interface

**Story**: As a user, I want a chat interface, so that I can ask questions naturally.

**Acceptance Criteria**:
- Chat panel embedded in app
- Send messages with Enter
- Message history displayed
- Typing indicator during response

**Traces**: ENT-004

---

### S10-002: Claude Integration

**Story**: As the system, I want to call Claude API, so that chat requests get AI responses.

**Acceptance Criteria**:
- Claude API integration via SDK
- Context from current project included
- Token usage tracked
- Rate limiting applied

**Traces**: ENT-004

---

### S10-003: Context Scoping

**Story**: As a user, I want the AI to understand my project context, so that responses are relevant.

**Acceptance Criteria**:
- Default context: current project
- Can expand scope by asking
- RBAC enforced (only query accessible data)
- Context indicated in UI

**Traces**: ENT-004

---

### S10-004: Chat History

**Story**: As a user, I want chat history saved, so that I can refer to past conversations.

**Acceptance Criteria**:
- Conversations persisted per user
- Retrieve recent conversations
- Delete conversations
- Search history (optional)

**Traces**: ENT-004

---

### S10-005: AI Data Access

**Story**: As the AI, I want access to project data, so that I can answer questions accurately.

**Acceptance Criteria**:
- Items queryable by AI
- Budget data accessible
- AI can reference specific items
- Data formatted for AI consumption

**Traces**: ENT-004

---

## Sequence 11: Attachments

File attachment capabilities.

Depends on: Sequences 3, 8

### S11-001: File Upload

**Story**: As a user, I want to upload files to items, so that I can attach supporting documents.

**Acceptance Criteria**:
- Upload button on item edit dialog
- Support images (jpg, png, gif), documents (pdf, docx), spreadsheets (xlsx)
- File size limit enforced (10MB per file)
- Progress indicator during upload
- Files stored in S3

**Traces**: ENT-005

---

### S11-002: File Display

**Story**: As a user, I want to view attached files, so that I can access item documentation.

**Acceptance Criteria**:
- Attachment list on item detail
- Images display inline with lightbox
- Documents downloadable via signed URL
- File metadata shown (name, size, upload date)

**Traces**: ENT-005

---

### S11-003: File Management

**Story**: As a user, I want to manage attachments, so that I can remove outdated files.

**Acceptance Criteria**:
- Delete attachment option
- Confirmation before delete
- Only uploader or admin can delete
- Audit log entry on delete

**Traces**: ENT-005

---

## Sequence 12: Exports

Export functionality.

Depends on: Sequences 4, 5

### S12-001: Markdown Export

**Story**: As a user, I want to export to Markdown, so that I can share reports.

**Acceptance Criteria**:
- Active items report
- Summary report
- Table format
- Download as .md file

**Traces**: PAR-014

---

### S12-002: CSV Export

**Story**: As a user, I want to export to CSV, so that I can analyze in Excel.

**Acceptance Criteria**:
- All columns exported
- Dates formatted correctly
- Special characters escaped
- Download as .csv file

**Traces**: PAR-015

---

### S12-003: Filtered Export

**Story**: As a user, I want to export filtered results, so that I get only what I need.

**Acceptance Criteria**:
- Export current filter state
- By type, assignee, workstream, status
- Export open items only
- Export critical items only

**Traces**: PAR-014, PAR-015, PAR-016

---

## Sequence 13: SSO

Enterprise Single Sign-On integration.

Depends on: Sequences 7, 8

### S13-001: SSO Configuration

**Story**: As an org admin, I want to configure SSO, so that users can log in with their corporate credentials.

**Acceptance Criteria**:
- SSO settings in org admin panel
- Support SAML 2.0 and OIDC protocols
- Identity provider metadata upload
- Test connection before enabling
- Fallback to email/password if SSO fails

**Traces**: ENT-006

---

### S13-002: SSO Login Flow

**Story**: As a user, I want to log in via SSO, so that I use my work credentials.

**Acceptance Criteria**:
- Redirect to IdP login page
- Return with authenticated session
- Auto-provision user on first login
- Map IdP attributes to user profile
- SSO-only mode option per org

**Traces**: ENT-006

---

## Sequence 14: Global Search

Full-text search across all data.

Depends on: Sequences 3, 11

### S14-001: Search Index

**Story**: As a developer, I want searchable content indexed, so that search is fast.

**Acceptance Criteria**:
- PostgreSQL full-text search on items
- Index on title, description, notes
- Attachment filename indexed
- Index updates on data changes

**Traces**: ENT-007

---

### S14-002: Search Interface

**Story**: As a user, I want to search across all content, so that I can find items quickly.

**Acceptance Criteria**:
- Global search bar in header
- Results grouped by type (items, attachments)
- Highlights matching text
- Click result navigates to item
- Respects RBAC permissions

**Traces**: ENT-007

---

## Dependency Graph

```
Sequence 1 (Foundation)
    |
    +---> Sequence 2 (Auth)
    |         |
    |         +---> Sequence 7 (Multi-User)
    |         |         |
    |         |         +---> Sequence 8 (Multi-Org)
    |         |         |         |
    |         |         |         +---> Sequence 9 (Portfolios)
    |         |         |         |
    |         |         |         +---> Sequence 11 (Attachments) --> Sequence 14 (Search)
    |         |         |
    |         |         +---> Sequence 13 (SSO)
    |         |
    |         +---> Sequence 3 (Core Data)
    |                   |
    |                   +---> Sequence 4 (Views) ---> Sequence 6 (PWA)
    |                   |         |
    |                   |         +---> Sequence 12 (Exports)
    |                   |
    |                   +---> Sequence 5 (Budget)
    |                   |
    |                   +---> Sequence 10 (AI Chat)
```

---

## Story Count Summary

| Sequence | Name | Stories | Priority |
|----------|------|---------|----------|
| 1 | Foundation | 8 | MVP |
| 2 | Authentication | 6 | MVP |
| 3 | Core Data | 8 | MVP |
| 4 | Views | 8 | MVP |
| 5 | Budget | 4 | MVP |
| 6 | PWA | 3 | MVP |
| 7 | Multi-User | 6 | MVP |
| 8 | Multi-Org | 4 | MVP |
| 9 | Portfolios | 3 | MVP |
| 10 | AI Chat | 5 | MVP |
| 11 | Attachments | 3 | Post-MVP |
| 12 | Exports | 3 | MVP |
| 13 | SSO | 2 | Post-MVP |
| 14 | Global Search | 2 | Post-MVP |
| **Total** | | **65** | **57 MVP** |

---

## Requirements Coverage

All requirements from REQUIREMENTS.md are traced:
- **PAR (18)**: Covered in Sequences 3, 4, 5, 12
- **WEB (8)**: Covered in Sequences 1, 2, 6
- **ENT (9)**: Covered in Sequences 7, 8, 9, 10, 11, 13, 14

Coverage: 100%

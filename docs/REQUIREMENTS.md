# braidMgr Requirements

*Last updated: 2024-12-24 (v1)*

This document defines requirements for braidMgr v1.5 and v2. Requirements are organized into three categories:
- **PAR-NNN**: Parity requirements (v1 features to maintain for regression testing)
- **WEB-NNN**: Web platform requirements (v1.5 PWA conversion)
- **ENT-NNN**: Enterprise requirements (v2 multi-tenant, multi-user features)

---

## Requirement Format

Each requirement includes:
- **ID**: Unique identifier (PAR-001, WEB-001, ENT-001)
- **Title**: Brief description
- **Description**: Detailed requirement
- **Acceptance Criteria**: Testable conditions
- **Priority**: MVP or Post-MVP

---

## PAR: v1 Parity Requirements

These document the current v1 functionality. All must be preserved in v1.5 for regression testing.

### PAR-001: Item Types

**Title**: Support 7 BRAID item types

**Description**: The system shall support the following item types:
- Budget
- Risk
- Action Item
- Issue
- Decision
- Deliverable
- Plan Item

**Acceptance Criteria**:
- All 7 item types can be created
- Items display with type-appropriate styling
- Filtering by type works correctly

**Priority**: MVP

---

### PAR-002: Item Fields

**Title**: Support all item data fields

**Description**: Each item shall have the following fields:
- item_num (unique within project)
- type (one of 7 types)
- title (required)
- workstream (optional)
- description (optional, multi-line)
- assigned_to (optional)
- dep_item_num (list of dependent item numbers)
- start date (optional)
- finish date (optional)
- duration (optional, in days)
- deadline (optional)
- draft (boolean, excludes from views if true)
- client_visible (boolean)
- percent_complete (0-100)
- rpt_out (list of report codes)
- created_date
- last_updated
- notes (multi-line with dated entries)
- indicator (calculated status)
- priority (optional)
- budget_amount (for Budget type items)

**Acceptance Criteria**:
- All fields can be edited via item dialog
- Fields persist correctly through save/load cycles
- Empty optional fields handled gracefully

**Priority**: MVP

---

### PAR-003: Status Indicators

**Title**: Automatic status indicator calculation

**Description**: The system shall automatically calculate status indicators based on dates and progress:

| Indicator | Severity | Condition |
|-----------|----------|-----------|
| Beyond Deadline!!! | critical | Deadline has passed |
| Late Finish!! | critical | Finish date passed, not 100% complete |
| Late Start!! | critical | Start date passed, 0% complete |
| Trending Late! | warning | Remaining work > remaining time |
| Finishing Soon! | active | Finish within 2 weeks, not complete |
| Starting Soon! | upcoming | Start within 2 weeks, not started |
| In Progress | active | Between 1-99% complete |
| Not Started | upcoming | Has dates, 0% complete |
| Completed Recently | completed | 100% and finished within 2 weeks |
| Completed | done | 100% complete |

**Acceptance Criteria**:
- Indicators calculate correctly per precedence rules
- Draft items receive no indicator
- Indicators update when dates/progress change
- Batch update available via "Update Indicators" action

**Priority**: MVP

---

### PAR-004: Project Metadata

**Title**: Project-level metadata storage

**Description**: Each project shall store metadata:
- project_name (required)
- client_name (optional)
- next_item_num (auto-increment counter)
- last_updated (timestamp)
- project_start date
- project_end date
- indicators_updated (timestamp of last recalculation)
- workstreams (list of strings)

**Acceptance Criteria**:
- Metadata displays in appropriate views
- Workstream list populates filter dropdowns
- next_item_num increments when items created

**Priority**: MVP

---

### PAR-005: Dashboard View

**Title**: Summary dashboard with statistics

**Description**: Dashboard view shall display:
- Summary cards showing counts by severity:
  - Critical items count
  - Warning items count
  - Active items count
  - Completed items count
  - Total items count
- Budget status indicator (if budget data loaded)
- Health score or velocity metrics
- Clickable cards to navigate to filtered views

**Acceptance Criteria**:
- All counts accurate and update on data changes
- Clicking a card navigates to filtered All Items view
- Budget status reflects current calculations
- Dashboard loads within 1 second

**Priority**: MVP

---

### PAR-006: All Items View

**Title**: Tabular view of all items with filtering

**Description**: All Items view shall display:
- Table with columns: #, Type, Workstream, Title, Assignee, Indicator, Deadline
- Filter controls:
  - Type dropdown (all types + "All")
  - Workstream dropdown (all workstreams + "All")
  - Status/Indicator dropdown
  - Search text box
- Sortable columns (click header to sort)
- Double-click row opens Edit dialog

**Acceptance Criteria**:
- All items display in table
- Filters combine correctly (AND logic)
- Search filters on title and description
- Sorting works for all columns
- Column widths reasonable for content

**Priority**: MVP

---

### PAR-007: Active Items View

**Title**: Grouped view of non-completed items

**Description**: Active Items view shall display:
- Only non-completed items (excludes Completed, Completed Recently)
- Grouped by severity (Critical, Warning, Active, etc.)
- Collapsible group cards
- Color-coded by severity
- Double-click item opens Edit dialog

**Acceptance Criteria**:
- Completed items not shown
- Groups display in severity order
- Group cards show item count
- Items within groups sorted by deadline

**Priority**: MVP

---

### PAR-008: Timeline View

**Title**: Gantt-style timeline visualization

**Description**: Timeline view shall display:
- Items plotted by start/finish dates on horizontal timeline
- Color-coded bars by indicator status
- Date axis with week markers
- "Today" indicator line
- Hover tooltips showing full item details
- Double-click item opens Edit dialog

**Acceptance Criteria**:
- Items with dates display as bars
- Items without dates excluded or shown separately
- Timeline scrolls/zooms appropriately
- Today line clearly visible
- Colors match indicator severity

**Priority**: MVP

---

### PAR-009: Chronology View

**Title**: Monthly timeline with collapsible sections

**Description**: Chronology view shall display:
- Items grouped by month (based on deadline/finish date)
- Collapsible month sections
- Month headers with visual grouping
- Items sorted by date within month

**Acceptance Criteria**:
- All items with dates appear in correct month
- Sections expand/collapse correctly
- Current month highlighted or expanded by default

**Priority**: MVP

---

### PAR-010: Budget View

**Title**: Budget metrics and visualization

**Description**: Budget view shall display:
- Metric cards:
  - Budget Total
  - Burn to Date
  - Average Weekly Burn
  - Budget Remaining
- Progress bar showing burn percentage
- Budget status indicator (over/under/within 15%)
- Weekly burn chart (bar chart)
- Resource breakdown table (hours, cost per resource)

**Acceptance Criteria**:
- Metrics calculate correctly from budget data
- Progress bar reflects burn_to_date / budget_total
- Status indicator updates based on projections
- Chart displays weekly burn trend
- Resource table sorted by cost descending

**Priority**: MVP

---

### PAR-011: Budget Data Model

**Title**: Budget data structure

**Description**: Budget data shall include:
- Metadata: project_name, client, associated_raid_log, created, last_updated, data_source
- Rate card: resource name, geography, hourly rate, roll_off_date
- Budget ledger: amount, date, note (additions/changes)
- Timesheet data: week_ending, resource, hours, rate, cost, complete_week flag

**Acceptance Criteria**:
- All budget fields load from YAML
- Rate card used for projections
- Only complete weeks included in calculations
- Budget ledger sums to budget total

**Priority**: MVP

---

### PAR-012: Edit Item Dialog

**Title**: Modal dialog for editing items

**Description**: Edit dialog shall allow editing:
- All item fields from PAR-002
- Date fields with date picker
- Percent complete with slider or numeric input
- Notes with multi-line text area
- Save and Cancel buttons
- Validation for required fields

**Acceptance Criteria**:
- Dialog opens with current item values
- Changes save correctly
- Cancel discards changes
- Validation errors shown clearly
- URL links in notes are clickable

**Priority**: MVP

---

### PAR-013: YAML Persistence

**Title**: Load and save data as YAML files

**Description**: System shall:
- Load project data from RAID-Log-*.yaml or BRAID-Log-*.yaml files
- Load budget data from Budget-*.yaml files
- Save changes back to source files
- Handle date parsing with fallbacks

**Acceptance Criteria**:
- Files load without data loss
- Changes persist after save
- File format matches current v1 structure
- Graceful handling of missing optional fields

**Priority**: MVP

---

### PAR-014: Export - Markdown

**Title**: Export to Markdown format

**Description**: System shall export:
- Active items report (grouped by severity)
- Summary report (counts and budget)
- Table format (all items or filtered)

**Acceptance Criteria**:
- Markdown valid and renders correctly
- Reports include generation date
- Budget summary included if available

**Priority**: MVP

---

### PAR-015: Export - CSV

**Title**: Export to CSV format

**Description**: System shall export items to CSV with columns:
- Item #, Type, Workstream, Title, Description
- Assigned To, Start, Finish, Deadline
- % Complete, Indicator, Priority, Draft, Client Visible

**Acceptance Criteria**:
- CSV imports correctly into Excel
- Dates formatted as YYYY-MM-DD
- Special characters escaped properly

**Priority**: MVP

---

### PAR-016: Filtering

**Title**: Filter items by various criteria

**Description**: System shall support filtering by:
- Type
- Workstream
- Assignee
- Status/Indicator
- Open vs Completed
- Critical items only
- Search text

**Acceptance Criteria**:
- Filters apply correctly
- Multiple filters combine with AND
- Filter state persists during session
- Clear filters option available

**Priority**: MVP

---

### PAR-017: Help View

**Title**: In-app help documentation

**Description**: Help view shall display:
- User documentation
- Keyboard shortcuts
- Feature explanations
- Contact/feedback information

**Acceptance Criteria**:
- Help content is readable and accurate
- Navigation within help content
- Searchable or indexed

**Priority**: MVP

---

### PAR-018: Update Indicators Action

**Title**: Batch recalculate all indicators

**Description**: System shall provide action to:
- Recalculate indicators for all items
- Update indicators_updated timestamp
- Save changes to file

**Acceptance Criteria**:
- All items updated in one operation
- Timestamp reflects recalculation time
- Changes visible immediately in views

**Priority**: MVP

---

## WEB: Web Platform Requirements

These define the v1.5 web conversion requirements.

### WEB-001: Progressive Web App

**Title**: PWA with offline support

**Description**: Application shall be a Progressive Web App:
- Installable on desktop and mobile
- Service worker for offline capability
- App manifest with icons
- Works when network unavailable

**Acceptance Criteria**:
- Passes Lighthouse PWA audit
- Install prompt appears on supported browsers
- Basic functionality works offline
- Syncs when connection restored

**Priority**: MVP

---

### WEB-002: Responsive Design

**Title**: Responsive layout for all screen sizes

**Description**: Application shall adapt to:
- Desktop (1200px+)
- Tablet (768px - 1199px)
- Mobile (< 768px)

**Acceptance Criteria**:
- All views usable on all screen sizes
- Navigation adapts (sidebar collapses on mobile)
- Touch-friendly controls on mobile
- Tables scroll horizontally on narrow screens

**Priority**: MVP

---

### WEB-003: React Frontend

**Title**: React-based single-page application

**Description**: Frontend shall use:
- React 18 with TypeScript
- Vite build tool
- Tailwind CSS for styling
- shadcn/ui component library

**Acceptance Criteria**:
- Application builds without errors
- TypeScript strict mode enabled
- Component tests pass
- Build optimized for production

**Priority**: MVP

---

### WEB-004: FastAPI Backend

**Title**: Python FastAPI REST API

**Description**: Backend shall provide:
- RESTful API endpoints for all operations
- JSON request/response format
- JWT authentication
- Pydantic request validation

**Acceptance Criteria**:
- OpenAPI spec generated automatically
- All endpoints return consistent response format
- 400/401/403/404/500 errors handled properly
- Request validation with clear error messages

**Priority**: MVP

---

### WEB-005: PostgreSQL Database

**Title**: PostgreSQL for data persistence

**Description**: Application shall use:
- PostgreSQL for relational data storage
- Alembic for schema migrations
- Async database access (asyncpg)

**Acceptance Criteria**:
- Schema matches logical data model
- Migrations versioned and reversible
- Connection pooling configured
- Indexes on frequently queried columns

**Priority**: MVP

---

### WEB-006: Authentication

**Title**: User authentication

**Description**: Application shall support:
- Email/password registration and login
- OAuth (Google, Microsoft)
- JWT access tokens (short-lived)
- Refresh tokens (longer-lived)
- Password reset flow

**Acceptance Criteria**:
- Users can register with email
- OAuth login works for both providers
- Tokens refresh automatically
- Invalid tokens return 401
- Password reset email sends correctly

**Priority**: MVP

---

### WEB-007: API Error Handling

**Title**: Consistent API error responses

**Description**: All API errors shall return:
- Appropriate HTTP status code
- JSON body with: error code, message, details, correlation_id

**Acceptance Criteria**:
- 400: Validation errors with field-level details
- 401: Authentication required
- 403: Permission denied
- 404: Resource not found
- 500: Internal error (no sensitive details)

**Priority**: MVP

---

### WEB-008: Loading States

**Title**: Visual feedback during async operations

**Description**: Application shall show:
- Loading spinners during data fetch
- Skeleton screens for initial load
- Button loading states during submit
- Toast notifications for success/error

**Acceptance Criteria**:
- No blank screens during loading
- User knows when operation is in progress
- Errors display user-friendly messages
- Success confirmations appear briefly

**Priority**: MVP

---

## ENT: Enterprise Requirements

These define v2 multi-tenant, multi-user features.

### ENT-001: Organization Multi-Tenancy

**Title**: Database-per-organization isolation

**Description**: Each organization shall have:
- Separate database for complete isolation
- Organization-level settings and branding
- Admin-managed user access

**Acceptance Criteria**:
- Data never leaks between organizations
- Organization CRUD for super-admins
- Database provisioned on org creation
- Org deletion removes all data

**Priority**: MVP

---

### ENT-002: User Roles

**Title**: Role-based access control

**Description**: System shall support roles:
- **Admin**: Full access, user management
- **ProjectManager**: Create/edit projects, manage team members
- **TeamMember**: View/edit assigned items
- **Viewer**: Read-only access

**Acceptance Criteria**:
- Roles assigned per-project
- Permissions enforced on API endpoints
- UI hides/disables unauthorized actions
- Role inheritance (Admin has all PM permissions, etc.)

**Priority**: MVP

---

### ENT-003: Portfolio Grouping

**Title**: Flexible project grouping into portfolios

**Description**: Users shall be able to:
- Create portfolios as containers for projects
- Add/remove projects from portfolios
- View aggregated portfolio dashboards
- No rigid hierarchy (projects can be in multiple portfolios)

**Acceptance Criteria**:
- Portfolio CRUD operations work
- Portfolio dashboard aggregates project data
- Budget totals sum across projects
- Item counts aggregate correctly

**Priority**: MVP

---

### ENT-004: AI Chat Agent

**Title**: Natural language interface with Claude

**Description**: Users shall be able to:
- Chat with AI about project data
- Ask questions in natural language
- Get insights and summaries
- Default context: current project
- Expand scope by asking

**Acceptance Criteria**:
- Chat interface embedded in app
- Responses are contextually accurate
- AI can reference specific items by number
- Conversation history persisted
- RBAC respected (can only query accessible projects)

**Priority**: MVP

---

### ENT-005: File Attachments

**Title**: Attach files to items

**Description**: Users shall be able to:
- Upload files (images, documents) to items
- View attached files inline or download
- Delete attachments
- Storage in S3

**Acceptance Criteria**:
- Upload works for common file types
- Images display inline
- Documents downloadable
- File size limits enforced
- Virus scanning (optional, post-MVP)

**Priority**: Post-MVP

---

### ENT-006: SSO Integration

**Title**: Enterprise Single Sign-On

**Description**: Organizations shall be able to:
- Configure SAML or OIDC provider
- Auto-provision users on first login
- Enforce SSO-only authentication

**Acceptance Criteria**:
- SAML 2.0 and OIDC supported
- User attributes mapped from IdP
- Just-in-time provisioning works
- SSO can be required per-org

**Priority**: Post-MVP

---

### ENT-007: Global Search

**Title**: Full-text search across all data

**Description**: Users shall be able to:
- Search items, notes, attachments
- Filter search results
- Navigate directly to search results

**Acceptance Criteria**:
- Search returns results in < 500ms
- Highlights matching text
- Respects RBAC permissions
- Searches across accessible projects

**Priority**: Post-MVP

---

### ENT-008: Audit Logging

**Title**: Comprehensive audit trail

**Description**: System shall log:
- All data modifications (create, update, delete)
- User actions (login, logout, permission changes)
- Actor, timestamp, before/after values

**Acceptance Criteria**:
- Audit logs immutable
- Queryable by admin
- Retention policy configurable
- No PII in logs

**Priority**: MVP

---

### ENT-009: Multi-User Collaboration

**Title**: Real-time or near-real-time collaboration

**Description**: Multiple users shall be able to:
- View same project simultaneously
- See recent changes by others
- Avoid overwriting each other's edits

**Acceptance Criteria**:
- Changes visible within 30 seconds
- Edit conflicts detected and handled
- User presence indicators (optional)

**Priority**: Post-MVP

---

## Summary

| Category | Count | MVP | Post-MVP |
|----------|-------|-----|----------|
| PAR (Parity) | 18 | 18 | 0 |
| WEB (Web Platform) | 8 | 8 | 0 |
| ENT (Enterprise) | 9 | 5 | 4 |
| **Total** | **35** | **31** | **4** |

---

## Traceability

All requirements will be traced to:
- User stories in USER_STORIES.md
- Implementation sequences in docs/implementation/
- Test cases in tests/

See USER_STORIES.md for story-to-requirement mapping.

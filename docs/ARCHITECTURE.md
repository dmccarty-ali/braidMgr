# braidMgr Architecture

*Last updated: 2024-12-24*

This document describes the system architecture for braidMgr v2, a multi-tenant, multi-user RAID log management application with AI chat capabilities.

---

## Table of Contents

1. [Design Principles](#1-design-principles)
2. [System Overview](#2-system-overview)
3. [Technology Stack](#3-technology-stack)
4. [Project Structure](#4-project-structure)
5. [Service Architecture](#5-service-architecture)
6. [API Design](#6-api-design)
7. [Database Architecture](#7-database-architecture)
8. [Authentication & Authorization](#8-authentication--authorization)
9. [AI Integration](#9-ai-integration)
10. [Frontend Architecture](#10-frontend-architecture)
11. [Deployment Architecture](#11-deployment-architecture)

---

## 1. Design Principles

### 1.1 Service Centralization

All external service access MUST go through centralized service modules.

**Benefits**:
- Single place to modify connection logic, credentials, retry policies
- Consistent error handling and logging
- Testable via dependency injection
- Audit trail for all external calls

**Pattern**:
```python
# Correct - use service registry
from src.services import services
result = await services.aurora.execute_query(...)

# Incorrect - direct access
import asyncpg
conn = await asyncpg.connect(...)  # DON'T DO THIS
```

### 1.2 Fail Fast

Validate all configuration and connections at startup. Don't wait for first request to discover problems.

### 1.3 Audit Everything

All data changes logged with actor, timestamp, before/after state. No exceptions.

### 1.4 Defense in Depth

- Validate at API boundary (Pydantic schemas)
- Validate at service layer (business rules)
- Validate at database (constraints)

### 1.5 Clean Separation

- **Core**: Pure business logic, no I/O dependencies
- **Services**: External integrations (DB, S3, Claude)
- **API**: HTTP layer, request/response handling
- **UI**: Presentation only, no business logic

---

## 2. System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        Cloudflare CDN                            │
│                    (Static assets, WAF)                          │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                         AWS CloudFront                           │
│                      (API Gateway, SSL)                          │
└─────────────────────────────────────────────────────────────────┘
                                │
                    ┌───────────┴───────────┐
                    ▼                       ▼
        ┌───────────────────┐   ┌───────────────────┐
        │   React Frontend   │   │   FastAPI Backend  │
        │   (Vite, PWA)      │   │   (ECS Fargate)    │
        └───────────────────┘   └───────────────────┘
                                        │
                    ┌───────────────────┼───────────────────┐
                    ▼                   ▼                   ▼
        ┌───────────────────┐ ┌───────────────────┐ ┌───────────────────┐
        │  Aurora PostgreSQL │ │    Amazon S3      │ │   Claude API      │
        │   (Multi-DB)       │ │  (Attachments)    │ │   (Anthropic)     │
        └───────────────────┘ └───────────────────┘ └───────────────────┘
```

---

## 3. Technology Stack

### 3.1 Frontend

| Component | Technology | Version | Purpose |
|-----------|------------|---------|---------|
| Framework | React | 18.x | UI components |
| Build | Vite | 5.x | Fast bundler, HMR |
| Language | TypeScript | 5.x | Type safety |
| Styling | Tailwind CSS | 3.x | Utility-first CSS |
| Components | shadcn/ui | latest | Accessible components |
| State | React Query | 5.x | Server state management |
| State (UI) | Zustand | 4.x | Client state |
| PWA | vite-plugin-pwa | 0.x | Service worker, manifest |
| Testing | Vitest | 1.x | Unit tests |
| Testing | Playwright | 1.x | E2E tests |
| Linting | ESLint | 8.x | Code quality |
| Formatting | Prettier | 3.x | Code formatting |

### 3.2 Backend

| Component | Technology | Version | Purpose |
|-----------|------------|---------|---------|
| Framework | FastAPI | 0.110+ | Async web framework |
| Language | Python | 3.11+ | Runtime |
| Validation | Pydantic | 2.x | Request/response validation |
| ORM | None | - | Raw SQL with asyncpg |
| Database | asyncpg | 0.29+ | Async PostgreSQL driver |
| Auth | python-jose | 3.x | JWT handling |
| Auth | passlib | 1.7+ | Password hashing |
| Logging | structlog | 24.x | Structured logging |
| Testing | pytest | 8.x | Test framework |
| Testing | pytest-asyncio | 0.23+ | Async test support |
| HTTP Client | httpx | 0.27+ | Async HTTP client |

### 3.3 Database

| Component | Technology | Purpose |
|-----------|------------|---------|
| Database | Aurora PostgreSQL 15 | Primary data store |
| Migration | Alembic | Schema versioning |
| Pooling | Aurora connection pooling | Connection management |

### 3.4 Cloud Services (AWS)

| Service | Purpose |
|---------|---------|
| ECS Fargate | Container hosting |
| Aurora PostgreSQL | Database |
| S3 | File storage |
| CloudFront | CDN, API gateway |
| Secrets Manager | Credentials storage |
| CloudWatch | Logging, metrics |
| ECR | Container registry |

### 3.5 External Services

| Service | Purpose |
|---------|---------|
| Claude API (Anthropic) | AI chat capabilities |
| Cloudflare | DNS, WAF, static hosting |

---

## 4. Project Structure

```
braidMgr/
├── docs/                          # Documentation
│   ├── REQUIREMENTS.md
│   ├── USER_STORIES.md
│   ├── DATA_MODEL.md
│   ├── ARCHITECTURE.md
│   ├── PATTERNS.md
│   ├── PROCESS_FLOWS.md
│   ├── STATUS.yaml
│   ├── backlog.md
│   └── implementation/
│       └── SEQUENCE_NN.md
│
├── backend/                       # FastAPI backend
│   ├── src/
│   │   ├── api/                   # API layer
│   │   │   ├── __init__.py
│   │   │   ├── main.py            # FastAPI app
│   │   │   ├── middleware/        # Middleware stack
│   │   │   │   ├── auth.py
│   │   │   │   ├── correlation.py
│   │   │   │   ├── error_handler.py
│   │   │   │   └── request_logging.py
│   │   │   ├── routes/            # API endpoints
│   │   │   │   ├── auth.py
│   │   │   │   ├── projects.py
│   │   │   │   ├── items.py
│   │   │   │   ├── budget.py
│   │   │   │   └── chat.py
│   │   │   └── schemas/           # Pydantic models
│   │   │       ├── auth.py
│   │   │       ├── project.py
│   │   │       ├── item.py
│   │   │       └── chat.py
│   │   │
│   │   ├── core/                  # Business logic
│   │   │   ├── __init__.py
│   │   │   ├── indicators.py      # Status calculation
│   │   │   ├── budget.py          # Budget calculations
│   │   │   └── permissions.py     # RBAC logic
│   │   │
│   │   ├── domain/                # Domain models
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── project.py
│   │   │   ├── item.py
│   │   │   └── chat.py
│   │   │
│   │   ├── repositories/          # Data access
│   │   │   ├── __init__.py
│   │   │   ├── base.py
│   │   │   ├── user_repository.py
│   │   │   ├── project_repository.py
│   │   │   └── item_repository.py
│   │   │
│   │   ├── services/              # External services
│   │   │   ├── __init__.py        # ServiceRegistry
│   │   │   ├── base.py            # BaseService
│   │   │   ├── aurora_service.py
│   │   │   ├── s3_service.py
│   │   │   └── claude_service.py
│   │   │
│   │   └── utils/                 # Utilities
│   │       ├── __init__.py
│   │       ├── config.py
│   │       ├── exceptions.py
│   │       └── logging.py
│   │
│   ├── tests/
│   │   ├── conftest.py
│   │   ├── unit/
│   │   ├── integration/
│   │   └── e2e/
│   │
│   ├── alembic/                   # Migrations
│   │   ├── versions/
│   │   └── env.py
│   │
│   ├── pyproject.toml
│   └── requirements.txt
│
├── frontend/                      # React frontend
│   ├── src/
│   │   ├── components/            # Reusable components
│   │   │   ├── ui/                # shadcn/ui components
│   │   │   ├── layout/            # Layout components
│   │   │   └── features/          # Feature components
│   │   │
│   │   ├── pages/                 # Page components
│   │   │   ├── Dashboard.tsx
│   │   │   ├── Items.tsx
│   │   │   ├── Timeline.tsx
│   │   │   ├── Budget.tsx
│   │   │   └── Chat.tsx
│   │   │
│   │   ├── hooks/                 # Custom hooks
│   │   │   ├── useAuth.ts
│   │   │   ├── useProjects.ts
│   │   │   └── useItems.ts
│   │   │
│   │   ├── lib/                   # Utilities
│   │   │   ├── api.ts             # API client
│   │   │   ├── auth.ts            # Auth utilities
│   │   │   └── utils.ts
│   │   │
│   │   ├── stores/                # Zustand stores
│   │   │   └── uiStore.ts
│   │   │
│   │   ├── types/                 # TypeScript types
│   │   │   ├── api.ts
│   │   │   ├── project.ts
│   │   │   └── item.ts
│   │   │
│   │   ├── App.tsx
│   │   └── main.tsx
│   │
│   ├── public/
│   ├── index.html
│   ├── package.json
│   ├── tailwind.config.js
│   ├── tsconfig.json
│   └── vite.config.ts
│
├── docker-compose.yml             # Local development
├── Dockerfile.backend
├── Dockerfile.frontend
└── config.yaml                    # Configuration
```

---

## 5. Service Architecture

### 5.1 Service Registry

```python
# src/services/__init__.py

class ServiceRegistry:
    """Singleton registry for all external services."""

    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def initialize(self, config: AppConfig) -> None:
        """Initialize all services at startup."""
        if self._initialized:
            return

        self._aurora = AuroraService(config.database)
        self._s3 = S3Service(config.s3)
        self._claude = ClaudeService(config.claude)

        # Validate connections (fail fast)
        self._validate_connections()
        self._initialized = True

    @property
    def aurora(self) -> AuroraService:
        return self._aurora

    @property
    def s3(self) -> S3Service:
        return self._s3

    @property
    def claude(self) -> ClaudeService:
        return self._claude

# Singleton instance
services = ServiceRegistry()
```

### 5.2 Service Inventory

| Service | Purpose | Methods |
|---------|---------|---------|
| AuroraService | Database operations | execute_query, execute_one, execute_returning, transaction |
| S3Service | File storage | upload, download, delete, generate_presigned_url |
| ClaudeService | AI chat | send_message, stream_response |
| AuthService | Authentication | verify_token, create_tokens, hash_password |

---

## 6. API Design

### 6.1 Base URL Structure

```
Production: https://api.braidmgr.com/v1
Development: http://localhost:8000/v1
```

### 6.2 Authentication

All endpoints except `/auth/*` require JWT bearer token:

```
Authorization: Bearer <access_token>
```

### 6.3 Endpoint Groups

| Path | Purpose |
|------|---------|
| `/health` | Health check |
| `/auth/*` | Authentication (login, register, refresh) |
| `/users/*` | User management |
| `/orgs/*` | Organization management |
| `/projects/*` | Project CRUD |
| `/projects/{id}/items/*` | Item CRUD |
| `/projects/{id}/budget/*` | Budget operations |
| `/chat/*` | AI chat sessions |
| `/export/*` | Export operations |

### 6.4 Response Format

**Success**:
```json
{
    "data": { ... },
    "meta": {
        "page": 1,
        "per_page": 20,
        "total": 100
    }
}
```

**Error**:
```json
{
    "error": "VALIDATION_ERROR",
    "message": "Invalid input",
    "details": {
        "field": "email",
        "reason": "Invalid email format"
    },
    "correlation_id": "abc-123"
}
```

---

## 7. Database Architecture

### 7.1 Multi-Tenancy

**Strategy**: Database-per-organization

```
Central Database: braidmgr_central
├── users
├── organizations
├── user_org_memberships
└── audit_log

Org Database: braidmgr_org_{slug}
├── projects
├── items
├── ... (all org-specific tables)
└── audit_log
```

### 7.2 Connection Routing

```python
async def get_org_connection(org_id: UUID) -> asyncpg.Pool:
    """Get database connection for organization."""
    org = await central_db.get_org(org_id)
    return await get_pool(org.database_name)
```

### 7.3 Indexes

Key indexes for performance:
- `idx_item_project` - Item queries by project
- `idx_item_indicator` - Dashboard counts by status
- `idx_item_assigned` - Items by assignee
- `idx_timesheet_week` - Budget calculations

See DATA_MODEL.md for complete index definitions.

---

## 8. Authentication & Authorization

### 8.1 Authentication Flow

```
1. User submits credentials (email/password or OAuth)
2. Backend verifies credentials
3. Backend issues:
   - Access token (JWT, 15 min expiry)
   - Refresh token (opaque, 7 day expiry)
4. Frontend stores tokens securely
5. Frontend includes access token in requests
6. Backend validates token on each request
7. Frontend refreshes access token before expiry
```

### 8.2 JWT Structure

```json
{
    "sub": "user-uuid",
    "email": "user@example.com",
    "org_id": "org-uuid",
    "org_role": "admin",
    "iat": 1703419200,
    "exp": 1703420100
}
```

### 8.3 RBAC

**Organization Roles**:
- `owner`: Full org control, billing
- `admin`: User management, settings
- `member`: Standard access

**Project Roles**:
- `admin`: Full project control
- `project_manager`: Create/edit items and settings
- `team_member`: Edit assigned items
- `viewer`: Read-only

### 8.4 Permission Checks

```python
async def check_permission(
    user_id: UUID,
    project_id: UUID,
    action: str
) -> bool:
    """Check if user can perform action on project."""
    role = await get_user_project_role(user_id, project_id)
    return PERMISSIONS[role].get(action, False)
```

---

## 9. AI Integration

### 9.1 Claude Service

```python
class ClaudeService:
    """Integration with Claude API."""

    def __init__(self, config: ClaudeConfig):
        self.client = anthropic.Anthropic(api_key=config.api_key)
        self.model = "claude-sonnet-4-20250514"

    async def send_message(
        self,
        messages: list[dict],
        context: ProjectContext
    ) -> str:
        """Send message with project context."""
        system_prompt = self._build_system_prompt(context)

        response = await self.client.messages.create(
            model=self.model,
            system=system_prompt,
            messages=messages,
            max_tokens=4096
        )

        return response.content[0].text
```

### 9.2 Context Building

```python
def build_project_context(project_id: UUID) -> ProjectContext:
    """Build context from project data for AI."""
    project = await project_repo.get(project_id)
    items = await item_repo.get_by_project(project_id)
    budget = await budget_service.calculate(project_id)

    return ProjectContext(
        project=project,
        items=items,
        budget_metrics=budget,
        # Formatted for AI consumption
        summary=format_for_ai(project, items, budget)
    )
```

### 9.3 RBAC Enforcement

AI only sees data the user has permission to access:
- Default scope: current project
- Expanded scope: all user's accessible projects
- Never cross-org data

---

## 10. Frontend Architecture

### 10.1 State Management

| Type | Tool | Purpose |
|------|------|---------|
| Server state | React Query | API data, caching, sync |
| UI state | Zustand | Sidebar, modals, filters |
| Form state | React Hook Form | Form validation |

### 10.2 Data Fetching

```typescript
// hooks/useItems.ts
export function useItems(projectId: string) {
    return useQuery({
        queryKey: ['projects', projectId, 'items'],
        queryFn: () => api.getItems(projectId),
        staleTime: 1000 * 60 * 5, // 5 minutes
    });
}
```

### 10.3 Component Structure

```
components/
├── ui/                    # shadcn/ui primitives
│   ├── button.tsx
│   ├── card.tsx
│   └── ...
├── layout/                # Layout components
│   ├── Sidebar.tsx
│   ├── Header.tsx
│   └── MainLayout.tsx
└── features/              # Feature components
    ├── items/
    │   ├── ItemTable.tsx
    │   ├── ItemCard.tsx
    │   └── EditItemDialog.tsx
    ├── budget/
    │   ├── BudgetMetrics.tsx
    │   └── BurnChart.tsx
    └── chat/
        ├── ChatPanel.tsx
        └── MessageList.tsx
```

---

## 11. Deployment Architecture

### 11.1 Environments

| Environment | Purpose | URL |
|-------------|---------|-----|
| Development | Local dev | localhost:3000, localhost:8000 |
| Staging | Pre-production testing | staging.braidmgr.com |
| Production | Live system | app.braidmgr.com |

### 11.2 AWS Infrastructure

```
┌─────────────────────────────────────────────────────────────────┐
│                           VPC                                    │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │                    Public Subnet                            │ │
│  │  ┌──────────────┐  ┌──────────────┐                        │ │
│  │  │    ALB       │  │  CloudFront  │                        │ │
│  │  └──────────────┘  └──────────────┘                        │ │
│  └────────────────────────────────────────────────────────────┘ │
│                              │                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │                   Private Subnet                            │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │ │
│  │  │ ECS Fargate  │  │ ECS Fargate  │  │ ECS Fargate  │     │ │
│  │  │  (API x2)    │  │  (API x2)    │  │  (API x2)    │     │ │
│  │  └──────────────┘  └──────────────┘  └──────────────┘     │ │
│  └────────────────────────────────────────────────────────────┘ │
│                              │                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │                  Database Subnet                            │ │
│  │  ┌──────────────────────────────────────────────────────┐  │ │
│  │  │              Aurora PostgreSQL Cluster                │  │ │
│  │  │  ┌─────────────┐        ┌─────────────┐              │  │ │
│  │  │  │   Writer    │        │   Reader    │              │  │ │
│  │  │  └─────────────┘        └─────────────┘              │  │ │
│  │  └──────────────────────────────────────────────────────┘  │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘

External:
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│     S3       │  │   Secrets    │  │  CloudWatch  │
│ (Attachments)│  │   Manager    │  │   (Logs)     │
└──────────────┘  └──────────────┘  └──────────────┘
```

### 11.3 Scaling

- **API**: Auto-scale ECS tasks based on CPU/memory
- **Database**: Aurora auto-scaling read replicas
- **Frontend**: Static files on CloudFront (global edge)

---

## Related Documentation

| Document | Purpose |
|----------|---------|
| [REQUIREMENTS.md](REQUIREMENTS.md) | Business requirements |
| [USER_STORIES.md](USER_STORIES.md) | Implementation stories |
| [DATA_MODEL.md](DATA_MODEL.md) | Database schema |
| [PATTERNS.md](PATTERNS.md) | Code patterns |
| [PROCESS_FLOWS.md](PROCESS_FLOWS.md) | State machines |

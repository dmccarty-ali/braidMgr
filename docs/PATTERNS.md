# braidMgr Implementation Patterns

*Last updated: 2024-12-24*

This document contains code patterns and templates that MUST be applied when implementing features. Patterns are carried forward into implementation sequence docs.

---

## 1. Error Handling

### 1.1 Exception Hierarchy

All exceptions inherit from AppError. Use these instead of raw HTTPException:

```python
# src/utils/exceptions.py

class AppError(Exception):
    """Base application error."""
    status_code: int = 500
    error_code: str = "INTERNAL_ERROR"

    def __init__(
        self,
        message: str,
        details: dict = None,
        **kwargs
    ):
        self.message = message
        self.details = details or {}
        self.details.update(kwargs)
        super().__init__(message)


class ValidationError(AppError):
    """400 - Input validation failed."""
    status_code = 400
    error_code = "VALIDATION_ERROR"


class AuthenticationError(AppError):
    """401 - Not authenticated."""
    status_code = 401
    error_code = "AUTHENTICATION_ERROR"


class AuthorizationError(AppError):
    """403 - No permission."""
    status_code = 403
    error_code = "AUTHORIZATION_ERROR"


class NotFoundError(AppError):
    """404 - Resource not found."""
    status_code = 404
    error_code = "NOT_FOUND"

    def __init__(self, resource: str, identifier: str):
        super().__init__(
            f"{resource} not found",
            resource=resource,
            identifier=identifier
        )


class ConflictError(AppError):
    """409 - Duplicate or state conflict."""
    status_code = 409
    error_code = "CONFLICT"


class WorkflowError(AppError):
    """422 - Invalid state transition."""
    status_code = 422
    error_code = "WORKFLOW_ERROR"


class DatabaseError(AppError):
    """500 - Database operation failed."""
    status_code = 500
    error_code = "DATABASE_ERROR"


class ExternalServiceError(AppError):
    """502 - External API failed."""
    status_code = 502
    error_code = "EXTERNAL_SERVICE_ERROR"


class ServiceUnavailableError(AppError):
    """503 - Service temporarily unavailable."""
    status_code = 503
    error_code = "SERVICE_UNAVAILABLE"
```

### 1.2 Error Logging Pattern

**ALWAYS log errors with context before raising:**

```python
import structlog

logger = structlog.get_logger()

async def some_operation(resource_id: UUID, user_id: UUID):
    # Bind context for all logs in this operation
    log = logger.bind(resource_id=str(resource_id), user_id=str(user_id))

    try:
        result = await do_something(resource_id)
        log.info("operation_completed", result_count=len(result))
        return result
    except SpecificDatabaseError as e:
        log.error(
            "operation_failed",
            error_type=type(e).__name__,
            error_message=str(e),
            # NEVER log PII: passwords, tokens, SSN, etc.
        )
        raise DatabaseError(
            "Failed to complete operation",
            operation="some_operation",
            details={"resource_id": str(resource_id)}
        )
    except Exception as e:
        log.exception("unexpected_error")  # Includes stack trace
        raise
```

### 1.3 Database Error Mapping

```python
import asyncpg

async def execute_with_error_handling(query: str, *args):
    try:
        return await self._pool.fetch(query, *args)
    except asyncpg.UniqueViolationError as e:
        raise ConflictError(
            "Resource already exists",
            field=e.constraint_name,
        )
    except asyncpg.ForeignKeyViolationError as e:
        raise ValidationError(
            "Referenced resource not found",
            field=e.constraint_name,
        )
    except asyncpg.CheckViolationError as e:
        raise ValidationError(
            "Value out of allowed range",
            field=e.constraint_name,
        )
    except asyncpg.PostgresConnectionError as e:
        logger.critical("database_connection_failed", error=str(e))
        raise ServiceUnavailableError("Database temporarily unavailable")
```

---

## 2. Logging

### 2.1 Logging Setup

```python
# src/utils/logging.py
import logging
import structlog

def setup_logging(environment: str, log_level: str = "INFO"):
    """Configure structured logging."""

    logging.basicConfig(level=getattr(logging, log_level))

    processors = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]

    if environment == "production":
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.append(structlog.dev.ConsoleRenderer(colors=True))

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(logging, log_level)
        ),
        context_class=dict,
        cache_logger_on_first_use=True,
    )
```

### 2.2 Correlation ID Middleware

```python
# src/api/middleware/correlation.py
import uuid
import structlog
from contextvars import ContextVar
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

correlation_id_var: ContextVar[str] = ContextVar("correlation_id", default="")

class CorrelationIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Get from header or generate new
        correlation_id = request.headers.get(
            "X-Correlation-ID",
            str(uuid.uuid4())
        )
        correlation_id_var.set(correlation_id)

        # Bind to structlog context
        structlog.contextvars.bind_contextvars(correlation_id=correlation_id)

        # Store on request for error handlers
        request.state.correlation_id = correlation_id

        response = await call_next(request)
        response.headers["X-Correlation-ID"] = correlation_id

        return response
```

### 2.3 Log Levels by Layer

| Layer | Default Level | What to Log |
|-------|---------------|-------------|
| API | INFO | Request received, response sent, status codes |
| Middleware | INFO | Auth success/failure, rate limit hits |
| Core | INFO | Business events, state transitions |
| Repository | DEBUG | Query execution (no sensitive data) |
| Service | DEBUG | External API calls, retries, timeouts |

### 2.4 Sensitive Data - NEVER Log

- Passwords or password hashes
- JWT tokens or API keys
- Full credit card numbers
- Social Security Numbers
- Personal health information

---

## 3. API Middleware Stack

### 3.1 Error Handler Middleware

```python
# src/api/middleware/error_handler.py
from fastapi import Request
from fastapi.responses import JSONResponse
from src.utils.exceptions import AppError
import structlog

logger = structlog.get_logger()

async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    """Convert application errors to consistent JSON responses."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.error_code,
            "message": exc.message,
            "details": exc.details,
            "correlation_id": getattr(request.state, "correlation_id", None),
        }
    )

async def unhandled_error_handler(request: Request, exc: Exception) -> JSONResponse:
    """Catch-all for unexpected errors."""
    correlation_id = getattr(request.state, "correlation_id", "unknown")
    logger.exception(
        "unhandled_error",
        correlation_id=correlation_id,
        path=request.url.path,
    )
    return JSONResponse(
        status_code=500,
        content={
            "error": "INTERNAL_ERROR",
            "message": "An unexpected error occurred",
            "correlation_id": correlation_id,
        }
    )
```

### 3.2 Request Logging Middleware

```python
# src/api/middleware/request_logging.py
import time
import structlog
from starlette.middleware.base import BaseHTTPMiddleware

logger = structlog.get_logger()

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        start_time = time.perf_counter()

        logger.info(
            "request_started",
            method=request.method,
            path=request.url.path,
            query=str(request.query_params),
        )

        response = await call_next(request)

        duration_ms = (time.perf_counter() - start_time) * 1000
        logger.info(
            "request_completed",
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            duration_ms=round(duration_ms, 2),
        )

        return response
```

---

## 4. Service Centralization

### 4.1 Service Registry

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

        self._validate_connections()
        self._initialized = True

    @property
    def aurora(self) -> AuroraService:
        self._ensure_initialized()
        return self._aurora

    @property
    def s3(self) -> S3Service:
        self._ensure_initialized()
        return self._s3

    @property
    def claude(self) -> ClaudeService:
        self._ensure_initialized()
        return self._claude

    def _ensure_initialized(self) -> None:
        if not self._initialized:
            raise RuntimeError(
                "ServiceRegistry not initialized. "
                "Call services.initialize(config) at startup."
            )

    def _validate_connections(self) -> None:
        """Verify all services are reachable."""
        # Each service implements health_check()
        pass

# Singleton instance
services = ServiceRegistry()
```

### 4.2 Base Service

```python
# src/services/base.py
from abc import ABC, abstractmethod
import structlog

class BaseService(ABC):
    """Base class for all services."""

    def __init__(self, config):
        self.config = config
        self.logger = structlog.get_logger().bind(service=self.__class__.__name__)

    @abstractmethod
    async def health_check(self) -> bool:
        """Check service health."""
        pass
```

---

## 5. Repository Pattern

### 5.1 Base Repository

```python
# src/repositories/base.py
from typing import TypeVar, Generic, Optional
from uuid import UUID
import structlog

T = TypeVar('T')

class BaseRepository(Generic[T]):
    """Base repository with common CRUD operations."""

    def __init__(self, aurora_service, table_name: str):
        self._aurora = aurora_service
        self._table_name = table_name
        self._logger = structlog.get_logger().bind(repository=self.__class__.__name__)

    async def find_by_id(self, id: UUID) -> Optional[T]:
        """Find entity by ID."""
        log = self._logger.bind(id=str(id))

        try:
            query = f"""
                SELECT * FROM {self._table_name}
                WHERE id = $1 AND deleted_at IS NULL
            """
            row = await self._aurora.execute_one(query, id)

            if row:
                log.debug("entity_found")
            else:
                log.debug("entity_not_found")

            return self._row_to_entity(row) if row else None

        except Exception as e:
            log.error("find_by_id_failed", error=str(e))
            raise DatabaseError(
                f"Failed to find {self._table_name}",
                operation="find_by_id",
                table=self._table_name,
            )

    async def soft_delete(self, id: UUID) -> bool:
        """Soft delete by setting deleted_at."""
        query = f"""
            UPDATE {self._table_name}
            SET deleted_at = NOW()
            WHERE id = $1 AND deleted_at IS NULL
            RETURNING id
        """
        result = await self._aurora.execute_one(query, id)
        return result is not None

    @abstractmethod
    def _row_to_entity(self, row: dict) -> T:
        """Convert database row to entity."""
        pass
```

---

## 6. Testing Patterns

### 6.1 Test Distribution

| Type | Target % | Description |
|------|----------|-------------|
| Unit | 80% | Fast, no I/O, mocked dependencies |
| Integration | 15% | Real PostgreSQL (Docker), mock external services |
| E2E | 5% | Full HTTP stack with real database |

### 6.2 Test Structure

```
tests/
├── conftest.py                    # Global fixtures
├── unit/
│   ├── test_indicators.py
│   ├── test_budget.py
│   └── middleware/
│       ├── test_auth.py
│       └── test_error_handler.py
├── integration/
│   ├── conftest.py                # DB fixtures
│   └── repositories/
│       ├── test_project_repository.py
│       └── test_item_repository.py
└── e2e/
    ├── conftest.py                # API client fixtures
    └── test_items_api.py
```

### 6.3 Key Fixtures

```python
# tests/conftest.py
import pytest
from unittest.mock import AsyncMock, MagicMock

@pytest.fixture
def mock_aurora():
    """Mock Aurora service for unit tests."""
    aurora = MagicMock()
    aurora.execute_query = AsyncMock(return_value=[])
    aurora.execute_one = AsyncMock(return_value=None)
    aurora.execute_returning = AsyncMock(return_value={})
    return aurora

@pytest.fixture
def sample_project_data():
    """Sample project data for tests."""
    return {
        "id": uuid4(),
        "name": "Test Project",
        "client_name": "Test Client",
        "project_start": date(2025, 1, 1),
        "project_end": date(2025, 12, 31),
    }
```

### 6.4 Unit Test Template

```python
import pytest
from unittest.mock import AsyncMock

@pytest.mark.asyncio
async def test_create_item_success(mock_aurora, sample_item_data):
    # Arrange
    mock_aurora.execute_returning.return_value = sample_item_data
    repo = ItemRepository(mock_aurora)

    # Act
    result = await repo.create(Item(**sample_item_data))

    # Assert
    assert result.title == sample_item_data["title"]
    mock_aurora.execute_returning.assert_called_once()
```

### 6.5 Integration Test Template

```python
import pytest

@pytest.mark.asyncio
async def test_item_crud(test_db):
    """Test complete item lifecycle."""
    repo = ItemRepository(test_db)

    # Create
    item = await repo.create(Item(title="Test Item", type="Action Item"))
    assert item.id is not None

    # Read
    found = await repo.find_by_id(item.id)
    assert found.title == "Test Item"

    # Update
    found.title = "Updated Title"
    updated = await repo.update(found)
    assert updated.title == "Updated Title"

    # Delete
    await repo.soft_delete(item.id)
    assert await repo.find_by_id(item.id) is None
```

---

## 7. Async Patterns

### 7.1 Parallel Operations

```python
import asyncio

async def load_project_context(project_id: UUID) -> ProjectContext:
    """Load all project data in parallel."""
    project, items, budget = await asyncio.gather(
        project_repo.find_by_id(project_id),
        item_repo.find_by_project(project_id),
        budget_service.calculate(project_id),
    )
    return ProjectContext(project, items, budget)
```

### 7.2 Transaction Boundaries

```python
async def create_item_with_notes(data: ItemCreate) -> Item:
    """
    Transaction scope: item + initial note.
    Side effects happen AFTER commit.
    """
    async with aurora.transaction() as conn:
        # All writes in same transaction
        item = await conn.execute_returning(...)
        await conn.execute(...)  # note

    # Transaction committed

    # Side effects after commit
    await notify_assignee(item.assigned_to, item)

    return item
```

---

## 8. Pydantic Validation

### 8.1 Request Schemas

```python
# src/api/schemas/item.py
from pydantic import BaseModel, Field, field_validator
from datetime import date
from typing import Optional
from uuid import UUID

class ItemCreate(BaseModel):
    """Request body for creating an item."""
    type: str = Field(..., description="Item type")
    title: str = Field(..., min_length=1, max_length=500)
    description: Optional[str] = Field(None, max_length=10000)
    workstream_id: Optional[UUID] = None
    assigned_to: Optional[str] = Field(None, max_length=255)
    start_date: Optional[date] = None
    finish_date: Optional[date] = None
    deadline: Optional[date] = None
    percent_complete: int = Field(default=0, ge=0, le=100)

    @field_validator('type')
    @classmethod
    def validate_type(cls, v):
        allowed = ['Budget', 'Risk', 'Action Item', 'Issue',
                   'Decision', 'Deliverable', 'Plan Item']
        if v not in allowed:
            raise ValueError(f'type must be one of {allowed}')
        return v

    @field_validator('finish_date')
    @classmethod
    def validate_finish_after_start(cls, v, info):
        start = info.data.get('start_date')
        if start and v and v < start:
            raise ValueError('finish_date must be after start_date')
        return v
```

### 8.2 Response Schemas

```python
class ItemResponse(BaseModel):
    """Item in response."""
    id: UUID
    item_num: int
    type: str
    title: str
    indicator: Optional[str] = None
    percent_complete: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
```

---

## 9. React Component Patterns

### 9.1 Data Fetching Hook

```typescript
// hooks/useItems.ts
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '@/lib/api';

export function useItems(projectId: string) {
    return useQuery({
        queryKey: ['projects', projectId, 'items'],
        queryFn: () => api.getItems(projectId),
        staleTime: 1000 * 60 * 5,
    });
}

export function useCreateItem(projectId: string) {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: (data: ItemCreate) => api.createItem(projectId, data),
        onSuccess: () => {
            queryClient.invalidateQueries({
                queryKey: ['projects', projectId, 'items']
            });
        },
    });
}
```

### 9.2 Component Structure

```typescript
// components/features/items/ItemCard.tsx
import { Card, CardHeader, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Item } from '@/types/item';

interface ItemCardProps {
    item: Item;
    onEdit: (item: Item) => void;
}

export function ItemCard({ item, onEdit }: ItemCardProps) {
    return (
        <Card
            className="cursor-pointer hover:shadow-md transition-shadow"
            onClick={() => onEdit(item)}
        >
            <CardHeader className="flex flex-row items-center justify-between">
                <span className="font-medium">#{item.item_num}</span>
                <Badge variant={getVariantForIndicator(item.indicator)}>
                    {item.indicator}
                </Badge>
            </CardHeader>
            <CardContent>
                <h3 className="font-semibold">{item.title}</h3>
                {item.assigned_to && (
                    <p className="text-sm text-muted-foreground">
                        {item.assigned_to}
                    </p>
                )}
            </CardContent>
        </Card>
    );
}
```

---

## 10. Checklist

Before marking any feature complete, verify:

- [ ] All database operations wrapped in try/catch
- [ ] Errors logged with context (operation, parameters, error type)
- [ ] Custom exceptions used (not raw HTTPException)
- [ ] Correlation ID flows through all logs
- [ ] No PII in log messages
- [ ] Unit tests exist for business logic
- [ ] Integration tests exist for repositories
- [ ] Pydantic schemas validate all inputs
- [ ] API returns consistent error format

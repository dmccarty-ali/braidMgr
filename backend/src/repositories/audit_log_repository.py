"""
Audit Log Repository.

Handles reading and writing audit log entries for activity tracking.

The audit_log table stores:
- User actions (who did what)
- Entity changes (before/after state)
- Timestamps for chronological ordering
"""

from datetime import datetime, timedelta
from typing import Optional, Any
from uuid import UUID

from src.services.aurora_service import AuroraService
from src.utils.logging import get_logger

logger = get_logger(__name__)


# =============================================================================
# Data Classes
# =============================================================================


class AuditEntry:
    """Represents a single audit log entry."""

    def __init__(
        self,
        id: UUID,
        user_id: Optional[UUID],
        action: str,
        entity_type: str,
        entity_id: Optional[UUID],
        before_state: Optional[dict],
        after_state: Optional[dict],
        correlation_id: Optional[str],
        created_at: datetime,
        # Joined fields
        user_name: Optional[str] = None,
        user_email: Optional[str] = None,
    ):
        self.id = id
        self.user_id = user_id
        self.action = action
        self.entity_type = entity_type
        self.entity_id = entity_id
        self.before_state = before_state
        self.after_state = after_state
        self.correlation_id = correlation_id
        self.created_at = created_at
        self.user_name = user_name
        self.user_email = user_email

    def to_dict(self) -> dict:
        """Convert to dictionary for API response."""
        return {
            "id": str(self.id),
            "user_id": str(self.user_id) if self.user_id else None,
            "user_name": self.user_name,
            "user_email": self.user_email,
            "action": self.action,
            "entity_type": self.entity_type,
            "entity_id": str(self.entity_id) if self.entity_id else None,
            "before_state": self.before_state,
            "after_state": self.after_state,
            "correlation_id": self.correlation_id,
            "created_at": self.created_at.isoformat(),
        }


# =============================================================================
# Repository
# =============================================================================


class AuditLogRepository:
    """Repository for audit log operations."""

    def __init__(self, aurora: AuroraService):
        self.aurora = aurora

    async def create_entry(
        self,
        user_id: Optional[UUID],
        action: str,
        entity_type: str,
        entity_id: Optional[UUID] = None,
        before_state: Optional[dict] = None,
        after_state: Optional[dict] = None,
        correlation_id: Optional[str] = None,
    ) -> UUID:
        """
        Create a new audit log entry.

        Args:
            user_id: ID of the user who performed the action
            action: Action type (create, update, delete, etc.)
            entity_type: Type of entity (item, project, workstream, etc.)
            entity_id: ID of the entity
            before_state: Entity state before the change (for updates)
            after_state: Entity state after the change
            correlation_id: Request correlation ID for tracing

        Returns:
            UUID of the created entry
        """
        query = """
            INSERT INTO audit_log (
                user_id, action, entity_type, entity_id,
                before_state, after_state, correlation_id
            )
            VALUES ($1, $2, $3, $4, $5, $6, $7)
            RETURNING id
        """

        result = await self.aurora.execute_returning(
            query,
            user_id,
            action,
            entity_type,
            entity_id,
            before_state,
            after_state,
            correlation_id,
        )

        return result["id"]

    async def get_project_activity(
        self,
        project_id: UUID,
        limit: int = 100,
        offset: int = 0,
        days: int = 30,
        entity_types: Optional[list[str]] = None,
        search: Optional[str] = None,
    ) -> tuple[list[AuditEntry], int]:
        """
        Get activity feed for a project.

        Fetches audit entries for items, workstreams, and the project itself.

        Args:
            project_id: Project UUID
            limit: Max entries to return
            offset: Number of entries to skip
            days: Only include entries from the last N days
            entity_types: Filter by entity types (item, workstream, project)
            search: Search in action or entity details

        Returns:
            Tuple of (entries list, total count)
        """
        since_date = datetime.utcnow() - timedelta(days=days)

        # Build entity type filter
        type_filter = ""
        if entity_types:
            placeholders = ", ".join([f"${i+5}" for i in range(len(entity_types))])
            type_filter = f"AND a.entity_type IN ({placeholders})"

        # Build search filter
        search_filter = ""
        search_idx = 5 + len(entity_types or [])
        if search:
            search_filter = f"""
                AND (
                    a.action ILIKE ${search_idx}
                    OR a.after_state::text ILIKE ${search_idx}
                    OR a.before_state::text ILIKE ${search_idx}
                )
            """

        # Query for entries related to the project
        query = f"""
            SELECT
                a.id,
                a.user_id,
                a.action,
                a.entity_type,
                a.entity_id,
                a.before_state,
                a.after_state,
                a.correlation_id,
                a.created_at,
                u.name as user_name,
                u.email as user_email
            FROM audit_log a
            LEFT JOIN users u ON u.id = a.user_id
            WHERE a.created_at >= $1
              AND (
                  -- Direct project reference
                  (a.entity_type = 'project' AND a.entity_id = $2)
                  -- Items belonging to the project
                  OR (a.entity_type = 'item' AND EXISTS (
                      SELECT 1 FROM items i WHERE i.id = a.entity_id AND i.project_id = $2
                  ))
                  -- Workstreams belonging to the project
                  OR (a.entity_type = 'workstream' AND EXISTS (
                      SELECT 1 FROM workstreams w WHERE w.id = a.entity_id AND w.project_id = $2
                  ))
              )
              {type_filter}
              {search_filter}
            ORDER BY a.created_at DESC
            LIMIT $3 OFFSET $4
        """

        # Build parameters
        params: list[Any] = [since_date, project_id, limit, offset]
        if entity_types:
            params.extend(entity_types)
        if search:
            params.append(f"%{search}%")

        rows = await self.aurora.fetch_all(query, *params)

        entries = [
            AuditEntry(
                id=row["id"],
                user_id=row["user_id"],
                action=row["action"],
                entity_type=row["entity_type"],
                entity_id=row["entity_id"],
                before_state=row["before_state"],
                after_state=row["after_state"],
                correlation_id=row["correlation_id"],
                created_at=row["created_at"],
                user_name=row["user_name"],
                user_email=row["user_email"],
            )
            for row in rows
        ]

        # Get total count
        count_query = f"""
            SELECT COUNT(*) as total
            FROM audit_log a
            WHERE a.created_at >= $1
              AND (
                  (a.entity_type = 'project' AND a.entity_id = $2)
                  OR (a.entity_type = 'item' AND EXISTS (
                      SELECT 1 FROM items i WHERE i.id = a.entity_id AND i.project_id = $2
                  ))
                  OR (a.entity_type = 'workstream' AND EXISTS (
                      SELECT 1 FROM workstreams w WHERE w.id = a.entity_id AND w.project_id = $2
                  ))
              )
              {type_filter}
              {search_filter}
        """

        count_params: list[Any] = [since_date, project_id]
        if entity_types:
            count_params.extend(entity_types)
        if search:
            count_params.append(f"%{search}%")

        count_row = await self.aurora.fetch_one(count_query, *count_params)
        total = count_row["total"] if count_row else 0

        return entries, total

    async def get_item_history(
        self,
        item_id: UUID,
        limit: int = 50,
    ) -> list[AuditEntry]:
        """
        Get the change history for a specific item.

        Args:
            item_id: Item UUID
            limit: Max entries to return

        Returns:
            List of audit entries for the item
        """
        query = """
            SELECT
                a.id,
                a.user_id,
                a.action,
                a.entity_type,
                a.entity_id,
                a.before_state,
                a.after_state,
                a.correlation_id,
                a.created_at,
                u.name as user_name,
                u.email as user_email
            FROM audit_log a
            LEFT JOIN users u ON u.id = a.user_id
            WHERE a.entity_type = 'item' AND a.entity_id = $1
            ORDER BY a.created_at DESC
            LIMIT $2
        """

        rows = await self.aurora.fetch_all(query, item_id, limit)

        return [
            AuditEntry(
                id=row["id"],
                user_id=row["user_id"],
                action=row["action"],
                entity_type=row["entity_type"],
                entity_id=row["entity_id"],
                before_state=row["before_state"],
                after_state=row["after_state"],
                correlation_id=row["correlation_id"],
                created_at=row["created_at"],
                user_name=row["user_name"],
                user_email=row["user_email"],
            )
            for row in rows
        ]

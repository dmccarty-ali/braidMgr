"""
Item repository for database operations.

Handles all database access for items (RAID log entries).
Uses the AuroraService for query execution.

Usage:
    from src.repositories.item_repository import ItemRepository
    from src.services import services

    repo = ItemRepository(services.aurora)
    items = await repo.get_by_project_id(project_id)
"""

from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from src.domain.core import Item, ItemType, Indicator
from src.services.aurora_service import AuroraService
from src.utils.logging import get_logger

logger = get_logger(__name__)


class ItemRepository:
    """
    Repository for item database operations.

    Provides CRUD operations for items with soft delete support.
    Supports filtering by type, workstream, assignee, indicator, and search.
    """

    def __init__(self, aurora: AuroraService):
        """
        Initialize item repository.

        Args:
            aurora: Aurora database service for query execution.
        """
        self._aurora = aurora

    # =========================================================================
    # READ OPERATIONS
    # =========================================================================

    async def get_by_id(self, item_id: UUID) -> Optional[Item]:
        """
        Get an item by ID.

        Args:
            item_id: Item UUID.

        Returns:
            Item if found and not deleted, None otherwise.
        """
        row = await self._aurora.fetch_one(
            """
            SELECT id, project_id, item_num, type, title, description,
                   workstream_id, assigned_to, start_date, finish_date,
                   duration_days, deadline, draft, client_visible,
                   percent_complete, indicator, priority, rpt_out,
                   budget_amount, created_at, updated_at, deleted_at
            FROM items
            WHERE id = $1 AND deleted_at IS NULL
            """,
            item_id,
        )
        return self._row_to_item(row)

    async def get_by_item_num(self, project_id: UUID, item_num: int) -> Optional[Item]:
        """
        Get an item by project ID and item number.

        Args:
            project_id: Project UUID.
            item_num: Item number within the project.

        Returns:
            Item if found and not deleted, None otherwise.
        """
        row = await self._aurora.fetch_one(
            """
            SELECT id, project_id, item_num, type, title, description,
                   workstream_id, assigned_to, start_date, finish_date,
                   duration_days, deadline, draft, client_visible,
                   percent_complete, indicator, priority, rpt_out,
                   budget_amount, created_at, updated_at, deleted_at
            FROM items
            WHERE project_id = $1 AND item_num = $2 AND deleted_at IS NULL
            """,
            project_id,
            item_num,
        )
        return self._row_to_item(row)

    async def get_by_project_id(
        self,
        project_id: UUID,
        include_drafts: bool = False,
    ) -> list[Item]:
        """
        Get all items for a project.

        Args:
            project_id: Project UUID.
            include_drafts: Whether to include draft items.

        Returns:
            List of active items for the project.
        """
        draft_filter = "" if include_drafts else "AND draft = false"
        rows = await self._aurora.fetch_all(
            f"""
            SELECT id, project_id, item_num, type, title, description,
                   workstream_id, assigned_to, start_date, finish_date,
                   duration_days, deadline, draft, client_visible,
                   percent_complete, indicator, priority, rpt_out,
                   budget_amount, created_at, updated_at, deleted_at
            FROM items
            WHERE project_id = $1 AND deleted_at IS NULL {draft_filter}
            ORDER BY item_num ASC
            """,
            project_id,
        )
        return [self._row_to_item(row) for row in rows]

    async def list_with_filters(
        self,
        project_id: UUID,
        item_type: Optional[ItemType] = None,
        workstream_id: Optional[UUID] = None,
        assigned_to: Optional[str] = None,
        indicator: Optional[Indicator] = None,
        draft: Optional[bool] = None,
        search: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[Item]:
        """
        Get items with optional filters.

        All filters combine with AND logic.

        Args:
            project_id: Project UUID (required).
            item_type: Filter by item type.
            workstream_id: Filter by workstream.
            assigned_to: Filter by assignee (partial match).
            indicator: Filter by indicator.
            draft: Filter by draft status.
            search: Search in title and description.
            limit: Maximum number of results.
            offset: Number of results to skip.

        Returns:
            List of matching items.
        """
        conditions = ["project_id = $1", "deleted_at IS NULL"]
        params = [project_id]
        param_num = 2

        if item_type is not None:
            conditions.append(f"type = ${param_num}")
            params.append(item_type.value)
            param_num += 1

        if workstream_id is not None:
            conditions.append(f"workstream_id = ${param_num}")
            params.append(workstream_id)
            param_num += 1

        if assigned_to is not None:
            conditions.append(f"assigned_to ILIKE ${param_num}")
            params.append(f"%{assigned_to}%")
            param_num += 1

        if indicator is not None:
            conditions.append(f"indicator = ${param_num}")
            params.append(indicator.value)
            param_num += 1

        if draft is not None:
            conditions.append(f"draft = ${param_num}")
            params.append(draft)
            param_num += 1

        if search is not None:
            conditions.append(
                f"(title ILIKE ${param_num} OR description ILIKE ${param_num})"
            )
            params.append(f"%{search}%")
            param_num += 1

        where_clause = " AND ".join(conditions)
        params.extend([limit, offset])

        rows = await self._aurora.fetch_all(
            f"""
            SELECT id, project_id, item_num, type, title, description,
                   workstream_id, assigned_to, start_date, finish_date,
                   duration_days, deadline, draft, client_visible,
                   percent_complete, indicator, priority, rpt_out,
                   budget_amount, created_at, updated_at, deleted_at
            FROM items
            WHERE {where_clause}
            ORDER BY item_num ASC
            LIMIT ${param_num - 1} OFFSET ${param_num}
            """,
            *params,
        )
        return [self._row_to_item(row) for row in rows]

    async def count_by_project_id(
        self,
        project_id: UUID,
        include_drafts: bool = False,
    ) -> int:
        """
        Count items in a project.

        Args:
            project_id: Project UUID.
            include_drafts: Whether to include draft items.

        Returns:
            Number of active items.
        """
        draft_filter = "" if include_drafts else "AND draft = false"
        row = await self._aurora.fetch_one(
            f"""
            SELECT COUNT(*) as count
            FROM items
            WHERE project_id = $1 AND deleted_at IS NULL {draft_filter}
            """,
            project_id,
        )
        return row["count"] if row else 0

    # =========================================================================
    # WRITE OPERATIONS
    # =========================================================================

    async def create(
        self,
        project_id: UUID,
        item_num: int,
        item_type: ItemType,
        title: str,
        description: Optional[str] = None,
        workstream_id: Optional[UUID] = None,
        assigned_to: Optional[str] = None,
        start_date: Optional[date] = None,
        finish_date: Optional[date] = None,
        duration_days: Optional[int] = None,
        deadline: Optional[date] = None,
        draft: bool = False,
        client_visible: bool = True,
        percent_complete: int = 0,
        indicator: Optional[Indicator] = None,
        priority: Optional[str] = None,
        rpt_out: Optional[list[str]] = None,
        budget_amount: Optional[Decimal] = None,
    ) -> Item:
        """
        Create a new item.

        Args:
            project_id: Project UUID.
            item_num: Unique item number within project.
            item_type: Item type (Risk, Action, etc.).
            title: Item title.
            description: Detailed description (optional).
            workstream_id: Associated workstream (optional).
            assigned_to: Assignee name (optional).
            start_date: Planned start date (optional).
            finish_date: Planned finish date (optional).
            duration_days: Estimated duration (optional).
            deadline: Hard deadline (optional).
            draft: Whether item is in draft mode.
            client_visible: Whether visible to client.
            percent_complete: Completion percentage (0-100).
            indicator: Calculated indicator (optional).
            priority: Priority level (optional).
            rpt_out: Report codes (optional).
            budget_amount: Budget amount for Budget items (optional).

        Returns:
            Created item.
        """
        row = await self._aurora.fetch_one(
            """
            INSERT INTO items (
                project_id, item_num, type, title, description,
                workstream_id, assigned_to, start_date, finish_date,
                duration_days, deadline, draft, client_visible,
                percent_complete, indicator, priority, rpt_out, budget_amount
            )
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, $18)
            RETURNING id, project_id, item_num, type, title, description,
                      workstream_id, assigned_to, start_date, finish_date,
                      duration_days, deadline, draft, client_visible,
                      percent_complete, indicator, priority, rpt_out,
                      budget_amount, created_at, updated_at, deleted_at
            """,
            project_id,
            item_num,
            item_type.value,
            title,
            description,
            workstream_id,
            assigned_to,
            start_date,
            finish_date,
            duration_days,
            deadline,
            draft,
            client_visible,
            percent_complete,
            indicator.value if indicator else None,
            priority,
            rpt_out,
            budget_amount,
        )
        item = self._row_to_item(row)
        logger.info(
            "item_created",
            item_id=str(item.id),
            project_id=str(project_id),
            item_num=item_num,
        )
        return item

    async def update(
        self,
        item_id: UUID,
        title: Optional[str] = None,
        description: Optional[str] = None,
        workstream_id: Optional[UUID] = None,
        assigned_to: Optional[str] = None,
        start_date: Optional[date] = None,
        finish_date: Optional[date] = None,
        duration_days: Optional[int] = None,
        deadline: Optional[date] = None,
        draft: Optional[bool] = None,
        client_visible: Optional[bool] = None,
        percent_complete: Optional[int] = None,
        indicator: Optional[Indicator] = None,
        priority: Optional[str] = None,
        rpt_out: Optional[list[str]] = None,
        budget_amount: Optional[Decimal] = None,
    ) -> Optional[Item]:
        """
        Update an item.

        Only updates fields that are provided (not None).
        Note: type and item_num cannot be changed.

        Args:
            item_id: Item UUID.
            title: New title (optional).
            description: New description (optional).
            workstream_id: New workstream (optional).
            assigned_to: New assignee (optional).
            start_date: New start date (optional).
            finish_date: New finish date (optional).
            duration_days: New duration (optional).
            deadline: New deadline (optional).
            draft: New draft status (optional).
            client_visible: New visibility (optional).
            percent_complete: New completion (optional).
            indicator: New indicator (optional).
            priority: New priority (optional).
            rpt_out: New report codes (optional).
            budget_amount: New budget amount (optional).

        Returns:
            Updated item, or None if not found.
        """
        # Build dynamic update query
        updates = []
        params = []
        param_num = 1

        field_map = {
            "title": title,
            "description": description,
            "workstream_id": workstream_id,
            "assigned_to": assigned_to,
            "start_date": start_date,
            "finish_date": finish_date,
            "duration_days": duration_days,
            "deadline": deadline,
            "draft": draft,
            "client_visible": client_visible,
            "percent_complete": percent_complete,
            "priority": priority,
            "rpt_out": rpt_out,
            "budget_amount": budget_amount,
        }

        for field_name, value in field_map.items():
            if value is not None:
                updates.append(f"{field_name} = ${param_num}")
                params.append(value)
                param_num += 1

        # Handle indicator specially (enum to value)
        if indicator is not None:
            updates.append(f"indicator = ${param_num}")
            params.append(indicator.value)
            param_num += 1

        if not updates:
            return await self.get_by_id(item_id)

        updates.append("updated_at = now()")
        params.append(item_id)

        query = f"""
            UPDATE items
            SET {", ".join(updates)}
            WHERE id = ${param_num} AND deleted_at IS NULL
            RETURNING id, project_id, item_num, type, title, description,
                      workstream_id, assigned_to, start_date, finish_date,
                      duration_days, deadline, draft, client_visible,
                      percent_complete, indicator, priority, rpt_out,
                      budget_amount, created_at, updated_at, deleted_at
        """

        row = await self._aurora.fetch_one(query, *params)
        if row:
            logger.info("item_updated", item_id=str(item_id))
        return self._row_to_item(row)

    async def update_indicator(
        self, item_id: UUID, indicator: Optional[Indicator]
    ) -> bool:
        """
        Update just the indicator field.

        Used during batch indicator recalculation.

        Args:
            item_id: Item UUID.
            indicator: New indicator value.

        Returns:
            True if updated, False if not found.
        """
        result = await self._aurora.execute(
            """
            UPDATE items
            SET indicator = $1, updated_at = now()
            WHERE id = $2 AND deleted_at IS NULL
            """,
            indicator.value if indicator else None,
            item_id,
        )
        return result == "UPDATE 1"

    async def batch_update_indicators(
        self, updates: list[tuple[UUID, Optional[Indicator]]]
    ) -> int:
        """
        Batch update indicators for multiple items.

        More efficient than individual updates.

        Args:
            updates: List of (item_id, indicator) tuples.

        Returns:
            Number of items updated.
        """
        if not updates:
            return 0

        count = 0
        for item_id, indicator in updates:
            if await self.update_indicator(item_id, indicator):
                count += 1

        logger.info("batch_indicators_updated", count=count)
        return count

    async def soft_delete(self, item_id: UUID) -> bool:
        """
        Soft delete an item.

        Sets deleted_at timestamp instead of removing the record.

        Args:
            item_id: Item UUID.

        Returns:
            True if item was deleted, False if not found.
        """
        result = await self._aurora.execute(
            """
            UPDATE items
            SET deleted_at = now(), updated_at = now()
            WHERE id = $1 AND deleted_at IS NULL
            """,
            item_id,
        )
        deleted = result == "UPDATE 1"
        if deleted:
            logger.info("item_deleted", item_id=str(item_id))
        return deleted

    # =========================================================================
    # HELPERS
    # =========================================================================

    @staticmethod
    def _row_to_item(row) -> Optional[Item]:
        """
        Convert a database row to an Item dataclass.

        Args:
            row: Database row dict.

        Returns:
            Item instance, or None if row is None.
        """
        if row is None:
            return None

        return Item(
            id=row["id"],
            project_id=row["project_id"],
            item_num=row["item_num"],
            type=ItemType(row["type"]),
            title=row["title"],
            description=row["description"],
            workstream_id=row["workstream_id"],
            assigned_to=row["assigned_to"],
            start_date=row["start_date"],
            finish_date=row["finish_date"],
            duration_days=row["duration_days"],
            deadline=row["deadline"],
            draft=row["draft"],
            client_visible=row["client_visible"],
            percent_complete=row["percent_complete"],
            indicator=Indicator(row["indicator"]) if row["indicator"] else None,
            priority=row["priority"],
            rpt_out=row["rpt_out"],
            budget_amount=row["budget_amount"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            deleted_at=row["deleted_at"],
        )

"""
Item service for business logic.

Coordinates item operations between repositories.
Handles validation, auto-numbering, and indicator calculation.

Usage:
    from src.services.item_service import ItemService
    from src.services import services

    item_svc = ItemService(services.aurora)
    result = await item_svc.create_item(project_id, type, title, ...)
"""

from datetime import date
from decimal import Decimal
from typing import Optional
from uuid import UUID

from src.domain.core import Item, ItemResult, ItemType, Indicator
from src.repositories.project_repository import ProjectRepository
from src.repositories.item_repository import ItemRepository
from src.repositories.item_note_repository import ItemNoteRepository
from src.repositories.item_dependency_repository import ItemDependencyRepository
from src.services.aurora_service import AuroraService
from src.services.indicator_service import calculate_indicator
from src.utils.logging import get_logger

logger = get_logger(__name__)


class ItemService:
    """
    Service for item business logic.

    Coordinates between repositories and handles business rules
    including auto-numbering and indicator calculation.
    """

    def __init__(self, aurora: AuroraService):
        """
        Initialize item service.

        Args:
            aurora: Aurora database service.
        """
        self._aurora = aurora
        self._project_repo = ProjectRepository(aurora)
        self._item_repo = ItemRepository(aurora)
        self._note_repo = ItemNoteRepository(aurora)
        self._dep_repo = ItemDependencyRepository(aurora)

    # =========================================================================
    # ITEM CRUD
    # =========================================================================

    async def create_item(
        self,
        project_id: UUID,
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
        priority: Optional[str] = None,
        rpt_out: Optional[list[str]] = None,
        budget_amount: Optional[Decimal] = None,
    ) -> ItemResult:
        """
        Create a new item with auto-assigned item number.

        Args:
            project_id: Project UUID.
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
            priority: Priority level (optional).
            rpt_out: Report codes (optional).
            budget_amount: Budget amount for Budget items (optional).

        Returns:
            ItemResult with created item or error.
        """
        # Validate project exists
        project = await self._project_repo.get_by_id(project_id)
        if not project:
            return ItemResult(success=False, error="Project not found")

        # Validate dates
        if start_date and finish_date and finish_date < start_date:
            return ItemResult(
                success=False,
                error="Finish date must be after start date",
            )

        # Validate percent_complete range
        if percent_complete < 0 or percent_complete > 100:
            return ItemResult(
                success=False,
                error="Percent complete must be between 0 and 100",
            )

        # Get next item number atomically
        item_num = await self._project_repo.increment_item_num(project_id)

        # Create temporary item to calculate indicator
        temp_item = Item(
            id=UUID("00000000-0000-0000-0000-000000000000"),
            project_id=project_id,
            item_num=item_num,
            type=item_type,
            title=title,
            description=description,
            workstream_id=workstream_id,
            assigned_to=assigned_to,
            start_date=start_date,
            finish_date=finish_date,
            duration_days=duration_days,
            deadline=deadline,
            draft=draft,
            client_visible=client_visible,
            percent_complete=percent_complete,
            priority=priority,
            rpt_out=rpt_out,
            budget_amount=budget_amount,
        )
        indicator = calculate_indicator(temp_item)

        # Create item
        item = await self._item_repo.create(
            project_id=project_id,
            item_num=item_num,
            item_type=item_type,
            title=title,
            description=description,
            workstream_id=workstream_id,
            assigned_to=assigned_to,
            start_date=start_date,
            finish_date=finish_date,
            duration_days=duration_days,
            deadline=deadline,
            draft=draft,
            client_visible=client_visible,
            percent_complete=percent_complete,
            indicator=indicator,
            priority=priority,
            rpt_out=rpt_out,
            budget_amount=budget_amount,
        )

        logger.info(
            "item_created",
            item_id=str(item.id),
            project_id=str(project_id),
            item_num=item_num,
            type=item_type.value,
        )

        return ItemResult(success=True, item=item)

    async def get_item(self, item_id: UUID) -> Optional[Item]:
        """
        Get an item by ID.

        Args:
            item_id: Item UUID.

        Returns:
            Item if found, None otherwise.
        """
        return await self._item_repo.get_by_id(item_id)

    async def get_item_by_num(
        self, project_id: UUID, item_num: int
    ) -> Optional[Item]:
        """
        Get an item by project and item number.

        Args:
            project_id: Project UUID.
            item_num: Item number.

        Returns:
            Item if found, None otherwise.
        """
        return await self._item_repo.get_by_item_num(project_id, item_num)

    async def list_items(
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
        List items with optional filters.

        Args:
            project_id: Project UUID.
            item_type: Filter by type.
            workstream_id: Filter by workstream.
            assigned_to: Filter by assignee.
            indicator: Filter by indicator.
            draft: Filter by draft status.
            search: Search in title/description.
            limit: Maximum results.
            offset: Skip results.

        Returns:
            List of matching items.
        """
        return await self._item_repo.list_with_filters(
            project_id=project_id,
            item_type=item_type,
            workstream_id=workstream_id,
            assigned_to=assigned_to,
            indicator=indicator,
            draft=draft,
            search=search,
            limit=limit,
            offset=offset,
        )

    async def update_item(
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
        priority: Optional[str] = None,
        rpt_out: Optional[list[str]] = None,
        budget_amount: Optional[Decimal] = None,
    ) -> ItemResult:
        """
        Update an item with automatic indicator recalculation.

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
            priority: New priority (optional).
            rpt_out: New report codes (optional).
            budget_amount: New budget amount (optional).

        Returns:
            ItemResult with updated item or error.
        """
        # Get existing item
        existing = await self._item_repo.get_by_id(item_id)
        if not existing:
            return ItemResult(success=False, error="Item not found")

        # Validate dates
        start = start_date if start_date is not None else existing.start_date
        finish = finish_date if finish_date is not None else existing.finish_date
        if start and finish and finish < start:
            return ItemResult(
                success=False,
                error="Finish date must be after start date",
            )

        # Validate percent_complete range
        pct = percent_complete if percent_complete is not None else existing.percent_complete
        if pct < 0 or pct > 100:
            return ItemResult(
                success=False,
                error="Percent complete must be between 0 and 100",
            )

        # Update item (without indicator first)
        item = await self._item_repo.update(
            item_id=item_id,
            title=title,
            description=description,
            workstream_id=workstream_id,
            assigned_to=assigned_to,
            start_date=start_date,
            finish_date=finish_date,
            duration_days=duration_days,
            deadline=deadline,
            draft=draft,
            client_visible=client_visible,
            percent_complete=percent_complete,
            priority=priority,
            rpt_out=rpt_out,
            budget_amount=budget_amount,
        )

        if not item:
            return ItemResult(success=False, error="Item not found")

        # Recalculate and update indicator
        new_indicator = calculate_indicator(item)
        if new_indicator != item.indicator:
            await self._item_repo.update_indicator(item_id, new_indicator)
            item = await self._item_repo.get_by_id(item_id)

        logger.info("item_updated", item_id=str(item_id))
        return ItemResult(success=True, item=item)

    async def delete_item(self, item_id: UUID) -> ItemResult:
        """
        Soft delete an item.

        Args:
            item_id: Item UUID.

        Returns:
            ItemResult with success status.
        """
        deleted = await self._item_repo.soft_delete(item_id)
        if not deleted:
            return ItemResult(success=False, error="Item not found")

        logger.info("item_deleted", item_id=str(item_id))
        return ItemResult(success=True)

    # =========================================================================
    # INDICATOR MANAGEMENT
    # =========================================================================

    async def update_all_indicators(self, project_id: UUID) -> int:
        """
        Recalculate indicators for all items in a project.

        Args:
            project_id: Project UUID.

        Returns:
            Number of items updated.
        """
        # Get all non-draft items
        items = await self._item_repo.get_by_project_id(project_id, include_drafts=True)

        # Calculate new indicators
        updates = []
        today = date.today()
        for item in items:
            new_indicator = calculate_indicator(item, today)
            if new_indicator != item.indicator:
                updates.append((item.id, new_indicator))

        # Batch update
        count = await self._item_repo.batch_update_indicators(updates)

        # Update project timestamp
        await self._project_repo.update_indicators_timestamp(project_id)

        logger.info(
            "indicators_updated",
            project_id=str(project_id),
            total_items=len(items),
            updated_count=count,
        )

        return count

    # =========================================================================
    # ITEM PUBLISHING
    # =========================================================================

    async def publish_item(self, item_id: UUID) -> ItemResult:
        """
        Publish a draft item (set draft=false).

        Args:
            item_id: Item UUID.

        Returns:
            ItemResult with updated item.
        """
        item = await self._item_repo.get_by_id(item_id)
        if not item:
            return ItemResult(success=False, error="Item not found")

        if not item.draft:
            return ItemResult(success=False, error="Item is not a draft")

        return await self.update_item(item_id, draft=False)

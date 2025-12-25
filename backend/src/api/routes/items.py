"""
Item API routes.

Handles item CRUD operations with filtering.

Endpoints:
    POST /projects/{project_id}/items - Create new item
    GET /projects/{project_id}/items - List items with filters
    GET /projects/{project_id}/items/{item_id} - Get item details
    PUT /projects/{project_id}/items/{item_id} - Update item
    DELETE /projects/{project_id}/items/{item_id} - Soft delete item
"""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from src.api.dependencies.auth import (
    get_project_access,
    require_project_member,
)
from src.api.schemas.items import (
    ItemCreateRequest,
    ItemUpdateRequest,
    ItemResponse,
    ItemListResponse,
)
from src.domain.auth import ProjectRole
from src.domain.core import ItemType, Indicator
from src.services import services
from src.services.item_service import ItemService
from src.utils.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/projects/{project_id}/items", tags=["Items"])


def _get_item_service() -> ItemService:
    """Get item service instance."""
    return ItemService(services.aurora)


# =============================================================================
# CREATE ITEM
# =============================================================================


@router.post(
    "",
    response_model=ItemResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create new item",
    description="Create a new item (Risk, Action, Issue, Decision, etc.) in the project.",
)
async def create_item(
    project_id: UUID,
    body: ItemCreateRequest,
    role: ProjectRole = Depends(require_project_member),
):
    """
    Create a new item in the project.

    Requires team member or higher role.
    Auto-assigns item number and calculates indicator.
    """
    item_service = _get_item_service()
    result = await item_service.create_item(
        project_id=project_id,
        item_type=body.type,
        title=body.title,
        description=body.description,
        workstream_id=body.workstream_id,
        assigned_to=body.assigned_to,
        start_date=body.start_date,
        finish_date=body.finish_date,
        duration_days=body.duration_days,
        deadline=body.deadline,
        draft=body.draft,
        client_visible=body.client_visible,
        percent_complete=body.percent_complete,
        priority=body.priority,
        rpt_out=body.rpt_out,
        budget_amount=body.budget_amount,
    )

    if not result.success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.error,
        )

    logger.info(
        "item_created",
        item_id=str(result.item.id),
        project_id=str(project_id),
        type=result.item.type.value,
        item_num=result.item.item_num,
    )

    return ItemResponse.model_validate(result.item)


# =============================================================================
# LIST ITEMS
# =============================================================================


@router.get(
    "",
    response_model=ItemListResponse,
    summary="List items",
    description="List items with optional filtering.",
)
async def list_items(
    project_id: UUID,
    type: Optional[ItemType] = Query(None, description="Filter by item type"),
    workstream_id: Optional[UUID] = Query(None, description="Filter by workstream"),
    assigned_to: Optional[str] = Query(None, description="Filter by assignee (partial match)"),
    indicator: Optional[Indicator] = Query(None, description="Filter by indicator"),
    draft: Optional[bool] = Query(None, description="Filter by draft status"),
    search: Optional[str] = Query(None, max_length=100, description="Search in title/description"),
    limit: int = Query(100, ge=1, le=500, description="Max results"),
    offset: int = Query(0, ge=0, description="Skip results"),
    role: ProjectRole = Depends(get_project_access),
):
    """
    List items for a project with optional filters.

    Filters combine with AND logic.
    Results ordered by item_num descending (newest first).
    """
    item_service = _get_item_service()
    items, total = await item_service.list_items(
        project_id=project_id,
        item_type=type,
        workstream_id=workstream_id,
        assigned_to=assigned_to,
        indicator=indicator,
        draft=draft,
        search=search,
        limit=limit,
        offset=offset,
    )

    return ItemListResponse(
        items=[ItemResponse.model_validate(i) for i in items],
        total=total,
    )


# =============================================================================
# GET ITEM
# =============================================================================


@router.get(
    "/{item_id}",
    response_model=ItemResponse,
    summary="Get item",
    description="Get item details by ID.",
)
async def get_item(
    project_id: UUID,
    item_id: UUID,
    role: ProjectRole = Depends(get_project_access),
):
    """
    Get an item by ID.

    Returns 404 if item not found or belongs to different project.
    """
    item_service = _get_item_service()
    item = await item_service.get_item(item_id)

    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found",
        )

    # Verify item belongs to the project
    if item.project_id != project_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found",
        )

    return ItemResponse.model_validate(item)


# =============================================================================
# UPDATE ITEM
# =============================================================================


@router.put(
    "/{item_id}",
    response_model=ItemResponse,
    summary="Update item",
    description="Update item details.",
)
async def update_item(
    project_id: UUID,
    item_id: UUID,
    body: ItemUpdateRequest,
    role: ProjectRole = Depends(require_project_member),
):
    """
    Update an item.

    Requires team member or higher role.
    Only provided fields are updated.
    Indicator is recalculated after update.
    """
    item_service = _get_item_service()

    # First verify item exists and belongs to project
    existing = await item_service.get_item(item_id)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found",
        )
    if existing.project_id != project_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found",
        )

    result = await item_service.update_item(
        item_id=item_id,
        title=body.title,
        description=body.description,
        workstream_id=body.workstream_id,
        assigned_to=body.assigned_to,
        start_date=body.start_date,
        finish_date=body.finish_date,
        duration_days=body.duration_days,
        deadline=body.deadline,
        draft=body.draft,
        client_visible=body.client_visible,
        percent_complete=body.percent_complete,
        priority=body.priority,
        rpt_out=body.rpt_out,
        budget_amount=body.budget_amount,
    )

    if not result.success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.error,
        )

    logger.info("item_updated", item_id=str(item_id), project_id=str(project_id))
    return ItemResponse.model_validate(result.item)


# =============================================================================
# DELETE ITEM
# =============================================================================


@router.delete(
    "/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete item",
    description="Soft delete an item.",
)
async def delete_item(
    project_id: UUID,
    item_id: UUID,
    role: ProjectRole = Depends(require_project_member),
):
    """
    Soft delete an item.

    Requires team member or higher role.
    Item is marked as deleted but data is retained.
    """
    item_service = _get_item_service()

    # First verify item exists and belongs to project
    existing = await item_service.get_item(item_id)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found",
        )
    if existing.project_id != project_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found",
        )

    result = await item_service.delete_item(item_id)

    if not result.success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.error,
        )

    logger.info("item_deleted", item_id=str(item_id), project_id=str(project_id))

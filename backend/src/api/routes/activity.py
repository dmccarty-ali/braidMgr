"""
Activity API routes.

Provides project activity feed endpoints for the Chronology view.

Endpoints:
    GET /projects/{project_id}/activity - Get project activity feed
    GET /projects/{project_id}/items/{item_id}/history - Get item change history
"""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query

from src.api.dependencies.auth import require_project_viewer
from src.domain.auth import ProjectRole
from src.repositories.audit_log_repository import AuditLogRepository
from src.services import services
from src.utils.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/projects/{project_id}", tags=["Activity"])


def _get_audit_repo() -> AuditLogRepository:
    """Get audit log repository instance."""
    return AuditLogRepository(services.aurora)


# =============================================================================
# PROJECT ACTIVITY FEED
# =============================================================================


@router.get(
    "/activity",
    summary="Get project activity feed",
    description="Get a chronological feed of all project activity (item changes, etc.)",
)
async def get_project_activity(
    project_id: UUID,
    days: int = Query(30, ge=1, le=365, description="Number of days to look back"),
    limit: int = Query(100, ge=1, le=500, description="Max entries to return"),
    offset: int = Query(0, ge=0, description="Number of entries to skip"),
    entity_type: Optional[str] = Query(None, description="Filter by entity type (item, workstream, project)"),
    search: Optional[str] = Query(None, description="Search in activity details"),
    role: ProjectRole = Depends(require_project_viewer),
    repo: AuditLogRepository = Depends(_get_audit_repo),
):
    """
    Get project activity feed.

    Returns audit log entries for items, workstreams, and the project itself,
    ordered by most recent first.
    """
    entity_types = [entity_type] if entity_type else None

    entries, total = await repo.get_project_activity(
        project_id=project_id,
        limit=limit,
        offset=offset,
        days=days,
        entity_types=entity_types,
        search=search,
    )

    return {
        "activity": [entry.to_dict() for entry in entries],
        "total": total,
        "limit": limit,
        "offset": offset,
    }


# =============================================================================
# ITEM HISTORY
# =============================================================================


@router.get(
    "/items/{item_id}/history",
    summary="Get item change history",
    description="Get the full change history for a specific item",
)
async def get_item_history(
    project_id: UUID,
    item_id: UUID,
    limit: int = Query(50, ge=1, le=200, description="Max entries to return"),
    role: ProjectRole = Depends(require_project_viewer),
    repo: AuditLogRepository = Depends(_get_audit_repo),
):
    """
    Get item change history.

    Returns all audit log entries for a specific item, ordered by most recent first.
    """
    entries = await repo.get_item_history(item_id=item_id, limit=limit)

    return {
        "history": [entry.to_dict() for entry in entries],
        "item_id": str(item_id),
    }

"""
Workstream API routes.

Handles workstream CRUD operations and reordering.

Endpoints:
    POST /projects/{project_id}/workstreams - Create new workstream
    GET /projects/{project_id}/workstreams - List workstreams
    PUT /projects/{project_id}/workstreams/{workstream_id} - Update workstream
    DELETE /projects/{project_id}/workstreams/{workstream_id} - Delete workstream
    PUT /projects/{project_id}/workstreams/reorder - Reorder workstreams
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from src.api.dependencies.auth import (
    get_project_access,
    require_project_manager,
)
from src.api.schemas.workstreams import (
    WorkstreamCreateRequest,
    WorkstreamUpdateRequest,
    WorkstreamReorderRequest,
    WorkstreamResponse,
    WorkstreamListResponse,
)
from src.domain.auth import ProjectRole
from src.services import services
from src.services.workstream_service import WorkstreamService
from src.utils.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/projects/{project_id}/workstreams", tags=["Workstreams"])


def _get_workstream_service() -> WorkstreamService:
    """Get workstream service instance."""
    return WorkstreamService(services.aurora)


# =============================================================================
# CREATE WORKSTREAM
# =============================================================================


@router.post(
    "",
    response_model=WorkstreamResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create new workstream",
    description="Create a new workstream in the project.",
)
async def create_workstream(
    project_id: UUID,
    body: WorkstreamCreateRequest,
    role: ProjectRole = Depends(require_project_manager),
):
    """
    Create a new workstream in the project.

    Requires project manager or higher role.
    Workstream name must be unique within the project.
    """
    workstream_service = _get_workstream_service()
    result = await workstream_service.create_workstream(
        project_id=project_id,
        name=body.name,
    )

    if not result.success:
        if result.error == "Project not found":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=result.error,
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.error,
        )

    logger.info(
        "workstream_created",
        workstream_id=str(result.workstream.id),
        project_id=str(project_id),
        name=result.workstream.name,
    )

    return WorkstreamResponse.model_validate(result.workstream)


# =============================================================================
# LIST WORKSTREAMS
# =============================================================================


@router.get(
    "",
    response_model=WorkstreamListResponse,
    summary="List workstreams",
    description="List all workstreams in the project.",
)
async def list_workstreams(
    project_id: UUID,
    role: ProjectRole = Depends(get_project_access),
):
    """
    List all workstreams for a project.

    Returns workstreams ordered by sort_order.
    """
    workstream_service = _get_workstream_service()
    workstreams = await workstream_service.list_workstreams(project_id)

    return WorkstreamListResponse(
        workstreams=[WorkstreamResponse.model_validate(w) for w in workstreams],
        total=len(workstreams),
    )


# =============================================================================
# UPDATE WORKSTREAM
# =============================================================================


@router.put(
    "/{workstream_id}",
    response_model=WorkstreamResponse,
    summary="Update workstream",
    description="Update workstream details.",
)
async def update_workstream(
    project_id: UUID,
    workstream_id: UUID,
    body: WorkstreamUpdateRequest,
    role: ProjectRole = Depends(require_project_manager),
):
    """
    Update a workstream.

    Requires project manager or higher role.
    Workstream name must remain unique within the project.
    """
    workstream_service = _get_workstream_service()

    # Verify workstream belongs to project
    existing = await workstream_service.get_workstream(workstream_id)
    if not existing or existing.project_id != project_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workstream not found",
        )

    result = await workstream_service.update_workstream(
        workstream_id=workstream_id,
        name=body.name,
    )

    if not result.success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.error,
        )

    logger.info("workstream_updated", workstream_id=str(workstream_id))
    return WorkstreamResponse.model_validate(result.workstream)


# =============================================================================
# DELETE WORKSTREAM
# =============================================================================


@router.delete(
    "/{workstream_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete workstream",
    description="Delete a workstream. Items using it will have workstream_id set to NULL.",
)
async def delete_workstream(
    project_id: UUID,
    workstream_id: UUID,
    role: ProjectRole = Depends(require_project_manager),
):
    """
    Delete a workstream.

    Requires project manager or higher role.
    Items using this workstream will have workstream_id set to NULL.
    """
    workstream_service = _get_workstream_service()

    # Verify workstream belongs to project
    existing = await workstream_service.get_workstream(workstream_id)
    if not existing or existing.project_id != project_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workstream not found",
        )

    result = await workstream_service.delete_workstream(workstream_id)

    if not result.success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.error,
        )

    logger.info("workstream_deleted", workstream_id=str(workstream_id))


# =============================================================================
# REORDER WORKSTREAMS
# =============================================================================


@router.put(
    "/reorder",
    response_model=WorkstreamListResponse,
    summary="Reorder workstreams",
    description="Reorder workstreams by providing the new order of IDs.",
)
async def reorder_workstreams(
    project_id: UUID,
    body: WorkstreamReorderRequest,
    role: ProjectRole = Depends(require_project_manager),
):
    """
    Reorder workstreams in a project.

    Requires project manager or higher role.
    Provide list of workstream IDs in desired order.
    """
    workstream_service = _get_workstream_service()
    workstreams = await workstream_service.reorder_workstreams(
        project_id=project_id,
        workstream_ids=body.workstream_ids,
    )

    logger.info(
        "workstreams_reordered",
        project_id=str(project_id),
        count=len(workstreams),
    )

    return WorkstreamListResponse(
        workstreams=[WorkstreamResponse.model_validate(w) for w in workstreams],
        total=len(workstreams),
    )

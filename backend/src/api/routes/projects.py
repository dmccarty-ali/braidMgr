"""
Project API routes.

Handles project CRUD operations and indicator recalculation.

Endpoints:
    POST /projects - Create new project
    GET /projects - List user's projects
    GET /projects/{project_id} - Get project details
    PUT /projects/{project_id} - Update project
    DELETE /projects/{project_id} - Soft delete project
    POST /projects/{project_id}/update-indicators - Batch recalculate indicators
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from src.api.dependencies.auth import (
    RequireAuth,
    get_project_access,
    require_project_admin,
)
from src.api.schemas.projects import (
    ProjectCreateRequest,
    ProjectUpdateRequest,
    ProjectResponse,
    ProjectListResponse,
)
from src.domain.auth import ProjectRole
from src.services import services
from src.services.project_service import ProjectService
from src.utils.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/projects", tags=["Projects"])


def _get_project_service() -> ProjectService:
    """Get project service instance."""
    return ProjectService(services.aurora)


# =============================================================================
# CREATE PROJECT
# =============================================================================


@router.post(
    "",
    response_model=ProjectResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create new project",
    description="Create a new project in the user's organization.",
)
async def create_project(
    body: ProjectCreateRequest,
    user: RequireAuth,
):
    """
    Create a new project.

    User must have an organization context (org_id in token).
    Initial workstreams can be provided.
    """
    if not user.org_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No organization context",
        )

    project_service = _get_project_service()
    result = await project_service.create_project(
        org_id=user.org_id,
        name=body.name,
        client_name=body.client_name,
        project_start=body.project_start,
        project_end=body.project_end,
        workstream_names=body.workstreams,
        created_by=user.id,
    )

    if not result.success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.error,
        )

    logger.info(
        "project_created",
        project_id=str(result.project.id),
        name=result.project.name,
        user_id=str(user.id),
    )

    return ProjectResponse.model_validate(result.project)


# =============================================================================
# LIST PROJECTS
# =============================================================================


@router.get(
    "",
    response_model=ProjectListResponse,
    summary="List projects",
    description="List all projects the user has access to.",
)
async def list_projects(user: RequireAuth):
    """
    List projects for the current user.

    Returns only projects where user has a role.
    """
    if not user.org_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No organization context",
        )

    project_service = _get_project_service()
    projects = await project_service.list_projects(
        user_id=user.id,
        org_id=user.org_id,
    )

    return ProjectListResponse(
        projects=[ProjectResponse.model_validate(p) for p in projects],
        total=len(projects),
    )


# =============================================================================
# GET PROJECT
# =============================================================================


@router.get(
    "/{project_id}",
    response_model=ProjectResponse,
    summary="Get project",
    description="Get project details by ID.",
)
async def get_project(
    project_id: UUID,
    role: ProjectRole = Depends(get_project_access),
):
    """
    Get a project by ID.

    User must have access to the project.
    """
    project_service = _get_project_service()
    project = await project_service.get_project(project_id)

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    return ProjectResponse.model_validate(project)


# =============================================================================
# UPDATE PROJECT
# =============================================================================


@router.put(
    "/{project_id}",
    response_model=ProjectResponse,
    summary="Update project",
    description="Update project details.",
)
async def update_project(
    project_id: UUID,
    body: ProjectUpdateRequest,
    role: ProjectRole = Depends(get_project_access),
):
    """
    Update a project.

    User must have access to the project.
    Only provided fields are updated.
    """
    project_service = _get_project_service()
    result = await project_service.update_project(
        project_id=project_id,
        name=body.name,
        client_name=body.client_name,
        project_start=body.project_start,
        project_end=body.project_end,
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

    logger.info("project_updated", project_id=str(project_id))
    return ProjectResponse.model_validate(result.project)


# =============================================================================
# DELETE PROJECT
# =============================================================================


@router.delete(
    "/{project_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete project",
    description="Soft delete a project (requires admin role).",
)
async def delete_project(
    project_id: UUID,
    role: ProjectRole = Depends(require_project_admin),
):
    """
    Soft delete a project.

    Requires project admin role.
    Project is marked as deleted but data is retained.
    """
    project_service = _get_project_service()
    result = await project_service.delete_project(project_id)

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

    logger.info("project_deleted", project_id=str(project_id))


# =============================================================================
# INDICATOR RECALCULATION
# =============================================================================


@router.post(
    "/{project_id}/update-indicators",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Recalculate indicators",
    description="Batch recalculate all item indicators for the project.",
)
async def update_indicators(
    project_id: UUID,
    role: ProjectRole = Depends(get_project_access),
):
    """
    Recalculate all item indicators for a project.

    Updates the indicators_updated timestamp on the project.
    """
    project_service = _get_project_service()

    # Verify project exists
    project = await project_service.get_project(project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    await project_service.update_all_indicators(project_id)
    logger.info("indicators_updated", project_id=str(project_id))

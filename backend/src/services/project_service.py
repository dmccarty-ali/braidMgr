"""
Project service for business logic.

Coordinates project operations between repositories.
Handles validation, authorization, and business rules.

Usage:
    from src.services.project_service import ProjectService
    from src.services import services

    project_svc = ProjectService(services.aurora)
    result = await project_svc.create_project(org_id, name, ...)
"""

from datetime import date
from typing import Optional
from uuid import UUID

from src.domain.core import Project, ProjectResult, Workstream
from src.repositories.project_repository import ProjectRepository
from src.repositories.workstream_repository import WorkstreamRepository
from src.repositories.item_repository import ItemRepository
from src.services.aurora_service import AuroraService
from src.utils.logging import get_logger

logger = get_logger(__name__)


class ProjectService:
    """
    Service for project business logic.

    Coordinates between repositories and handles business rules.
    """

    def __init__(self, aurora: AuroraService):
        """
        Initialize project service.

        Args:
            aurora: Aurora database service.
        """
        self._aurora = aurora
        self._project_repo = ProjectRepository(aurora)
        self._workstream_repo = WorkstreamRepository(aurora)
        self._item_repo = ItemRepository(aurora)

    # =========================================================================
    # PROJECT CRUD
    # =========================================================================

    async def create_project(
        self,
        org_id: UUID,
        name: str,
        client_name: Optional[str] = None,
        project_start: Optional[date] = None,
        project_end: Optional[date] = None,
        workstreams: Optional[list[str]] = None,
    ) -> ProjectResult:
        """
        Create a new project with optional initial workstreams.

        Args:
            org_id: Organization UUID.
            name: Project name.
            client_name: Client/customer name (optional).
            project_start: Project start date (optional).
            project_end: Project end date (optional).
            workstreams: List of workstream names to create (optional).

        Returns:
            ProjectResult with created project or error.
        """
        # Validate dates if both provided
        if project_start and project_end and project_end < project_start:
            return ProjectResult(
                success=False,
                error="Project end date must be after start date",
            )

        # Create project
        project = await self._project_repo.create(
            org_id=org_id,
            name=name,
            client_name=client_name,
            project_start=project_start,
            project_end=project_end,
        )

        # Create initial workstreams if provided
        if workstreams:
            for index, ws_name in enumerate(workstreams):
                await self._workstream_repo.create(
                    project_id=project.id,
                    name=ws_name,
                    sort_order=index,
                )

        logger.info(
            "project_created",
            project_id=str(project.id),
            org_id=str(org_id),
            name=name,
            workstream_count=len(workstreams) if workstreams else 0,
        )

        return ProjectResult(success=True, project=project)

    async def get_project(self, project_id: UUID) -> Optional[Project]:
        """
        Get a project by ID.

        Args:
            project_id: Project UUID.

        Returns:
            Project if found, None otherwise.
        """
        return await self._project_repo.get_by_id(project_id)

    async def list_projects_for_user(
        self, user_id: UUID, org_id: UUID
    ) -> list[Project]:
        """
        Get all projects a user has access to.

        Args:
            user_id: User UUID.
            org_id: Organization UUID.

        Returns:
            List of projects the user has a role on.
        """
        return await self._project_repo.list_for_user(user_id, org_id)

    async def list_projects_for_org(self, org_id: UUID) -> list[Project]:
        """
        Get all projects in an organization.

        Args:
            org_id: Organization UUID.

        Returns:
            List of all active projects.
        """
        return await self._project_repo.get_by_org_id(org_id)

    async def update_project(
        self,
        project_id: UUID,
        name: Optional[str] = None,
        client_name: Optional[str] = None,
        project_start: Optional[date] = None,
        project_end: Optional[date] = None,
    ) -> ProjectResult:
        """
        Update a project.

        Args:
            project_id: Project UUID.
            name: New name (optional).
            client_name: New client name (optional).
            project_start: New start date (optional).
            project_end: New end date (optional).

        Returns:
            ProjectResult with updated project or error.
        """
        # Get existing project
        existing = await self._project_repo.get_by_id(project_id)
        if not existing:
            return ProjectResult(success=False, error="Project not found")

        # Validate dates
        start = project_start if project_start is not None else existing.project_start
        end = project_end if project_end is not None else existing.project_end
        if start and end and end < start:
            return ProjectResult(
                success=False,
                error="Project end date must be after start date",
            )

        # Update
        project = await self._project_repo.update(
            project_id=project_id,
            name=name,
            client_name=client_name,
            project_start=project_start,
            project_end=project_end,
        )

        if not project:
            return ProjectResult(success=False, error="Project not found")

        logger.info("project_updated", project_id=str(project_id))
        return ProjectResult(success=True, project=project)

    async def delete_project(self, project_id: UUID) -> ProjectResult:
        """
        Soft delete a project.

        Args:
            project_id: Project UUID.

        Returns:
            ProjectResult with success status.
        """
        deleted = await self._project_repo.soft_delete(project_id)
        if not deleted:
            return ProjectResult(success=False, error="Project not found")

        logger.info("project_deleted", project_id=str(project_id))
        return ProjectResult(success=True)

    # =========================================================================
    # PROJECT STATISTICS
    # =========================================================================

    async def get_item_count(
        self, project_id: UUID, include_drafts: bool = False
    ) -> int:
        """
        Get the number of items in a project.

        Args:
            project_id: Project UUID.
            include_drafts: Whether to include draft items.

        Returns:
            Item count.
        """
        return await self._item_repo.count_by_project_id(project_id, include_drafts)

    async def get_workstreams(self, project_id: UUID) -> list[Workstream]:
        """
        Get all workstreams for a project.

        Args:
            project_id: Project UUID.

        Returns:
            List of workstreams ordered by sort_order.
        """
        return await self._workstream_repo.get_by_project_id(project_id)

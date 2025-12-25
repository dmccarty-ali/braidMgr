"""
Workstream service for business logic.

Coordinates workstream operations between repositories.
Handles validation and business rules.

Usage:
    from src.services.workstream_service import WorkstreamService
    from src.services import services

    ws_svc = WorkstreamService(services.aurora)
    result = await ws_svc.create_workstream(project_id, name)
"""

from typing import Optional
from uuid import UUID

from src.domain.core import Workstream, WorkstreamResult
from src.repositories.project_repository import ProjectRepository
from src.repositories.workstream_repository import WorkstreamRepository
from src.services.aurora_service import AuroraService
from src.utils.logging import get_logger

logger = get_logger(__name__)


class WorkstreamService:
    """
    Service for workstream business logic.

    Coordinates between repositories and handles business rules.
    """

    def __init__(self, aurora: AuroraService):
        """
        Initialize workstream service.

        Args:
            aurora: Aurora database service.
        """
        self._aurora = aurora
        self._project_repo = ProjectRepository(aurora)
        self._workstream_repo = WorkstreamRepository(aurora)

    # =========================================================================
    # WORKSTREAM CRUD
    # =========================================================================

    async def create_workstream(
        self,
        project_id: UUID,
        name: str,
    ) -> WorkstreamResult:
        """
        Create a new workstream in a project.

        Args:
            project_id: Project UUID.
            name: Workstream name.

        Returns:
            WorkstreamResult with created workstream or error.
        """
        # Validate project exists
        project = await self._project_repo.get_by_id(project_id)
        if not project:
            return WorkstreamResult(success=False, error="Project not found")

        # Check for duplicate name
        if await self._workstream_repo.exists_by_name(project_id, name):
            return WorkstreamResult(
                success=False,
                error=f"Workstream '{name}' already exists in this project",
            )

        # Create workstream
        workstream = await self._workstream_repo.create(
            project_id=project_id,
            name=name,
        )

        logger.info(
            "workstream_created",
            workstream_id=str(workstream.id),
            project_id=str(project_id),
            name=name,
        )

        return WorkstreamResult(success=True, workstream=workstream)

    async def get_workstream(self, workstream_id: UUID) -> Optional[Workstream]:
        """
        Get a workstream by ID.

        Args:
            workstream_id: Workstream UUID.

        Returns:
            Workstream if found, None otherwise.
        """
        return await self._workstream_repo.get_by_id(workstream_id)

    async def list_workstreams(self, project_id: UUID) -> list[Workstream]:
        """
        Get all workstreams for a project.

        Args:
            project_id: Project UUID.

        Returns:
            List of workstreams ordered by sort_order.
        """
        return await self._workstream_repo.get_by_project_id(project_id)

    async def update_workstream(
        self,
        workstream_id: UUID,
        name: Optional[str] = None,
    ) -> WorkstreamResult:
        """
        Update a workstream.

        Args:
            workstream_id: Workstream UUID.
            name: New name (optional).

        Returns:
            WorkstreamResult with updated workstream or error.
        """
        # Get existing workstream
        existing = await self._workstream_repo.get_by_id(workstream_id)
        if not existing:
            return WorkstreamResult(success=False, error="Workstream not found")

        # Check for duplicate name if name is changing
        if name and name != existing.name:
            if await self._workstream_repo.exists_by_name(existing.project_id, name):
                return WorkstreamResult(
                    success=False,
                    error=f"Workstream '{name}' already exists in this project",
                )

        # Update
        workstream = await self._workstream_repo.update(
            workstream_id=workstream_id,
            name=name,
        )

        if not workstream:
            return WorkstreamResult(success=False, error="Workstream not found")

        logger.info("workstream_updated", workstream_id=str(workstream_id))
        return WorkstreamResult(success=True, workstream=workstream)

    async def delete_workstream(self, workstream_id: UUID) -> WorkstreamResult:
        """
        Delete a workstream.

        Note: Items using this workstream will have their
        workstream_id set to NULL.

        Args:
            workstream_id: Workstream UUID.

        Returns:
            WorkstreamResult with success status.
        """
        deleted = await self._workstream_repo.delete(workstream_id)
        if not deleted:
            return WorkstreamResult(success=False, error="Workstream not found")

        logger.info("workstream_deleted", workstream_id=str(workstream_id))
        return WorkstreamResult(success=True)

    async def reorder_workstreams(
        self,
        project_id: UUID,
        workstream_ids: list[UUID],
    ) -> list[Workstream]:
        """
        Reorder workstreams in a project.

        Args:
            project_id: Project UUID.
            workstream_ids: List of workstream IDs in desired order.

        Returns:
            Reordered list of workstreams.
        """
        await self._workstream_repo.reorder(project_id, workstream_ids)

        logger.info(
            "workstreams_reordered",
            project_id=str(project_id),
            count=len(workstream_ids),
        )

        return await self._workstream_repo.get_by_project_id(project_id)

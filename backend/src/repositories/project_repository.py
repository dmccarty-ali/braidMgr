"""
Project repository for database operations.

Handles all database access for projects.
Uses the AuroraService for query execution.

Usage:
    from src.repositories.project_repository import ProjectRepository
    from src.services import services

    repo = ProjectRepository(services.aurora)
    project = await repo.get_by_id(project_id)
"""

from datetime import date, datetime
from typing import Optional
from uuid import UUID

from src.domain.core import Project
from src.services.aurora_service import AuroraService
from src.utils.logging import get_logger

logger = get_logger(__name__)


class ProjectRepository:
    """
    Repository for project database operations.

    Provides CRUD operations for projects with soft delete support.
    """

    def __init__(self, aurora: AuroraService):
        """
        Initialize project repository.

        Args:
            aurora: Aurora database service for query execution.
        """
        self._aurora = aurora

    # =========================================================================
    # READ OPERATIONS
    # =========================================================================

    async def get_by_id(self, project_id: UUID) -> Optional[Project]:
        """
        Get a project by ID.

        Args:
            project_id: Project UUID.

        Returns:
            Project if found and not deleted, None otherwise.
        """
        row = await self._aurora.fetch_one(
            """
            SELECT id, organization_id, name, client_name, project_start,
                   project_end, next_item_num, indicators_updated,
                   created_at, updated_at, deleted_at
            FROM projects
            WHERE id = $1 AND deleted_at IS NULL
            """,
            project_id,
        )
        return self._row_to_project(row)

    async def get_by_org_id(self, org_id: UUID) -> list[Project]:
        """
        Get all projects for an organization.

        Args:
            org_id: Organization UUID.

        Returns:
            List of active projects for the organization.
        """
        rows = await self._aurora.fetch_all(
            """
            SELECT id, organization_id, name, client_name, project_start,
                   project_end, next_item_num, indicators_updated,
                   created_at, updated_at, deleted_at
            FROM projects
            WHERE organization_id = $1 AND deleted_at IS NULL
            ORDER BY name ASC
            """,
            org_id,
        )
        return [self._row_to_project(row) for row in rows]

    async def list_for_user(self, user_id: UUID, org_id: UUID) -> list[Project]:
        """
        Get all projects a user has access to in an organization.

        Args:
            user_id: User UUID.
            org_id: Organization UUID.

        Returns:
            List of projects the user has a role on.
        """
        rows = await self._aurora.fetch_all(
            """
            SELECT p.id, p.organization_id, p.name, p.client_name, p.project_start,
                   p.project_end, p.next_item_num, p.indicators_updated,
                   p.created_at, p.updated_at, p.deleted_at
            FROM projects p
            INNER JOIN user_project_roles upr ON upr.project_id = p.id
            WHERE upr.user_id = $1
              AND p.organization_id = $2
              AND p.deleted_at IS NULL
            ORDER BY p.name ASC
            """,
            user_id,
            org_id,
        )
        return [self._row_to_project(row) for row in rows]

    async def exists(self, project_id: UUID) -> bool:
        """
        Check if a project exists and is not deleted.

        Args:
            project_id: Project UUID.

        Returns:
            True if project exists and is active.
        """
        row = await self._aurora.fetch_one(
            """
            SELECT 1 FROM projects WHERE id = $1 AND deleted_at IS NULL
            """,
            project_id,
        )
        return row is not None

    # =========================================================================
    # WRITE OPERATIONS
    # =========================================================================

    async def create(
        self,
        org_id: UUID,
        name: str,
        client_name: Optional[str] = None,
        project_start: Optional[date] = None,
        project_end: Optional[date] = None,
    ) -> Project:
        """
        Create a new project.

        Args:
            org_id: Organization UUID.
            name: Project name.
            client_name: Client/customer name (optional).
            project_start: Project start date (optional).
            project_end: Project end date (optional).

        Returns:
            Created project.
        """
        row = await self._aurora.fetch_one(
            """
            INSERT INTO projects (organization_id, name, client_name, project_start, project_end)
            VALUES ($1, $2, $3, $4, $5)
            RETURNING id, organization_id, name, client_name, project_start,
                      project_end, next_item_num, indicators_updated,
                      created_at, updated_at, deleted_at
            """,
            org_id,
            name,
            client_name,
            project_start,
            project_end,
        )
        project = self._row_to_project(row)
        logger.info("project_created", project_id=str(project.id), name=name)
        return project

    async def update(
        self,
        project_id: UUID,
        name: Optional[str] = None,
        client_name: Optional[str] = None,
        project_start: Optional[date] = None,
        project_end: Optional[date] = None,
    ) -> Optional[Project]:
        """
        Update a project.

        Only updates fields that are provided (not None).

        Args:
            project_id: Project UUID.
            name: New name (optional).
            client_name: New client name (optional).
            project_start: New start date (optional).
            project_end: New end date (optional).

        Returns:
            Updated project, or None if not found.
        """
        # Build dynamic update query
        updates = []
        params = []
        param_num = 1

        if name is not None:
            updates.append(f"name = ${param_num}")
            params.append(name)
            param_num += 1

        if client_name is not None:
            updates.append(f"client_name = ${param_num}")
            params.append(client_name)
            param_num += 1

        if project_start is not None:
            updates.append(f"project_start = ${param_num}")
            params.append(project_start)
            param_num += 1

        if project_end is not None:
            updates.append(f"project_end = ${param_num}")
            params.append(project_end)
            param_num += 1

        if not updates:
            return await self.get_by_id(project_id)

        updates.append("updated_at = now()")
        params.append(project_id)

        query = f"""
            UPDATE projects
            SET {", ".join(updates)}
            WHERE id = ${param_num} AND deleted_at IS NULL
            RETURNING id, organization_id, name, client_name, project_start,
                      project_end, next_item_num, indicators_updated,
                      created_at, updated_at, deleted_at
        """

        row = await self._aurora.fetch_one(query, *params)
        if row:
            logger.info("project_updated", project_id=str(project_id))
        return self._row_to_project(row)

    async def soft_delete(self, project_id: UUID) -> bool:
        """
        Soft delete a project.

        Sets deleted_at timestamp instead of removing the record.

        Args:
            project_id: Project UUID.

        Returns:
            True if project was deleted, False if not found.
        """
        result = await self._aurora.execute(
            """
            UPDATE projects
            SET deleted_at = now(), updated_at = now()
            WHERE id = $1 AND deleted_at IS NULL
            """,
            project_id,
        )
        deleted = result == "UPDATE 1"
        if deleted:
            logger.info("project_deleted", project_id=str(project_id))
        return deleted

    async def increment_item_num(self, project_id: UUID) -> int:
        """
        Atomically increment and return the next item number.

        This is used when creating new items to ensure unique item numbers.

        Args:
            project_id: Project UUID.

        Returns:
            The item number to use (before increment).

        Raises:
            ValueError: If project not found.
        """
        row = await self._aurora.fetch_one(
            """
            UPDATE projects
            SET next_item_num = next_item_num + 1, updated_at = now()
            WHERE id = $1 AND deleted_at IS NULL
            RETURNING next_item_num - 1 as item_num
            """,
            project_id,
        )
        if row is None:
            raise ValueError(f"Project not found: {project_id}")
        return row["item_num"]

    async def update_indicators_timestamp(self, project_id: UUID) -> None:
        """
        Update the indicators_updated timestamp.

        Called after batch indicator recalculation.

        Args:
            project_id: Project UUID.
        """
        await self._aurora.execute(
            """
            UPDATE projects
            SET indicators_updated = now(), updated_at = now()
            WHERE id = $1 AND deleted_at IS NULL
            """,
            project_id,
        )

    # =========================================================================
    # HELPERS
    # =========================================================================

    @staticmethod
    def _row_to_project(row) -> Optional[Project]:
        """
        Convert a database row to a Project dataclass.

        Args:
            row: Database row dict.

        Returns:
            Project instance, or None if row is None.
        """
        if row is None:
            return None

        return Project(
            id=row["id"],
            organization_id=row["organization_id"],
            name=row["name"],
            client_name=row["client_name"],
            project_start=row["project_start"],
            project_end=row["project_end"],
            next_item_num=row["next_item_num"],
            indicators_updated=row["indicators_updated"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            deleted_at=row["deleted_at"],
        )

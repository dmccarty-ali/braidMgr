"""
User project role repository for database operations.

Handles database access for user_project_roles table.
Used by auth dependencies to check project-level permissions.

Usage:
    from src.repositories.user_project_role_repository import UserProjectRoleRepository
    from src.services import services

    repo = UserProjectRoleRepository(services.aurora)
    role = await repo.get_user_role(user_id, project_id)
"""

from typing import Optional
from uuid import UUID

from src.domain.auth import ProjectRole
from src.services.aurora_service import AuroraService
from src.utils.logging import get_logger

logger = get_logger(__name__)


class UserProjectRoleRepository:
    """
    Repository for user project role database operations.

    Provides read operations for checking project-level permissions.
    """

    def __init__(self, aurora: AuroraService):
        """
        Initialize user project role repository.

        Args:
            aurora: Aurora database service for query execution.
        """
        self._aurora = aurora

    # =========================================================================
    # READ OPERATIONS
    # =========================================================================

    async def get_user_role(
        self,
        user_id: UUID,
        project_id: UUID,
    ) -> Optional[ProjectRole]:
        """
        Get a user's role on a project.

        Args:
            user_id: User UUID.
            project_id: Project UUID.

        Returns:
            ProjectRole if user has a role on the project, None otherwise.
        """
        row = await self._aurora.fetch_one(
            """
            SELECT role FROM user_project_roles
            WHERE user_id = $1 AND project_id = $2
            """,
            user_id,
            project_id,
        )
        if row is None:
            return None
        return ProjectRole(row["role"])

    async def has_access(self, user_id: UUID, project_id: UUID) -> bool:
        """
        Check if a user has any role on a project.

        Args:
            user_id: User UUID.
            project_id: Project UUID.

        Returns:
            True if user has any role on the project.
        """
        row = await self._aurora.fetch_one(
            """
            SELECT 1 FROM user_project_roles
            WHERE user_id = $1 AND project_id = $2
            """,
            user_id,
            project_id,
        )
        return row is not None

    async def has_role(
        self,
        user_id: UUID,
        project_id: UUID,
        roles: list[ProjectRole],
    ) -> bool:
        """
        Check if a user has one of the specified roles on a project.

        Args:
            user_id: User UUID.
            project_id: Project UUID.
            roles: List of allowed roles.

        Returns:
            True if user has one of the specified roles.
        """
        role_values = [r.value for r in roles]
        row = await self._aurora.fetch_one(
            """
            SELECT 1 FROM user_project_roles
            WHERE user_id = $1 AND project_id = $2 AND role = ANY($3)
            """,
            user_id,
            project_id,
            role_values,
        )
        return row is not None

    # =========================================================================
    # WRITE OPERATIONS
    # =========================================================================

    async def assign_role(
        self,
        user_id: UUID,
        project_id: UUID,
        role: ProjectRole,
    ) -> None:
        """
        Assign a role to a user on a project.

        If the user already has a role, it will be updated.

        Args:
            user_id: User UUID.
            project_id: Project UUID.
            role: Role to assign.
        """
        await self._aurora.execute(
            """
            INSERT INTO user_project_roles (user_id, project_id, role)
            VALUES ($1, $2, $3)
            ON CONFLICT (user_id, project_id) DO UPDATE SET role = $3
            """,
            user_id,
            project_id,
            role.value,
        )
        logger.info(
            "project_role_assigned",
            user_id=str(user_id),
            project_id=str(project_id),
            role=role.value,
        )

    async def remove_role(self, user_id: UUID, project_id: UUID) -> bool:
        """
        Remove a user's role from a project.

        Args:
            user_id: User UUID.
            project_id: Project UUID.

        Returns:
            True if role was removed, False if not found.
        """
        result = await self._aurora.execute(
            """
            DELETE FROM user_project_roles
            WHERE user_id = $1 AND project_id = $2
            """,
            user_id,
            project_id,
        )
        removed = result == "DELETE 1"
        if removed:
            logger.info(
                "project_role_removed",
                user_id=str(user_id),
                project_id=str(project_id),
            )
        return removed

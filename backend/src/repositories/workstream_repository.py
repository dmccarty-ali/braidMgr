"""
Workstream repository for database operations.

Handles all database access for workstreams.
Uses the AuroraService for query execution.

Usage:
    from src.repositories.workstream_repository import WorkstreamRepository
    from src.services import services

    repo = WorkstreamRepository(services.aurora)
    workstreams = await repo.get_by_project_id(project_id)
"""

from typing import Optional
from uuid import UUID

from src.domain.core import Workstream
from src.services.aurora_service import AuroraService
from src.utils.logging import get_logger

logger = get_logger(__name__)


class WorkstreamRepository:
    """
    Repository for workstream database operations.

    Provides CRUD operations for workstreams with ordering support.
    """

    def __init__(self, aurora: AuroraService):
        """
        Initialize workstream repository.

        Args:
            aurora: Aurora database service for query execution.
        """
        self._aurora = aurora

    # =========================================================================
    # READ OPERATIONS
    # =========================================================================

    async def get_by_id(self, workstream_id: UUID) -> Optional[Workstream]:
        """
        Get a workstream by ID.

        Args:
            workstream_id: Workstream UUID.

        Returns:
            Workstream if found, None otherwise.
        """
        row = await self._aurora.fetch_one(
            """
            SELECT id, project_id, name, sort_order
            FROM workstreams
            WHERE id = $1
            """,
            workstream_id,
        )
        return self._row_to_workstream(row)

    async def get_by_project_id(self, project_id: UUID) -> list[Workstream]:
        """
        Get all workstreams for a project.

        Args:
            project_id: Project UUID.

        Returns:
            List of workstreams ordered by sort_order.
        """
        rows = await self._aurora.fetch_all(
            """
            SELECT id, project_id, name, sort_order
            FROM workstreams
            WHERE project_id = $1
            ORDER BY sort_order ASC, name ASC
            """,
            project_id,
        )
        return [self._row_to_workstream(row) for row in rows]

    async def exists_by_name(self, project_id: UUID, name: str) -> bool:
        """
        Check if a workstream with the given name exists in the project.

        Args:
            project_id: Project UUID.
            name: Workstream name.

        Returns:
            True if workstream exists.
        """
        row = await self._aurora.fetch_one(
            """
            SELECT 1 FROM workstreams
            WHERE project_id = $1 AND name = $2
            """,
            project_id,
            name,
        )
        return row is not None

    # =========================================================================
    # WRITE OPERATIONS
    # =========================================================================

    async def create(
        self,
        project_id: UUID,
        name: str,
        sort_order: Optional[int] = None,
    ) -> Workstream:
        """
        Create a new workstream.

        Args:
            project_id: Project UUID.
            name: Workstream name.
            sort_order: Sort order (defaults to next available).

        Returns:
            Created workstream.
        """
        # If no sort_order provided, use next available
        if sort_order is None:
            max_row = await self._aurora.fetch_one(
                """
                SELECT COALESCE(MAX(sort_order), -1) + 1 as next_order
                FROM workstreams
                WHERE project_id = $1
                """,
                project_id,
            )
            sort_order = max_row["next_order"] if max_row else 0

        row = await self._aurora.fetch_one(
            """
            INSERT INTO workstreams (project_id, name, sort_order)
            VALUES ($1, $2, $3)
            RETURNING id, project_id, name, sort_order
            """,
            project_id,
            name,
            sort_order,
        )
        workstream = self._row_to_workstream(row)
        logger.info(
            "workstream_created",
            workstream_id=str(workstream.id),
            project_id=str(project_id),
            name=name,
        )
        return workstream

    async def update(
        self,
        workstream_id: UUID,
        name: Optional[str] = None,
        sort_order: Optional[int] = None,
    ) -> Optional[Workstream]:
        """
        Update a workstream.

        Only updates fields that are provided (not None).

        Args:
            workstream_id: Workstream UUID.
            name: New name (optional).
            sort_order: New sort order (optional).

        Returns:
            Updated workstream, or None if not found.
        """
        updates = []
        params = []
        param_num = 1

        if name is not None:
            updates.append(f"name = ${param_num}")
            params.append(name)
            param_num += 1

        if sort_order is not None:
            updates.append(f"sort_order = ${param_num}")
            params.append(sort_order)
            param_num += 1

        if not updates:
            return await self.get_by_id(workstream_id)

        params.append(workstream_id)

        query = f"""
            UPDATE workstreams
            SET {", ".join(updates)}
            WHERE id = ${param_num}
            RETURNING id, project_id, name, sort_order
        """

        row = await self._aurora.fetch_one(query, *params)
        if row:
            logger.info("workstream_updated", workstream_id=str(workstream_id))
        return self._row_to_workstream(row)

    async def delete(self, workstream_id: UUID) -> bool:
        """
        Delete a workstream.

        Note: Items referencing this workstream will have their
        workstream_id set to NULL (ON DELETE SET NULL).

        Args:
            workstream_id: Workstream UUID.

        Returns:
            True if workstream was deleted, False if not found.
        """
        result = await self._aurora.execute(
            """
            DELETE FROM workstreams WHERE id = $1
            """,
            workstream_id,
        )
        deleted = result == "DELETE 1"
        if deleted:
            logger.info("workstream_deleted", workstream_id=str(workstream_id))
        return deleted

    async def reorder(self, project_id: UUID, workstream_ids: list[UUID]) -> bool:
        """
        Reorder workstreams in a project.

        Sets sort_order based on position in the provided list.

        Args:
            project_id: Project UUID.
            workstream_ids: List of workstream IDs in desired order.

        Returns:
            True if all updates succeeded.
        """
        for index, ws_id in enumerate(workstream_ids):
            await self._aurora.execute(
                """
                UPDATE workstreams
                SET sort_order = $1
                WHERE id = $2 AND project_id = $3
                """,
                index,
                ws_id,
                project_id,
            )

        logger.info(
            "workstreams_reordered",
            project_id=str(project_id),
            count=len(workstream_ids),
        )
        return True

    # =========================================================================
    # HELPERS
    # =========================================================================

    @staticmethod
    def _row_to_workstream(row) -> Optional[Workstream]:
        """
        Convert a database row to a Workstream dataclass.

        Args:
            row: Database row dict.

        Returns:
            Workstream instance, or None if row is None.
        """
        if row is None:
            return None

        return Workstream(
            id=row["id"],
            project_id=row["project_id"],
            name=row["name"],
            sort_order=row["sort_order"],
        )

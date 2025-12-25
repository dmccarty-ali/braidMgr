"""
Item dependency repository for database operations.

Handles all database access for item dependencies (predecessor links).
Uses the AuroraService for query execution.

Usage:
    from src.repositories.item_dependency_repository import ItemDependencyRepository
    from src.services import services

    repo = ItemDependencyRepository(services.aurora)
    deps = await repo.get_dependencies(item_id)
"""

from typing import Optional
from uuid import UUID

from src.domain.core import ItemDependency
from src.services.aurora_service import AuroraService
from src.utils.logging import get_logger

logger = get_logger(__name__)


class ItemDependencyRepository:
    """
    Repository for item dependency database operations.

    Provides operations for managing predecessor/successor relationships.
    """

    def __init__(self, aurora: AuroraService):
        """
        Initialize item dependency repository.

        Args:
            aurora: Aurora database service for query execution.
        """
        self._aurora = aurora

    # =========================================================================
    # READ OPERATIONS
    # =========================================================================

    async def get_dependencies(self, item_id: UUID) -> list[ItemDependency]:
        """
        Get all items that this item depends on (predecessors).

        Args:
            item_id: Item UUID.

        Returns:
            List of dependencies where this item is the dependent.
        """
        rows = await self._aurora.fetch_all(
            """
            SELECT item_id, depends_on_id
            FROM item_dependencies
            WHERE item_id = $1
            """,
            item_id,
        )
        return [self._row_to_dependency(row) for row in rows]

    async def get_dependents(self, item_id: UUID) -> list[ItemDependency]:
        """
        Get all items that depend on this item (successors).

        Args:
            item_id: Item UUID.

        Returns:
            List of dependencies where this item is the prerequisite.
        """
        rows = await self._aurora.fetch_all(
            """
            SELECT item_id, depends_on_id
            FROM item_dependencies
            WHERE depends_on_id = $1
            """,
            item_id,
        )
        return [self._row_to_dependency(row) for row in rows]

    async def exists(self, item_id: UUID, depends_on_id: UUID) -> bool:
        """
        Check if a dependency exists.

        Args:
            item_id: Dependent item UUID.
            depends_on_id: Prerequisite item UUID.

        Returns:
            True if dependency exists.
        """
        row = await self._aurora.fetch_one(
            """
            SELECT 1 FROM item_dependencies
            WHERE item_id = $1 AND depends_on_id = $2
            """,
            item_id,
            depends_on_id,
        )
        return row is not None

    async def would_create_cycle(
        self, item_id: UUID, depends_on_id: UUID
    ) -> bool:
        """
        Check if adding this dependency would create a cycle.

        Uses recursive CTE to detect if depends_on_id eventually
        depends on item_id.

        Args:
            item_id: Item that would become dependent.
            depends_on_id: Item that would become prerequisite.

        Returns:
            True if adding this would create a cycle.
        """
        # If item_id depends on depends_on_id, and depends_on_id (transitively)
        # depends on item_id, we have a cycle.
        row = await self._aurora.fetch_one(
            """
            WITH RECURSIVE dep_chain AS (
                -- Base: direct dependencies of depends_on_id
                SELECT item_id, depends_on_id
                FROM item_dependencies
                WHERE item_id = $1

                UNION

                -- Recursive: follow the chain
                SELECT d.item_id, d.depends_on_id
                FROM item_dependencies d
                INNER JOIN dep_chain c ON d.item_id = c.depends_on_id
            )
            SELECT 1 FROM dep_chain WHERE depends_on_id = $2
            """,
            depends_on_id,
            item_id,
        )
        return row is not None

    # =========================================================================
    # WRITE OPERATIONS
    # =========================================================================

    async def add(self, item_id: UUID, depends_on_id: UUID) -> ItemDependency:
        """
        Add a dependency between items.

        Args:
            item_id: Dependent item UUID.
            depends_on_id: Prerequisite item UUID.

        Returns:
            Created dependency.

        Raises:
            ValueError: If dependency already exists or would create cycle.
        """
        # Check for existing
        if await self.exists(item_id, depends_on_id):
            raise ValueError("Dependency already exists")

        # Check for cycle
        if await self.would_create_cycle(item_id, depends_on_id):
            raise ValueError("Adding this dependency would create a cycle")

        await self._aurora.execute(
            """
            INSERT INTO item_dependencies (item_id, depends_on_id)
            VALUES ($1, $2)
            """,
            item_id,
            depends_on_id,
        )

        logger.info(
            "item_dependency_added",
            item_id=str(item_id),
            depends_on_id=str(depends_on_id),
        )
        return ItemDependency(item_id=item_id, depends_on_id=depends_on_id)

    async def remove(self, item_id: UUID, depends_on_id: UUID) -> bool:
        """
        Remove a dependency between items.

        Args:
            item_id: Dependent item UUID.
            depends_on_id: Prerequisite item UUID.

        Returns:
            True if dependency was removed, False if not found.
        """
        result = await self._aurora.execute(
            """
            DELETE FROM item_dependencies
            WHERE item_id = $1 AND depends_on_id = $2
            """,
            item_id,
            depends_on_id,
        )
        deleted = result == "DELETE 1"
        if deleted:
            logger.info(
                "item_dependency_removed",
                item_id=str(item_id),
                depends_on_id=str(depends_on_id),
            )
        return deleted

    async def remove_all_for_item(self, item_id: UUID) -> int:
        """
        Remove all dependencies for an item (both directions).

        Called when an item is deleted.

        Args:
            item_id: Item UUID.

        Returns:
            Number of dependencies removed.
        """
        result = await self._aurora.execute(
            """
            DELETE FROM item_dependencies
            WHERE item_id = $1 OR depends_on_id = $1
            """,
            item_id,
        )
        # Parse count from result like "DELETE 5"
        count = int(result.split()[1]) if result else 0
        if count > 0:
            logger.info(
                "item_dependencies_cleared",
                item_id=str(item_id),
                count=count,
            )
        return count

    # =========================================================================
    # HELPERS
    # =========================================================================

    @staticmethod
    def _row_to_dependency(row) -> Optional[ItemDependency]:
        """
        Convert a database row to an ItemDependency dataclass.

        Args:
            row: Database row dict.

        Returns:
            ItemDependency instance, or None if row is None.
        """
        if row is None:
            return None

        return ItemDependency(
            item_id=row["item_id"],
            depends_on_id=row["depends_on_id"],
        )

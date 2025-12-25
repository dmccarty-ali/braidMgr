"""
Item note repository for database operations.

Handles all database access for item notes (comments).
Uses the AuroraService for query execution.

Usage:
    from src.repositories.item_note_repository import ItemNoteRepository
    from src.services import services

    repo = ItemNoteRepository(services.aurora)
    notes = await repo.get_by_item_id(item_id)
"""

from datetime import date, datetime
from typing import Optional
from uuid import UUID

from src.domain.core import ItemNote
from src.services.aurora_service import AuroraService
from src.utils.logging import get_logger

logger = get_logger(__name__)


class ItemNoteRepository:
    """
    Repository for item note database operations.

    Provides CRUD operations for item notes.
    """

    def __init__(self, aurora: AuroraService):
        """
        Initialize item note repository.

        Args:
            aurora: Aurora database service for query execution.
        """
        self._aurora = aurora

    # =========================================================================
    # READ OPERATIONS
    # =========================================================================

    async def get_by_id(self, note_id: UUID) -> Optional[ItemNote]:
        """
        Get a note by ID.

        Args:
            note_id: Note UUID.

        Returns:
            ItemNote if found, None otherwise.
        """
        row = await self._aurora.fetch_one(
            """
            SELECT id, item_id, note_date, content, created_by, created_at
            FROM item_notes
            WHERE id = $1
            """,
            note_id,
        )
        return self._row_to_note(row)

    async def get_by_item_id(self, item_id: UUID) -> list[ItemNote]:
        """
        Get all notes for an item.

        Args:
            item_id: Item UUID.

        Returns:
            List of notes ordered by date descending.
        """
        rows = await self._aurora.fetch_all(
            """
            SELECT id, item_id, note_date, content, created_by, created_at
            FROM item_notes
            WHERE item_id = $1
            ORDER BY note_date DESC, created_at DESC
            """,
            item_id,
        )
        return [self._row_to_note(row) for row in rows]

    # =========================================================================
    # WRITE OPERATIONS
    # =========================================================================

    async def create(
        self,
        item_id: UUID,
        note_date: date,
        content: str,
        created_by: Optional[UUID] = None,
    ) -> ItemNote:
        """
        Create a new note.

        Args:
            item_id: Item UUID.
            note_date: Date of the note.
            content: Note text content.
            created_by: User who created the note (optional).

        Returns:
            Created note.
        """
        row = await self._aurora.fetch_one(
            """
            INSERT INTO item_notes (item_id, note_date, content, created_by)
            VALUES ($1, $2, $3, $4)
            RETURNING id, item_id, note_date, content, created_by, created_at
            """,
            item_id,
            note_date,
            content,
            created_by,
        )
        note = self._row_to_note(row)
        logger.info(
            "item_note_created",
            note_id=str(note.id),
            item_id=str(item_id),
        )
        return note

    async def update(
        self,
        note_id: UUID,
        content: Optional[str] = None,
        note_date: Optional[date] = None,
    ) -> Optional[ItemNote]:
        """
        Update a note.

        Only updates fields that are provided (not None).

        Args:
            note_id: Note UUID.
            content: New content (optional).
            note_date: New date (optional).

        Returns:
            Updated note, or None if not found.
        """
        updates = []
        params = []
        param_num = 1

        if content is not None:
            updates.append(f"content = ${param_num}")
            params.append(content)
            param_num += 1

        if note_date is not None:
            updates.append(f"note_date = ${param_num}")
            params.append(note_date)
            param_num += 1

        if not updates:
            return await self.get_by_id(note_id)

        params.append(note_id)

        query = f"""
            UPDATE item_notes
            SET {", ".join(updates)}
            WHERE id = ${param_num}
            RETURNING id, item_id, note_date, content, created_by, created_at
        """

        row = await self._aurora.fetch_one(query, *params)
        if row:
            logger.info("item_note_updated", note_id=str(note_id))
        return self._row_to_note(row)

    async def delete(self, note_id: UUID) -> bool:
        """
        Delete a note.

        Args:
            note_id: Note UUID.

        Returns:
            True if note was deleted, False if not found.
        """
        result = await self._aurora.execute(
            """
            DELETE FROM item_notes WHERE id = $1
            """,
            note_id,
        )
        deleted = result == "DELETE 1"
        if deleted:
            logger.info("item_note_deleted", note_id=str(note_id))
        return deleted

    # =========================================================================
    # HELPERS
    # =========================================================================

    @staticmethod
    def _row_to_note(row) -> Optional[ItemNote]:
        """
        Convert a database row to an ItemNote dataclass.

        Args:
            row: Database row dict.

        Returns:
            ItemNote instance, or None if row is None.
        """
        if row is None:
            return None

        return ItemNote(
            id=row["id"],
            item_id=row["item_id"],
            note_date=row["note_date"],
            content=row["content"],
            created_by=row["created_by"],
            created_at=row["created_at"],
        )

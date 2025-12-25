"""
Core domain models for braidMgr.

Contains dataclasses representing core project management entities:
- Project: Container for items and workstreams
- Item: RAID log entry (Risk, Action, Issue, Decision, etc.)
- Workstream: Project-specific grouping of items
- ItemNote: Dated comment on an item
- ItemDependency: Predecessor/successor link between items

Usage:
    from src.domain.core import Project, Item, Workstream, ItemType, Indicator
"""

from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import Optional
from uuid import UUID


# =============================================================================
# ENUMS
# =============================================================================
# Enums matching database enum types from migration 001.
# Values must match PostgreSQL ENUM values exactly.
# =============================================================================


class ItemType(str, Enum):
    """
    Item type enum - the seven RAID+ item types.

    Matches item_type_enum in PostgreSQL.
    Values include display-friendly names with spaces.
    """

    BUDGET = "Budget"
    RISK = "Risk"
    ACTION_ITEM = "Action Item"
    ISSUE = "Issue"
    DECISION = "Decision"
    DELIVERABLE = "Deliverable"
    PLAN_ITEM = "Plan Item"


class Indicator(str, Enum):
    """
    Indicator enum - calculated status indicators.

    Matches indicator_enum in PostgreSQL.
    Ordered by severity (most severe first).
    """

    BEYOND_DEADLINE = "Beyond Deadline!!!"
    LATE_FINISH = "Late Finish!!"
    LATE_START = "Late Start!!"
    TRENDING_LATE = "Trending Late!"
    FINISHING_SOON = "Finishing Soon!"
    STARTING_SOON = "Starting Soon!"
    IN_PROGRESS = "In Progress"
    NOT_STARTED = "Not Started"
    COMPLETED_RECENTLY = "Completed Recently"
    COMPLETED = "Completed"


# =============================================================================
# PROJECT ENTITY
# =============================================================================


@dataclass
class Project:
    """
    Project entity - container for items and workstreams.

    Represents a RAID log project in the system.
    Maps to the 'projects' table in PostgreSQL.

    Attributes:
        id: Unique project identifier
        organization_id: Owning organization
        name: Project name
        client_name: Client/customer name (optional)
        project_start: Project start date (optional)
        project_end: Project end date (optional)
        next_item_num: Next auto-increment number for items
        indicators_updated: Last indicator recalculation timestamp
        created_at: Creation timestamp
        updated_at: Last update timestamp
        deleted_at: Soft delete timestamp (None if active)
    """

    id: UUID
    organization_id: UUID
    name: str
    client_name: Optional[str] = None
    project_start: Optional[date] = None
    project_end: Optional[date] = None
    next_item_num: int = 1
    indicators_updated: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None

    @property
    def is_active(self) -> bool:
        """Project is active (not soft-deleted)."""
        return self.deleted_at is None

    @property
    def has_dates(self) -> bool:
        """Project has start and end dates defined."""
        return self.project_start is not None and self.project_end is not None


# =============================================================================
# WORKSTREAM ENTITY
# =============================================================================


@dataclass
class Workstream:
    """
    Workstream entity - project-specific grouping.

    Represents a logical grouping of items within a project.
    Maps to the 'workstreams' table in PostgreSQL.

    Attributes:
        id: Unique workstream identifier
        project_id: Parent project
        name: Workstream name
        sort_order: Display order (0-based)
    """

    id: UUID
    project_id: UUID
    name: str
    sort_order: int = 0


# =============================================================================
# ITEM ENTITY
# =============================================================================


@dataclass
class Item:
    """
    Item entity - RAID log entry.

    Represents a single item (Risk, Action, Issue, Decision, etc.)
    Maps to the 'items' table in PostgreSQL.

    Attributes:
        id: Unique item identifier
        project_id: Parent project
        item_num: Human-readable number (unique per project)
        type: Item type (Risk, Action, Issue, etc.)
        title: Item title
        description: Detailed description (optional)
        workstream_id: Associated workstream (optional)
        assigned_to: Assignee name (optional)
        start_date: Planned start date (optional)
        finish_date: Planned finish date (optional)
        duration_days: Estimated duration (optional)
        deadline: Hard deadline date (optional)
        draft: Whether item is in draft mode
        client_visible: Whether item is visible to client
        percent_complete: Completion percentage (0-100)
        indicator: Calculated status indicator (optional)
        priority: Priority level (optional)
        rpt_out: Report codes list (optional)
        budget_amount: Budget amount for Budget items (optional)
        created_at: Creation timestamp
        updated_at: Last update timestamp
        deleted_at: Soft delete timestamp (None if active)
    """

    id: UUID
    project_id: UUID
    item_num: int
    type: ItemType
    title: str
    description: Optional[str] = None
    workstream_id: Optional[UUID] = None
    assigned_to: Optional[str] = None
    start_date: Optional[date] = None
    finish_date: Optional[date] = None
    duration_days: Optional[int] = None
    deadline: Optional[date] = None
    draft: bool = False
    client_visible: bool = True
    percent_complete: int = 0
    indicator: Optional[Indicator] = None
    priority: Optional[str] = None
    rpt_out: Optional[list[str]] = None
    budget_amount: Optional[Decimal] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None

    @property
    def is_active(self) -> bool:
        """Item is active (not soft-deleted)."""
        return self.deleted_at is None

    @property
    def is_draft(self) -> bool:
        """Item is in draft mode."""
        return self.draft

    @property
    def is_complete(self) -> bool:
        """Item is 100% complete."""
        return self.percent_complete >= 100

    @property
    def has_dates(self) -> bool:
        """Item has start and finish dates defined."""
        return self.start_date is not None and self.finish_date is not None

    @property
    def has_deadline(self) -> bool:
        """Item has a deadline defined."""
        return self.deadline is not None


# =============================================================================
# ITEM NOTE ENTITY
# =============================================================================


@dataclass
class ItemNote:
    """
    Item note entity - dated comment on an item.

    Represents a note/comment attached to an item.
    Maps to the 'item_notes' table in PostgreSQL.

    Attributes:
        id: Unique note identifier
        item_id: Parent item
        note_date: Date of the note
        content: Note text content
        created_by: User who created the note (optional)
        created_at: Creation timestamp
    """

    id: UUID
    item_id: UUID
    note_date: date
    content: str
    created_by: Optional[UUID] = None
    created_at: Optional[datetime] = None


# =============================================================================
# ITEM DEPENDENCY ENTITY
# =============================================================================


@dataclass
class ItemDependency:
    """
    Item dependency - predecessor/successor link.

    Represents a dependency between two items.
    Maps to the 'item_dependencies' table in PostgreSQL.

    Attributes:
        item_id: The dependent item (successor)
        depends_on_id: The prerequisite item (predecessor)
    """

    item_id: UUID
    depends_on_id: UUID


# =============================================================================
# RESULT DATACLASSES
# =============================================================================
# Result types for service operations following the success/error pattern.
# =============================================================================


@dataclass
class ProjectResult:
    """
    Result of a project operation.

    Returned by project service after create/update/delete.

    Attributes:
        success: Whether operation succeeded
        project: Resulting project (if success)
        error: Error message (if failure)
    """

    success: bool
    project: Optional[Project] = None
    error: Optional[str] = None


@dataclass
class ItemResult:
    """
    Result of an item operation.

    Returned by item service after create/update/delete.

    Attributes:
        success: Whether operation succeeded
        item: Resulting item (if success)
        error: Error message (if failure)
    """

    success: bool
    item: Optional[Item] = None
    error: Optional[str] = None


@dataclass
class WorkstreamResult:
    """
    Result of a workstream operation.

    Returned by workstream service after create/update/delete.

    Attributes:
        success: Whether operation succeeded
        workstream: Resulting workstream (if success)
        error: Error message (if failure)
    """

    success: bool
    workstream: Optional[Workstream] = None
    error: Optional[str] = None


@dataclass
class ItemNoteResult:
    """
    Result of an item note operation.

    Returned by item note service after create/update/delete.

    Attributes:
        success: Whether operation succeeded
        note: Resulting note (if success)
        error: Error message (if failure)
    """

    success: bool
    note: Optional[ItemNote] = None
    error: Optional[str] = None

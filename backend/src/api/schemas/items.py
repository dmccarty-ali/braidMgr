"""
Pydantic schemas for item API endpoints.

Defines request and response models for item CRUD operations.

Usage:
    from src.api.schemas.items import ItemCreateRequest, ItemResponse
"""

from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from src.domain.core import ItemType, Indicator


# =============================================================================
# REQUEST SCHEMAS
# =============================================================================


class ItemCreateRequest(BaseModel):
    """Request body for creating an item."""

    type: ItemType = Field(
        ...,
        description="Item type (Budget, Risk, Action Item, Issue, Decision, Deliverable, Plan Item)",
        examples=["Risk"],
    )
    title: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="Item title",
        examples=["Database migration may exceed timeline"],
    )
    description: Optional[str] = Field(
        None,
        description="Detailed description",
        examples=["The legacy database has complex schema that may require additional migration time."],
    )
    workstream_id: Optional[UUID] = Field(
        None,
        description="Associated workstream ID",
    )
    assigned_to: Optional[str] = Field(
        None,
        max_length=255,
        description="Assignee name",
        examples=["John Smith"],
    )
    start_date: Optional[date] = Field(
        None,
        description="Planned start date",
        examples=["2024-02-01"],
    )
    finish_date: Optional[date] = Field(
        None,
        description="Planned finish date",
        examples=["2024-02-15"],
    )
    duration_days: Optional[int] = Field(
        None,
        ge=0,
        description="Estimated duration in days",
        examples=[10],
    )
    deadline: Optional[date] = Field(
        None,
        description="Hard deadline date",
        examples=["2024-02-28"],
    )
    draft: bool = Field(
        False,
        description="Whether item is in draft mode",
    )
    client_visible: bool = Field(
        True,
        description="Whether item is visible to client",
    )
    percent_complete: int = Field(
        0,
        ge=0,
        le=100,
        description="Completion percentage (0-100)",
        examples=[25],
    )
    priority: Optional[str] = Field(
        None,
        max_length=50,
        description="Priority level",
        examples=["High"],
    )
    rpt_out: Optional[list[str]] = Field(
        None,
        description="Report codes",
        examples=[["SR", "CL"]],
    )
    budget_amount: Optional[Decimal] = Field(
        None,
        ge=0,
        description="Budget amount for Budget items",
        examples=[50000.00],
    )


class ItemUpdateRequest(BaseModel):
    """Request body for updating an item."""

    title: Optional[str] = Field(
        None,
        min_length=1,
        max_length=500,
        description="Item title",
    )
    description: Optional[str] = Field(
        None,
        description="Detailed description",
    )
    workstream_id: Optional[UUID] = Field(
        None,
        description="Associated workstream ID",
    )
    assigned_to: Optional[str] = Field(
        None,
        max_length=255,
        description="Assignee name",
    )
    start_date: Optional[date] = Field(
        None,
        description="Planned start date",
    )
    finish_date: Optional[date] = Field(
        None,
        description="Planned finish date",
    )
    duration_days: Optional[int] = Field(
        None,
        ge=0,
        description="Estimated duration in days",
    )
    deadline: Optional[date] = Field(
        None,
        description="Hard deadline date",
    )
    draft: Optional[bool] = Field(
        None,
        description="Whether item is in draft mode",
    )
    client_visible: Optional[bool] = Field(
        None,
        description="Whether item is visible to client",
    )
    percent_complete: Optional[int] = Field(
        None,
        ge=0,
        le=100,
        description="Completion percentage (0-100)",
    )
    priority: Optional[str] = Field(
        None,
        max_length=50,
        description="Priority level",
    )
    rpt_out: Optional[list[str]] = Field(
        None,
        description="Report codes",
    )
    budget_amount: Optional[Decimal] = Field(
        None,
        ge=0,
        description="Budget amount for Budget items",
    )


class ItemFilterParams(BaseModel):
    """Query parameters for filtering items."""

    type: Optional[ItemType] = Field(
        None,
        description="Filter by item type",
    )
    workstream_id: Optional[UUID] = Field(
        None,
        description="Filter by workstream",
    )
    assigned_to: Optional[str] = Field(
        None,
        description="Filter by assignee (partial match)",
    )
    indicator: Optional[Indicator] = Field(
        None,
        description="Filter by indicator",
    )
    draft: Optional[bool] = Field(
        None,
        description="Filter by draft status",
    )
    search: Optional[str] = Field(
        None,
        max_length=100,
        description="Search in title and description",
    )
    limit: int = Field(
        100,
        ge=1,
        le=500,
        description="Maximum number of results",
    )
    offset: int = Field(
        0,
        ge=0,
        description="Number of results to skip",
    )


# =============================================================================
# RESPONSE SCHEMAS
# =============================================================================


class ItemResponse(BaseModel):
    """Response body for a single item."""

    id: UUID = Field(
        ...,
        description="Unique item identifier",
    )
    project_id: UUID = Field(
        ...,
        description="Parent project ID",
    )
    item_num: int = Field(
        ...,
        description="Human-readable item number",
    )
    type: ItemType = Field(
        ...,
        description="Item type",
    )
    title: str = Field(
        ...,
        description="Item title",
    )
    description: Optional[str] = Field(
        None,
        description="Detailed description",
    )
    workstream_id: Optional[UUID] = Field(
        None,
        description="Associated workstream ID",
    )
    assigned_to: Optional[str] = Field(
        None,
        description="Assignee name",
    )
    start_date: Optional[date] = Field(
        None,
        description="Planned start date",
    )
    finish_date: Optional[date] = Field(
        None,
        description="Planned finish date",
    )
    duration_days: Optional[int] = Field(
        None,
        description="Estimated duration in days",
    )
    deadline: Optional[date] = Field(
        None,
        description="Hard deadline date",
    )
    draft: bool = Field(
        ...,
        description="Whether item is in draft mode",
    )
    client_visible: bool = Field(
        ...,
        description="Whether item is visible to client",
    )
    percent_complete: int = Field(
        ...,
        description="Completion percentage (0-100)",
    )
    indicator: Optional[Indicator] = Field(
        None,
        description="Calculated status indicator",
    )
    priority: Optional[str] = Field(
        None,
        description="Priority level",
    )
    rpt_out: Optional[list[str]] = Field(
        None,
        description="Report codes",
    )
    budget_amount: Optional[Decimal] = Field(
        None,
        description="Budget amount for Budget items",
    )
    created_at: Optional[datetime] = Field(
        None,
        description="Creation timestamp",
    )
    updated_at: Optional[datetime] = Field(
        None,
        description="Last update timestamp",
    )

    model_config = {"from_attributes": True}


class ItemListResponse(BaseModel):
    """Response body for listing items."""

    items: list[ItemResponse] = Field(
        ...,
        description="List of items",
    )
    total: int = Field(
        ...,
        description="Total number of matching items",
    )

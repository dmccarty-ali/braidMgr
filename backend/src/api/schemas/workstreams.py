"""
Pydantic schemas for workstream API endpoints.

Defines request and response models for workstream CRUD operations.

Usage:
    from src.api.schemas.workstreams import WorkstreamCreateRequest, WorkstreamResponse
"""

from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


# =============================================================================
# REQUEST SCHEMAS
# =============================================================================


class WorkstreamCreateRequest(BaseModel):
    """Request body for creating a workstream."""

    name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Workstream name",
        examples=["Development"],
    )


class WorkstreamUpdateRequest(BaseModel):
    """Request body for updating a workstream."""

    name: Optional[str] = Field(
        None,
        min_length=1,
        max_length=255,
        description="Workstream name",
        examples=["Development"],
    )


class WorkstreamReorderRequest(BaseModel):
    """Request body for reordering workstreams."""

    workstream_ids: list[UUID] = Field(
        ...,
        min_length=1,
        description="List of workstream IDs in desired order",
    )


# =============================================================================
# RESPONSE SCHEMAS
# =============================================================================


class WorkstreamResponse(BaseModel):
    """Response body for a single workstream."""

    id: UUID = Field(
        ...,
        description="Unique workstream identifier",
    )
    project_id: UUID = Field(
        ...,
        description="Parent project ID",
    )
    name: str = Field(
        ...,
        description="Workstream name",
    )
    sort_order: int = Field(
        ...,
        description="Display order (0-based)",
    )

    model_config = {"from_attributes": True}


class WorkstreamListResponse(BaseModel):
    """Response body for listing workstreams."""

    workstreams: list[WorkstreamResponse] = Field(
        ...,
        description="List of workstreams",
    )

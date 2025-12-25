"""
Pydantic schemas for project API endpoints.

Defines request and response models for project CRUD operations.

Usage:
    from src.api.schemas.projects import ProjectCreateRequest, ProjectResponse
"""

from datetime import date, datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


# =============================================================================
# REQUEST SCHEMAS
# =============================================================================


class ProjectCreateRequest(BaseModel):
    """Request body for creating a project."""

    name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Project name",
        examples=["Q1 Platform Upgrade"],
    )
    client_name: Optional[str] = Field(
        None,
        max_length=255,
        description="Client or customer name",
        examples=["Acme Corp"],
    )
    project_start: Optional[date] = Field(
        None,
        description="Project start date",
        examples=["2024-01-15"],
    )
    project_end: Optional[date] = Field(
        None,
        description="Project end date",
        examples=["2024-06-30"],
    )
    workstreams: Optional[list[str]] = Field(
        None,
        description="Initial workstream names to create",
        examples=[["Development", "Testing", "Deployment"]],
    )


class ProjectUpdateRequest(BaseModel):
    """Request body for updating a project."""

    name: Optional[str] = Field(
        None,
        min_length=1,
        max_length=255,
        description="Project name",
        examples=["Q1 Platform Upgrade"],
    )
    client_name: Optional[str] = Field(
        None,
        max_length=255,
        description="Client or customer name",
        examples=["Acme Corp"],
    )
    project_start: Optional[date] = Field(
        None,
        description="Project start date",
        examples=["2024-01-15"],
    )
    project_end: Optional[date] = Field(
        None,
        description="Project end date",
        examples=["2024-06-30"],
    )


# =============================================================================
# RESPONSE SCHEMAS
# =============================================================================


class ProjectResponse(BaseModel):
    """Response body for a single project."""

    id: UUID = Field(
        ...,
        description="Unique project identifier",
    )
    organization_id: UUID = Field(
        ...,
        description="Owning organization ID",
    )
    name: str = Field(
        ...,
        description="Project name",
    )
    client_name: Optional[str] = Field(
        None,
        description="Client or customer name",
    )
    project_start: Optional[date] = Field(
        None,
        description="Project start date",
    )
    project_end: Optional[date] = Field(
        None,
        description="Project end date",
    )
    next_item_num: int = Field(
        ...,
        description="Next item number to be assigned",
    )
    indicators_updated: Optional[datetime] = Field(
        None,
        description="Last indicator recalculation timestamp",
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


class ProjectListResponse(BaseModel):
    """Response body for listing projects."""

    projects: list[ProjectResponse] = Field(
        ...,
        description="List of projects",
    )
    total: int = Field(
        ...,
        description="Total number of projects",
    )

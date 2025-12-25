"""
API schemas for braidMgr.

Pydantic models for request/response validation.
"""

# Auth schemas
from src.api.schemas.auth import (
    RegisterRequest,
    LoginRequest,
    ForgotPasswordRequest,
    ResetPasswordRequest,
    AuthResponse,
    TokenResponse,
    MessageResponse,
    ErrorResponse,
    UserResponse,
    CurrentUserResponse,
    UpdateProfileRequest,
)

# Project schemas
from src.api.schemas.projects import (
    ProjectCreateRequest,
    ProjectUpdateRequest,
    ProjectResponse,
    ProjectListResponse,
)

# Item schemas
from src.api.schemas.items import (
    ItemCreateRequest,
    ItemUpdateRequest,
    ItemFilterParams,
    ItemResponse,
    ItemListResponse,
)

# Workstream schemas
from src.api.schemas.workstreams import (
    WorkstreamCreateRequest,
    WorkstreamUpdateRequest,
    WorkstreamReorderRequest,
    WorkstreamResponse,
    WorkstreamListResponse,
)

__all__ = [
    # Auth requests
    "RegisterRequest",
    "LoginRequest",
    "ForgotPasswordRequest",
    "ResetPasswordRequest",
    "UpdateProfileRequest",
    # Auth responses
    "AuthResponse",
    "TokenResponse",
    "MessageResponse",
    "ErrorResponse",
    "UserResponse",
    "CurrentUserResponse",
    # Project schemas
    "ProjectCreateRequest",
    "ProjectUpdateRequest",
    "ProjectResponse",
    "ProjectListResponse",
    # Item schemas
    "ItemCreateRequest",
    "ItemUpdateRequest",
    "ItemFilterParams",
    "ItemResponse",
    "ItemListResponse",
    # Workstream schemas
    "WorkstreamCreateRequest",
    "WorkstreamUpdateRequest",
    "WorkstreamReorderRequest",
    "WorkstreamResponse",
    "WorkstreamListResponse",
]

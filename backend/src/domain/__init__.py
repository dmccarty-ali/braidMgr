"""
Domain models for braidMgr.

Contains dataclasses representing business entities.
"""

from src.domain.auth import (
    User,
    TokenPayload,
    RefreshToken,
    PasswordResetToken,
    LoginAttempt,
    OAuthAccount,
    OAuthProvider,
    OrgRole,
    ProjectRole,
    AuthResult,
    CurrentUser,
)

from src.domain.core import (
    Project,
    Item,
    Workstream,
    ItemNote,
    ItemDependency,
    ItemType,
    Indicator,
    ProjectResult,
    ItemResult,
    WorkstreamResult,
    ItemNoteResult,
)

__all__ = [
    # Auth entities
    "User",
    "TokenPayload",
    "RefreshToken",
    "PasswordResetToken",
    "LoginAttempt",
    "OAuthAccount",
    "OAuthProvider",
    # Role enums
    "OrgRole",
    "ProjectRole",
    # Auth results
    "AuthResult",
    "CurrentUser",
    # Core entities
    "Project",
    "Item",
    "Workstream",
    "ItemNote",
    "ItemDependency",
    # Core enums
    "ItemType",
    "Indicator",
    # Core results
    "ProjectResult",
    "ItemResult",
    "WorkstreamResult",
    "ItemNoteResult",
]

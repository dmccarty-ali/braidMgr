"""
Repository layer for braidMgr.

Provides database access for domain entities.
All repositories require an AuroraService instance.

Usage:
    from src.repositories import UserRepository, ProjectRepository
    from src.services import services

    repo = UserRepository(services.aurora)
    user = await repo.get_by_email("user@example.com")
"""

# Auth repositories
from src.repositories.user_repository import UserRepository
from src.repositories.refresh_token_repository import RefreshTokenRepository
from src.repositories.password_reset_repository import PasswordResetRepository
from src.repositories.login_attempt_repository import LoginAttemptRepository
from src.repositories.oauth_account_repository import OAuthAccountRepository
from src.repositories.user_project_role_repository import UserProjectRoleRepository

# Core repositories
from src.repositories.project_repository import ProjectRepository
from src.repositories.item_repository import ItemRepository
from src.repositories.workstream_repository import WorkstreamRepository
from src.repositories.item_note_repository import ItemNoteRepository
from src.repositories.item_dependency_repository import ItemDependencyRepository

__all__ = [
    # Auth
    "UserRepository",
    "RefreshTokenRepository",
    "PasswordResetRepository",
    "LoginAttemptRepository",
    "OAuthAccountRepository",
    "UserProjectRoleRepository",
    # Core
    "ProjectRepository",
    "ItemRepository",
    "WorkstreamRepository",
    "ItemNoteRepository",
    "ItemDependencyRepository",
]

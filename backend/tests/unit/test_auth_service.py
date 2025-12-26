"""
Unit tests for src/services/auth_service.py

Tests authentication service functionality:
- Login with org membership lookup
- Token generation with org context
"""

import pytest
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import UUID

from src.services.auth_service import AuthService
from src.domain.auth import User
from src.utils.jwt import decode_access_token


class TestAuthServiceLogin:
    """Tests for AuthService.login with org membership."""

    @pytest.fixture
    def mock_aurora(self):
        """Create mock Aurora service."""
        aurora = MagicMock()
        aurora.fetch_one = AsyncMock()
        return aurora

    @pytest.fixture
    def auth_service(self, mock_aurora):
        """Create AuthService with mocked dependencies."""
        service = AuthService(mock_aurora)
        # Mock repositories
        service._users = MagicMock()
        service._users.get_by_email = AsyncMock()
        service._refresh_tokens = MagicMock()
        service._refresh_tokens.create = AsyncMock()
        service._login_attempts = MagicMock()
        service._login_attempts.is_locked_out = AsyncMock(return_value=False)
        service._login_attempts.check_rate_limit = AsyncMock(return_value=True)
        service._login_attempts.record_attempt = AsyncMock()
        return service

    @pytest.fixture
    def test_user(self):
        """Create test user."""
        return User(
            id=UUID("550e8400-e29b-41d4-a716-446655440000"),
            email="test@example.com",
            name="Test User",
            password_hash="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4.G1K1z5z5z5z5z5",
            email_verified=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )

    @pytest.mark.asyncio
    async def test_login_includes_org_id_when_user_has_membership(
        self, auth_service, mock_aurora, test_user
    ):
        """Login token includes org_id when user has an organization membership."""
        # Setup
        org_id = "660e8400-e29b-41d4-a716-446655440000"
        auth_service._users.get_by_email.return_value = test_user
        mock_aurora.fetch_one.return_value = {
            "organization_id": UUID(org_id),
            "org_role": "admin",
        }

        # Mock password verification
        with patch("src.services.auth_service.verify_password", return_value=True):
            result = await auth_service.login(
                email="test@example.com",
                password="password123",
            )

        # Verify
        assert result.success is True
        assert result.access_token is not None

        # Decode token and verify org_id is present
        payload = decode_access_token(result.access_token)
        assert payload is not None
        assert payload.get("org_id") == org_id
        assert payload.get("org_role") == "admin"

    @pytest.mark.asyncio
    async def test_login_no_org_id_when_user_has_no_membership(
        self, auth_service, mock_aurora, test_user
    ):
        """Login token has no org_id when user has no organization membership."""
        # Setup
        auth_service._users.get_by_email.return_value = test_user
        mock_aurora.fetch_one.return_value = None  # No org membership

        # Mock password verification
        with patch("src.services.auth_service.verify_password", return_value=True):
            result = await auth_service.login(
                email="test@example.com",
                password="password123",
            )

        # Verify
        assert result.success is True
        assert result.access_token is not None

        # Decode token and verify org_id is not present
        payload = decode_access_token(result.access_token)
        assert payload is not None
        assert payload.get("org_id") is None
        assert payload.get("org_role") is None

    @pytest.mark.asyncio
    async def test_login_queries_org_membership_with_correct_user_id(
        self, auth_service, mock_aurora, test_user
    ):
        """Login queries org membership using the correct user ID."""
        # Setup
        auth_service._users.get_by_email.return_value = test_user
        mock_aurora.fetch_one.return_value = None

        # Mock password verification
        with patch("src.services.auth_service.verify_password", return_value=True):
            await auth_service.login(
                email="test@example.com",
                password="password123",
            )

        # Verify fetch_one was called with user's ID
        mock_aurora.fetch_one.assert_called_once()
        call_args = mock_aurora.fetch_one.call_args
        # The SQL query should include user_id parameter
        assert test_user.id == call_args[0][1]  # Second positional arg is user_id

    @pytest.mark.asyncio
    async def test_login_fails_with_invalid_credentials(
        self, auth_service, mock_aurora, test_user
    ):
        """Login fails with invalid credentials (no org lookup attempted)."""
        # Setup
        auth_service._users.get_by_email.return_value = test_user

        # Mock password verification to fail
        with patch("src.services.auth_service.verify_password", return_value=False):
            result = await auth_service.login(
                email="test@example.com",
                password="wrong_password",
            )

        # Verify
        assert result.success is False
        assert "Invalid" in result.error

        # Org membership should not be queried on failed login
        mock_aurora.fetch_one.assert_not_called()

"""
Unit tests for ProjectRepository.

Tests all CRUD operations with mocked Aurora service.
"""

import pytest
from datetime import date, datetime, timezone
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

from src.repositories.project_repository import ProjectRepository


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def mock_aurora():
    """Mock Aurora service."""
    aurora = MagicMock()
    aurora.fetch_one = AsyncMock(return_value=None)
    aurora.fetch_all = AsyncMock(return_value=[])
    aurora.execute = AsyncMock(return_value="UPDATE 0")
    return aurora


@pytest.fixture
def project_repo(mock_aurora):
    """Project repository with mocked aurora."""
    return ProjectRepository(mock_aurora)


@pytest.fixture
def sample_project_row():
    """Sample database row for a project."""
    return {
        "id": uuid4(),
        "organization_id": uuid4(),
        "name": "Website Modernization",
        "client_name": "Acme Corp",
        "project_start": date(2025, 1, 1),
        "project_end": date(2025, 12, 31),
        "next_item_num": 100,
        "indicators_updated": datetime.now(timezone.utc),
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
        "deleted_at": None,
    }


# =============================================================================
# Get By ID Tests
# =============================================================================

class TestGetById:
    """Tests for get_by_id method."""

    @pytest.mark.asyncio
    async def test_returns_project_when_found(self, project_repo, mock_aurora, sample_project_row):
        """Test that get_by_id returns project when found."""
        mock_aurora.fetch_one.return_value = sample_project_row

        result = await project_repo.get_by_id(sample_project_row["id"])

        assert result is not None
        assert result.id == sample_project_row["id"]
        assert result.name == "Website Modernization"
        assert result.client_name == "Acme Corp"

    @pytest.mark.asyncio
    async def test_returns_none_when_not_found(self, project_repo, mock_aurora):
        """Test that get_by_id returns None when project not found."""
        mock_aurora.fetch_one.return_value = None

        result = await project_repo.get_by_id(uuid4())

        assert result is None

    @pytest.mark.asyncio
    async def test_queries_with_correct_id(self, project_repo, mock_aurora):
        """Test that get_by_id passes correct ID to query."""
        project_id = uuid4()

        await project_repo.get_by_id(project_id)

        mock_aurora.fetch_one.assert_called_once()
        call_args = mock_aurora.fetch_one.call_args
        assert project_id in call_args[0]


# =============================================================================
# Get By Org ID Tests
# =============================================================================

class TestGetByOrgId:
    """Tests for get_by_org_id method."""

    @pytest.mark.asyncio
    async def test_returns_all_projects_for_org(self, project_repo, mock_aurora, sample_project_row):
        """Test that get_by_org_id returns all projects."""
        row2 = sample_project_row.copy()
        row2["id"] = uuid4()
        row2["name"] = "Mobile App"
        mock_aurora.fetch_all.return_value = [sample_project_row, row2]

        result = await project_repo.get_by_org_id(sample_project_row["organization_id"])

        assert len(result) == 2
        assert result[0].name == "Website Modernization"
        assert result[1].name == "Mobile App"

    @pytest.mark.asyncio
    async def test_returns_empty_list_when_no_projects(self, project_repo, mock_aurora):
        """Test that get_by_org_id returns empty list when no projects."""
        mock_aurora.fetch_all.return_value = []

        result = await project_repo.get_by_org_id(uuid4())

        assert result == []


# =============================================================================
# List For User Tests
# =============================================================================

class TestListForUser:
    """Tests for list_for_user method."""

    @pytest.mark.asyncio
    async def test_returns_accessible_projects(self, project_repo, mock_aurora, sample_project_row):
        """Test that list_for_user returns projects user has access to."""
        mock_aurora.fetch_all.return_value = [sample_project_row]

        result = await project_repo.list_for_user(
            user_id=uuid4(),
            org_id=sample_project_row["organization_id"],
        )

        assert len(result) == 1
        assert result[0].name == "Website Modernization"

    @pytest.mark.asyncio
    async def test_returns_empty_when_no_access(self, project_repo, mock_aurora):
        """Test that list_for_user returns empty when user has no project access."""
        mock_aurora.fetch_all.return_value = []

        result = await project_repo.list_for_user(
            user_id=uuid4(),
            org_id=uuid4(),
        )

        assert result == []


# =============================================================================
# Exists Tests
# =============================================================================

class TestExists:
    """Tests for exists method."""

    @pytest.mark.asyncio
    async def test_returns_true_when_exists(self, project_repo, mock_aurora):
        """Test that exists returns True when project exists."""
        mock_aurora.fetch_one.return_value = {"1": 1}

        result = await project_repo.exists(uuid4())

        assert result is True

    @pytest.mark.asyncio
    async def test_returns_false_when_not_exists(self, project_repo, mock_aurora):
        """Test that exists returns False when project not found."""
        mock_aurora.fetch_one.return_value = None

        result = await project_repo.exists(uuid4())

        assert result is False


# =============================================================================
# Create Tests
# =============================================================================

class TestCreate:
    """Tests for create method."""

    @pytest.mark.asyncio
    async def test_creates_project_with_required_fields(self, project_repo, mock_aurora, sample_project_row):
        """Test that create works with required fields only."""
        mock_aurora.fetch_one.return_value = sample_project_row
        org_id = sample_project_row["organization_id"]

        result = await project_repo.create(
            org_id=org_id,
            name="New Project",
        )

        assert result is not None
        mock_aurora.fetch_one.assert_called_once()

    @pytest.mark.asyncio
    async def test_creates_project_with_all_fields(self, project_repo, mock_aurora, sample_project_row):
        """Test that create works with all fields."""
        mock_aurora.fetch_one.return_value = sample_project_row
        org_id = sample_project_row["organization_id"]

        result = await project_repo.create(
            org_id=org_id,
            name="Full Project",
            client_name="Big Client",
            project_start=date(2025, 1, 1),
            project_end=date(2025, 12, 31),
        )

        assert result is not None


# =============================================================================
# Update Tests
# =============================================================================

class TestUpdate:
    """Tests for update method."""

    @pytest.mark.asyncio
    async def test_updates_single_field(self, project_repo, mock_aurora, sample_project_row):
        """Test that update works with single field."""
        updated_row = sample_project_row.copy()
        updated_row["name"] = "Updated Name"
        mock_aurora.fetch_one.return_value = updated_row

        result = await project_repo.update(
            project_id=sample_project_row["id"],
            name="Updated Name",
        )

        assert result is not None
        mock_aurora.fetch_one.assert_called_once()

    @pytest.mark.asyncio
    async def test_updates_multiple_fields(self, project_repo, mock_aurora, sample_project_row):
        """Test that update works with multiple fields."""
        mock_aurora.fetch_one.return_value = sample_project_row

        result = await project_repo.update(
            project_id=sample_project_row["id"],
            name="Updated Name",
            client_name="New Client",
        )

        assert result is not None

    @pytest.mark.asyncio
    async def test_returns_none_when_not_found(self, project_repo, mock_aurora):
        """Test that update returns None when project not found."""
        mock_aurora.fetch_one.return_value = None

        result = await project_repo.update(
            project_id=uuid4(),
            name="Updated Name",
        )

        assert result is None

    @pytest.mark.asyncio
    async def test_no_changes_returns_current_project(self, project_repo, mock_aurora, sample_project_row):
        """Test that update with no changes returns current project."""
        mock_aurora.fetch_one.return_value = sample_project_row

        result = await project_repo.update(project_id=sample_project_row["id"])

        assert result is not None


# =============================================================================
# Soft Delete Tests
# =============================================================================

class TestSoftDelete:
    """Tests for soft_delete method."""

    @pytest.mark.asyncio
    async def test_deletes_project(self, project_repo, mock_aurora):
        """Test that soft_delete marks project as deleted."""
        mock_aurora.execute.return_value = "UPDATE 1"

        result = await project_repo.soft_delete(uuid4())

        assert result is True

    @pytest.mark.asyncio
    async def test_returns_false_when_not_found(self, project_repo, mock_aurora):
        """Test that soft_delete returns False when not found."""
        mock_aurora.execute.return_value = "UPDATE 0"

        result = await project_repo.soft_delete(uuid4())

        assert result is False


# =============================================================================
# Increment Item Num Tests
# =============================================================================

class TestIncrementItemNum:
    """Tests for increment_item_num method."""

    @pytest.mark.asyncio
    async def test_returns_next_item_number(self, project_repo, mock_aurora):
        """Test that increment_item_num returns correct number."""
        mock_aurora.fetch_one.return_value = {"item_num": 42}

        result = await project_repo.increment_item_num(uuid4())

        assert result == 42

    @pytest.mark.asyncio
    async def test_raises_when_project_not_found(self, project_repo, mock_aurora):
        """Test that increment_item_num raises when project not found."""
        mock_aurora.fetch_one.return_value = None
        project_id = uuid4()

        with pytest.raises(ValueError, match="Project not found"):
            await project_repo.increment_item_num(project_id)


# =============================================================================
# Update Indicators Timestamp Tests
# =============================================================================

class TestUpdateIndicatorsTimestamp:
    """Tests for update_indicators_timestamp method."""

    @pytest.mark.asyncio
    async def test_updates_timestamp(self, project_repo, mock_aurora):
        """Test that update_indicators_timestamp calls execute."""
        project_id = uuid4()

        await project_repo.update_indicators_timestamp(project_id)

        mock_aurora.execute.assert_called_once()
        call_args = mock_aurora.execute.call_args
        assert project_id in call_args[0]


# =============================================================================
# Row To Project Conversion Tests
# =============================================================================

class TestRowToProject:
    """Tests for _row_to_project helper."""

    def test_converts_all_fields(self, sample_project_row):
        """Test that _row_to_project converts all fields correctly."""
        result = ProjectRepository._row_to_project(sample_project_row)

        assert result.id == sample_project_row["id"]
        assert result.organization_id == sample_project_row["organization_id"]
        assert result.name == "Website Modernization"
        assert result.client_name == "Acme Corp"
        assert result.project_start == date(2025, 1, 1)
        assert result.project_end == date(2025, 12, 31)
        assert result.next_item_num == 100

    def test_returns_none_for_none_row(self):
        """Test that _row_to_project returns None for None row."""
        result = ProjectRepository._row_to_project(None)

        assert result is None

    def test_handles_null_optional_fields(self, sample_project_row):
        """Test that _row_to_project handles null optional fields."""
        sample_project_row["client_name"] = None
        sample_project_row["project_start"] = None
        sample_project_row["project_end"] = None

        result = ProjectRepository._row_to_project(sample_project_row)

        assert result.client_name is None
        assert result.project_start is None
        assert result.project_end is None

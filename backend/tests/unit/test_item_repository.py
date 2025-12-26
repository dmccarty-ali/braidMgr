"""
Unit tests for ItemRepository.

Tests all CRUD operations with mocked Aurora service.
"""

import pytest
from datetime import date, datetime, timezone
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

from src.repositories.item_repository import ItemRepository
from src.domain.core import ItemType, Indicator


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
def item_repo(mock_aurora):
    """Item repository with mocked aurora."""
    return ItemRepository(mock_aurora)


@pytest.fixture
def sample_item_row():
    """Sample database row for an item."""
    return {
        "id": uuid4(),
        "project_id": uuid4(),
        "item_num": 1,
        "type": "Risk",
        "title": "Test Risk Item",
        "description": "A test risk description",
        "workstream_id": uuid4(),
        "assigned_to": "John Doe",
        "start_date": date(2025, 1, 1),
        "finish_date": date(2025, 1, 31),
        "duration_days": 30,
        "deadline": date(2025, 2, 15),
        "draft": False,
        "client_visible": True,
        "percent_complete": 50,
        "indicator": "In Progress",
        "priority": "High",
        "rpt_out": ["EXEC", "CLIENT"],
        "budget_amount": Decimal("10000.00"),
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
    async def test_returns_item_when_found(self, item_repo, mock_aurora, sample_item_row):
        """Test that get_by_id returns item when found."""
        mock_aurora.fetch_one.return_value = sample_item_row

        result = await item_repo.get_by_id(sample_item_row["id"])

        assert result is not None
        assert result.id == sample_item_row["id"]
        assert result.title == "Test Risk Item"
        assert result.type == ItemType.RISK

    @pytest.mark.asyncio
    async def test_returns_none_when_not_found(self, item_repo, mock_aurora):
        """Test that get_by_id returns None when item not found."""
        mock_aurora.fetch_one.return_value = None

        result = await item_repo.get_by_id(uuid4())

        assert result is None

    @pytest.mark.asyncio
    async def test_queries_with_correct_id(self, item_repo, mock_aurora):
        """Test that get_by_id passes correct ID to query."""
        item_id = uuid4()

        await item_repo.get_by_id(item_id)

        mock_aurora.fetch_one.assert_called_once()
        call_args = mock_aurora.fetch_one.call_args
        assert item_id in call_args[0]


# =============================================================================
# Get By Item Number Tests
# =============================================================================

class TestGetByItemNum:
    """Tests for get_by_item_num method."""

    @pytest.mark.asyncio
    async def test_returns_item_when_found(self, item_repo, mock_aurora, sample_item_row):
        """Test that get_by_item_num returns item when found."""
        mock_aurora.fetch_one.return_value = sample_item_row
        project_id = sample_item_row["project_id"]

        result = await item_repo.get_by_item_num(project_id, 1)

        assert result is not None
        assert result.item_num == 1

    @pytest.mark.asyncio
    async def test_returns_none_when_not_found(self, item_repo, mock_aurora):
        """Test that get_by_item_num returns None when not found."""
        mock_aurora.fetch_one.return_value = None

        result = await item_repo.get_by_item_num(uuid4(), 999)

        assert result is None


# =============================================================================
# Get By Project ID Tests
# =============================================================================

class TestGetByProjectId:
    """Tests for get_by_project_id method."""

    @pytest.mark.asyncio
    async def test_returns_all_items_for_project(self, item_repo, mock_aurora, sample_item_row):
        """Test that get_by_project_id returns all items."""
        row2 = sample_item_row.copy()
        row2["id"] = uuid4()
        row2["item_num"] = 2
        mock_aurora.fetch_all.return_value = [sample_item_row, row2]

        result = await item_repo.get_by_project_id(sample_item_row["project_id"])

        assert len(result) == 2
        assert result[0].item_num == 1
        assert result[1].item_num == 2

    @pytest.mark.asyncio
    async def test_returns_empty_list_when_no_items(self, item_repo, mock_aurora):
        """Test that get_by_project_id returns empty list when no items."""
        mock_aurora.fetch_all.return_value = []

        result = await item_repo.get_by_project_id(uuid4())

        assert result == []


# =============================================================================
# List With Filters Tests
# =============================================================================

class TestListWithFilters:
    """Tests for list_with_filters method."""

    @pytest.mark.asyncio
    async def test_returns_filtered_items(self, item_repo, mock_aurora, sample_item_row):
        """Test that list_with_filters returns matching items."""
        mock_aurora.fetch_all.return_value = [sample_item_row]

        result = await item_repo.list_with_filters(
            project_id=sample_item_row["project_id"],
            item_type=ItemType.RISK,
        )

        assert len(result) == 1
        assert result[0].type == ItemType.RISK

    @pytest.mark.asyncio
    async def test_applies_type_filter(self, item_repo, mock_aurora):
        """Test that type filter is applied."""
        project_id = uuid4()

        await item_repo.list_with_filters(
            project_id=project_id,
            item_type=ItemType.ACTION_ITEM,
        )

        call_args = mock_aurora.fetch_all.call_args
        assert "Action Item" in call_args[0]

    @pytest.mark.asyncio
    async def test_applies_indicator_filter(self, item_repo, mock_aurora):
        """Test that indicator filter is applied."""
        project_id = uuid4()

        await item_repo.list_with_filters(
            project_id=project_id,
            indicator=Indicator.IN_PROGRESS,
        )

        call_args = mock_aurora.fetch_all.call_args
        assert "In Progress" in call_args[0]

    @pytest.mark.asyncio
    async def test_applies_search_filter(self, item_repo, mock_aurora):
        """Test that search filter is applied to title and description."""
        project_id = uuid4()

        await item_repo.list_with_filters(
            project_id=project_id,
            search="migration",
        )

        call_args = mock_aurora.fetch_all.call_args
        assert "%migration%" in call_args[0]

    @pytest.mark.asyncio
    async def test_applies_limit_and_offset(self, item_repo, mock_aurora):
        """Test that limit and offset are applied."""
        project_id = uuid4()

        await item_repo.list_with_filters(
            project_id=project_id,
            limit=10,
            offset=20,
        )

        call_args = mock_aurora.fetch_all.call_args
        assert 10 in call_args[0]
        assert 20 in call_args[0]


# =============================================================================
# Count Tests
# =============================================================================

class TestCountByProjectId:
    """Tests for count_by_project_id method."""

    @pytest.mark.asyncio
    async def test_returns_count(self, item_repo, mock_aurora):
        """Test that count_by_project_id returns correct count."""
        mock_aurora.fetch_one.return_value = {"count": 42}

        result = await item_repo.count_by_project_id(uuid4())

        assert result == 42

    @pytest.mark.asyncio
    async def test_returns_zero_when_no_items(self, item_repo, mock_aurora):
        """Test that count returns 0 when no items."""
        mock_aurora.fetch_one.return_value = None

        result = await item_repo.count_by_project_id(uuid4())

        assert result == 0


# =============================================================================
# Create Tests
# =============================================================================

class TestCreate:
    """Tests for create method."""

    @pytest.mark.asyncio
    async def test_creates_item_with_required_fields(self, item_repo, mock_aurora, sample_item_row):
        """Test that create works with required fields only."""
        mock_aurora.fetch_one.return_value = sample_item_row
        project_id = sample_item_row["project_id"]

        result = await item_repo.create(
            project_id=project_id,
            item_num=1,
            item_type=ItemType.RISK,
            title="New Risk",
        )

        assert result is not None
        assert result.title == "Test Risk Item"  # from mock
        mock_aurora.fetch_one.assert_called_once()

    @pytest.mark.asyncio
    async def test_creates_item_with_all_fields(self, item_repo, mock_aurora, sample_item_row):
        """Test that create works with all fields."""
        mock_aurora.fetch_one.return_value = sample_item_row
        project_id = sample_item_row["project_id"]
        workstream_id = uuid4()

        result = await item_repo.create(
            project_id=project_id,
            item_num=1,
            item_type=ItemType.BUDGET,
            title="Budget Item",
            description="Budget description",
            workstream_id=workstream_id,
            assigned_to="Jane Doe",
            start_date=date(2025, 1, 1),
            finish_date=date(2025, 12, 31),
            duration_days=365,
            deadline=date(2025, 6, 30),
            draft=True,
            client_visible=False,
            percent_complete=25,
            indicator=Indicator.TRENDING_LATE,
            priority="Medium",
            rpt_out=["EXEC"],
            budget_amount=Decimal("50000.00"),
        )

        assert result is not None


# =============================================================================
# Update Tests
# =============================================================================

class TestUpdate:
    """Tests for update method."""

    @pytest.mark.asyncio
    async def test_updates_single_field(self, item_repo, mock_aurora, sample_item_row):
        """Test that update works with single field."""
        updated_row = sample_item_row.copy()
        updated_row["title"] = "Updated Title"
        mock_aurora.fetch_one.return_value = updated_row

        result = await item_repo.update(
            item_id=sample_item_row["id"],
            title="Updated Title",
        )

        assert result is not None
        mock_aurora.fetch_one.assert_called_once()

    @pytest.mark.asyncio
    async def test_updates_multiple_fields(self, item_repo, mock_aurora, sample_item_row):
        """Test that update works with multiple fields."""
        mock_aurora.fetch_one.return_value = sample_item_row

        result = await item_repo.update(
            item_id=sample_item_row["id"],
            title="Updated Title",
            percent_complete=75,
            assigned_to="New Assignee",
        )

        assert result is not None

    @pytest.mark.asyncio
    async def test_returns_none_when_not_found(self, item_repo, mock_aurora):
        """Test that update returns None when item not found."""
        mock_aurora.fetch_one.return_value = None

        result = await item_repo.update(
            item_id=uuid4(),
            title="Updated Title",
        )

        assert result is None

    @pytest.mark.asyncio
    async def test_no_changes_returns_current_item(self, item_repo, mock_aurora, sample_item_row):
        """Test that update with no changes returns current item."""
        mock_aurora.fetch_one.return_value = sample_item_row

        result = await item_repo.update(item_id=sample_item_row["id"])

        assert result is not None


# =============================================================================
# Update Indicator Tests
# =============================================================================

class TestUpdateIndicator:
    """Tests for update_indicator method."""

    @pytest.mark.asyncio
    async def test_updates_indicator(self, item_repo, mock_aurora):
        """Test that update_indicator works."""
        mock_aurora.execute.return_value = "UPDATE 1"

        result = await item_repo.update_indicator(
            item_id=uuid4(),
            indicator=Indicator.COMPLETED,
        )

        assert result is True

    @pytest.mark.asyncio
    async def test_returns_false_when_not_found(self, item_repo, mock_aurora):
        """Test that update_indicator returns False when not found."""
        mock_aurora.execute.return_value = "UPDATE 0"

        result = await item_repo.update_indicator(
            item_id=uuid4(),
            indicator=Indicator.COMPLETED,
        )

        assert result is False


# =============================================================================
# Batch Update Indicators Tests
# =============================================================================

class TestBatchUpdateIndicators:
    """Tests for batch_update_indicators method."""

    @pytest.mark.asyncio
    async def test_updates_all_items(self, item_repo, mock_aurora):
        """Test that batch_update_indicators updates all items."""
        mock_aurora.execute.return_value = "UPDATE 1"
        updates = [
            (uuid4(), Indicator.COMPLETED),
            (uuid4(), Indicator.IN_PROGRESS),
            (uuid4(), Indicator.NOT_STARTED),
        ]

        result = await item_repo.batch_update_indicators(updates)

        assert result == 3

    @pytest.mark.asyncio
    async def test_returns_zero_for_empty_list(self, item_repo, mock_aurora):
        """Test that batch_update_indicators returns 0 for empty list."""
        result = await item_repo.batch_update_indicators([])

        assert result == 0


# =============================================================================
# Soft Delete Tests
# =============================================================================

class TestSoftDelete:
    """Tests for soft_delete method."""

    @pytest.mark.asyncio
    async def test_deletes_item(self, item_repo, mock_aurora):
        """Test that soft_delete marks item as deleted."""
        mock_aurora.execute.return_value = "UPDATE 1"

        result = await item_repo.soft_delete(uuid4())

        assert result is True

    @pytest.mark.asyncio
    async def test_returns_false_when_not_found(self, item_repo, mock_aurora):
        """Test that soft_delete returns False when not found."""
        mock_aurora.execute.return_value = "UPDATE 0"

        result = await item_repo.soft_delete(uuid4())

        assert result is False


# =============================================================================
# Row To Item Conversion Tests
# =============================================================================

class TestRowToItem:
    """Tests for _row_to_item helper."""

    def test_converts_all_fields(self, sample_item_row):
        """Test that _row_to_item converts all fields correctly."""
        result = ItemRepository._row_to_item(sample_item_row)

        assert result.id == sample_item_row["id"]
        assert result.project_id == sample_item_row["project_id"]
        assert result.item_num == 1
        assert result.type == ItemType.RISK
        assert result.title == "Test Risk Item"
        assert result.description == "A test risk description"
        assert result.percent_complete == 50
        assert result.indicator == Indicator.IN_PROGRESS
        assert result.budget_amount == Decimal("10000.00")

    def test_returns_none_for_none_row(self):
        """Test that _row_to_item returns None for None row."""
        result = ItemRepository._row_to_item(None)

        assert result is None

    def test_handles_null_indicator(self, sample_item_row):
        """Test that _row_to_item handles null indicator."""
        sample_item_row["indicator"] = None

        result = ItemRepository._row_to_item(sample_item_row)

        assert result.indicator is None

    def test_handles_all_item_types(self, sample_item_row):
        """Test that _row_to_item handles all item types."""
        for item_type in ItemType:
            sample_item_row["type"] = item_type.value
            result = ItemRepository._row_to_item(sample_item_row)
            assert result.type == item_type

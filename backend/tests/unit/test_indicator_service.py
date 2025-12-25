"""
Unit tests for indicator calculation service.

Tests all 10 indicator states and edge cases.
"""

from datetime import date, datetime, timedelta
from decimal import Decimal
from uuid import uuid4

import pytest

from src.domain.core import Item, ItemType, Indicator
from src.services.indicator_service import (
    calculate_indicator,
    calculate_indicators_batch,
    get_indicator_severity,
    SOON_THRESHOLD_DAYS,
    COMPLETED_RECENTLY_DAYS,
)


def make_item(**kwargs) -> Item:
    """Create a test item with default values."""
    defaults = {
        "id": uuid4(),
        "project_id": uuid4(),
        "item_num": 1,
        "type": ItemType.ACTION_ITEM,
        "title": "Test Item",
    }
    defaults.update(kwargs)
    return Item(**defaults)


class TestDraftItems:
    """Tests for draft item indicator (Rule 1)."""

    def test_draft_item_has_no_indicator(self):
        """Draft items should have no indicator regardless of dates/completion."""
        item = make_item(
            draft=True,
            start_date=date.today() - timedelta(days=30),
            finish_date=date.today() - timedelta(days=15),
            percent_complete=0,
        )
        assert calculate_indicator(item) is None

    def test_draft_item_ignores_deadline(self):
        """Draft items should have no indicator even with passed deadline."""
        item = make_item(
            draft=True,
            deadline=date.today() - timedelta(days=10),
            percent_complete=50,
        )
        assert calculate_indicator(item) is None


class TestCompletedItems:
    """Tests for completed item indicators (Rule 2)."""

    def test_completed_recently(self):
        """100% complete within threshold shows Completed Recently."""
        today = date.today()
        item = make_item(
            percent_complete=100,
            updated_at=datetime.combine(today - timedelta(days=5), datetime.min.time()),
        )
        assert calculate_indicator(item, today) == Indicator.COMPLETED_RECENTLY

    def test_completed_at_threshold_boundary(self):
        """100% complete at exactly threshold days shows Completed Recently."""
        today = date.today()
        item = make_item(
            percent_complete=100,
            updated_at=datetime.combine(
                today - timedelta(days=COMPLETED_RECENTLY_DAYS), datetime.min.time()
            ),
        )
        assert calculate_indicator(item, today) == Indicator.COMPLETED_RECENTLY

    def test_completed_beyond_threshold(self):
        """100% complete beyond threshold shows Completed."""
        today = date.today()
        item = make_item(
            percent_complete=100,
            updated_at=datetime.combine(
                today - timedelta(days=COMPLETED_RECENTLY_DAYS + 1), datetime.min.time()
            ),
        )
        assert calculate_indicator(item, today) == Indicator.COMPLETED

    def test_completed_no_updated_at(self):
        """100% complete without updated_at shows Completed."""
        item = make_item(percent_complete=100, updated_at=None)
        assert calculate_indicator(item) == Indicator.COMPLETED


class TestBeyondDeadline:
    """Tests for Beyond Deadline indicator (Rule 3)."""

    def test_deadline_passed(self):
        """Deadline passed shows Beyond Deadline."""
        today = date.today()
        item = make_item(
            deadline=today - timedelta(days=1),
            percent_complete=50,
        )
        assert calculate_indicator(item, today) == Indicator.BEYOND_DEADLINE

    def test_deadline_passed_overrides_late_finish(self):
        """Beyond Deadline takes precedence over Late Finish."""
        today = date.today()
        item = make_item(
            deadline=today - timedelta(days=1),
            finish_date=today - timedelta(days=5),
            percent_complete=50,
        )
        assert calculate_indicator(item, today) == Indicator.BEYOND_DEADLINE

    def test_deadline_today_not_beyond(self):
        """Deadline on today is not beyond deadline."""
        today = date.today()
        item = make_item(
            deadline=today,
            percent_complete=50,
        )
        assert calculate_indicator(item, today) != Indicator.BEYOND_DEADLINE


class TestLateFinish:
    """Tests for Late Finish indicator (Rule 4)."""

    def test_finish_date_passed_not_complete(self):
        """Finish date passed with <100% shows Late Finish."""
        today = date.today()
        item = make_item(
            finish_date=today - timedelta(days=1),
            percent_complete=75,
        )
        assert calculate_indicator(item, today) == Indicator.LATE_FINISH

    def test_finish_date_passed_at_zero(self):
        """Finish date passed at 0% shows Late Finish (not Late Start)."""
        today = date.today()
        item = make_item(
            start_date=today - timedelta(days=30),
            finish_date=today - timedelta(days=1),
            percent_complete=0,
        )
        # Late Finish takes precedence over Late Start
        assert calculate_indicator(item, today) == Indicator.LATE_FINISH


class TestLateStart:
    """Tests for Late Start indicator (Rule 5)."""

    def test_start_date_passed_zero_percent(self):
        """Start date passed at 0% shows Late Start."""
        today = date.today()
        item = make_item(
            start_date=today - timedelta(days=5),
            finish_date=today + timedelta(days=10),
            percent_complete=0,
        )
        assert calculate_indicator(item, today) == Indicator.LATE_START

    def test_start_date_passed_with_progress(self):
        """Start date passed with >0% is not Late Start."""
        today = date.today()
        item = make_item(
            start_date=today - timedelta(days=5),
            finish_date=today + timedelta(days=10),
            percent_complete=10,
        )
        assert calculate_indicator(item, today) != Indicator.LATE_START


class TestTrendingLate:
    """Tests for Trending Late indicator (Rule 6)."""

    def test_behind_schedule(self):
        """Item behind expected progress shows Trending Late."""
        today = date.today()
        # 10-day duration, 5 days elapsed, should be 50% but at 20%
        item = make_item(
            start_date=today - timedelta(days=5),
            finish_date=today + timedelta(days=5),
            percent_complete=20,  # Should be ~50% based on time
        )
        assert calculate_indicator(item, today) == Indicator.TRENDING_LATE

    def test_on_schedule(self):
        """Item on schedule is not Trending Late."""
        today = date.today()
        # 10-day duration, 5 days elapsed, at 50%
        item = make_item(
            start_date=today - timedelta(days=5),
            finish_date=today + timedelta(days=5),
            percent_complete=50,
        )
        assert calculate_indicator(item, today) != Indicator.TRENDING_LATE

    def test_ahead_of_schedule(self):
        """Item ahead of schedule is not Trending Late."""
        today = date.today()
        # 10-day duration, 5 days elapsed, at 75%
        item = make_item(
            start_date=today - timedelta(days=5),
            finish_date=today + timedelta(days=5),
            percent_complete=75,
        )
        assert calculate_indicator(item, today) != Indicator.TRENDING_LATE

    def test_not_started_not_trending_late(self):
        """Item that hasn't started is not Trending Late."""
        today = date.today()
        item = make_item(
            start_date=today + timedelta(days=5),
            finish_date=today + timedelta(days=15),
            percent_complete=0,
        )
        assert calculate_indicator(item, today) != Indicator.TRENDING_LATE


class TestFinishingSoon:
    """Tests for Finishing Soon indicator (Rule 7)."""

    def test_finish_within_threshold(self):
        """Finish date within threshold shows Finishing Soon."""
        today = date.today()
        item = make_item(
            start_date=today - timedelta(days=30),
            finish_date=today + timedelta(days=7),
            percent_complete=80,
        )
        assert calculate_indicator(item, today) == Indicator.FINISHING_SOON

    def test_finish_at_threshold_boundary(self):
        """Finish date at exactly threshold shows Finishing Soon."""
        today = date.today()
        item = make_item(
            start_date=today - timedelta(days=30),
            finish_date=today + timedelta(days=SOON_THRESHOLD_DAYS),
            percent_complete=80,
        )
        assert calculate_indicator(item, today) == Indicator.FINISHING_SOON

    def test_finish_beyond_threshold(self):
        """Finish date beyond threshold is not Finishing Soon."""
        today = date.today()
        item = make_item(
            start_date=today - timedelta(days=5),
            finish_date=today + timedelta(days=SOON_THRESHOLD_DAYS + 1),
            percent_complete=10,
        )
        assert calculate_indicator(item, today) != Indicator.FINISHING_SOON

    def test_finish_today(self):
        """Finish date today shows Finishing Soon."""
        today = date.today()
        item = make_item(
            finish_date=today,
            percent_complete=90,
        )
        assert calculate_indicator(item, today) == Indicator.FINISHING_SOON


class TestStartingSoon:
    """Tests for Starting Soon indicator (Rule 8)."""

    def test_start_within_threshold_zero_percent(self):
        """Start date within threshold at 0% shows Starting Soon."""
        today = date.today()
        item = make_item(
            start_date=today + timedelta(days=5),
            finish_date=today + timedelta(days=20),
            percent_complete=0,
        )
        assert calculate_indicator(item, today) == Indicator.STARTING_SOON

    def test_start_within_threshold_with_progress(self):
        """Start date within threshold with >0% is not Starting Soon."""
        today = date.today()
        item = make_item(
            start_date=today + timedelta(days=5),
            finish_date=today + timedelta(days=20),
            percent_complete=10,
        )
        assert calculate_indicator(item, today) != Indicator.STARTING_SOON

    def test_start_at_threshold_boundary(self):
        """Start date at exactly threshold shows Starting Soon."""
        today = date.today()
        item = make_item(
            start_date=today + timedelta(days=SOON_THRESHOLD_DAYS),
            finish_date=today + timedelta(days=30),
            percent_complete=0,
        )
        assert calculate_indicator(item, today) == Indicator.STARTING_SOON

    def test_start_today(self):
        """Start date today with far finish date shows Starting Soon."""
        today = date.today()
        item = make_item(
            start_date=today,
            finish_date=today + timedelta(days=30),  # Far enough to not trigger Finishing Soon
            percent_complete=0,
        )
        assert calculate_indicator(item, today) == Indicator.STARTING_SOON


class TestInProgress:
    """Tests for In Progress indicator (Rule 9)."""

    def test_partial_progress(self):
        """Item with 1-99% complete shows In Progress."""
        item = make_item(percent_complete=50)
        assert calculate_indicator(item) == Indicator.IN_PROGRESS

    def test_one_percent(self):
        """Item at 1% shows In Progress."""
        item = make_item(percent_complete=1)
        assert calculate_indicator(item) == Indicator.IN_PROGRESS

    def test_ninety_nine_percent(self):
        """Item at 99% shows In Progress."""
        item = make_item(percent_complete=99)
        assert calculate_indicator(item) == Indicator.IN_PROGRESS


class TestNotStarted:
    """Tests for Not Started indicator (Rule 10)."""

    def test_has_dates_zero_percent(self):
        """Item with dates at 0% shows Not Started."""
        today = date.today()
        item = make_item(
            start_date=today + timedelta(days=30),
            finish_date=today + timedelta(days=60),
            percent_complete=0,
        )
        assert calculate_indicator(item, today) == Indicator.NOT_STARTED

    def test_no_dates_zero_percent(self):
        """Item without dates at 0% has no indicator."""
        item = make_item(percent_complete=0)
        assert calculate_indicator(item) is None


class TestPrecedence:
    """Tests for indicator precedence order."""

    def test_beyond_deadline_over_late_finish(self):
        """Beyond Deadline takes precedence over Late Finish."""
        today = date.today()
        item = make_item(
            deadline=today - timedelta(days=1),
            finish_date=today - timedelta(days=5),
            percent_complete=50,
        )
        assert calculate_indicator(item, today) == Indicator.BEYOND_DEADLINE

    def test_late_finish_over_late_start(self):
        """Late Finish takes precedence over Late Start."""
        today = date.today()
        item = make_item(
            start_date=today - timedelta(days=10),
            finish_date=today - timedelta(days=1),
            percent_complete=0,
        )
        assert calculate_indicator(item, today) == Indicator.LATE_FINISH

    def test_late_start_over_trending_late(self):
        """Late Start takes precedence over Trending Late."""
        today = date.today()
        item = make_item(
            start_date=today - timedelta(days=10),
            finish_date=today + timedelta(days=10),
            percent_complete=0,
        )
        assert calculate_indicator(item, today) == Indicator.LATE_START

    def test_trending_late_over_finishing_soon(self):
        """Trending Late takes precedence over Finishing Soon."""
        today = date.today()
        # 20-day duration, 18 days elapsed, should be 90% but at 40%
        item = make_item(
            start_date=today - timedelta(days=18),
            finish_date=today + timedelta(days=2),
            percent_complete=40,
        )
        assert calculate_indicator(item, today) == Indicator.TRENDING_LATE


class TestBatchCalculation:
    """Tests for batch indicator calculation."""

    def test_batch_calculates_all_items(self):
        """Batch calculation returns indicator for each item."""
        today = date.today()
        items = [
            make_item(draft=True),
            make_item(percent_complete=100),
            make_item(percent_complete=50),
        ]

        results = calculate_indicators_batch(items, today)

        assert len(results) == 3
        assert results[0] == (items[0], None)
        assert results[1] == (items[1], Indicator.COMPLETED)
        assert results[2] == (items[2], Indicator.IN_PROGRESS)


class TestIndicatorSeverity:
    """Tests for indicator severity ordering."""

    def test_severity_order(self):
        """Indicators should be ordered by severity."""
        assert get_indicator_severity(None) < get_indicator_severity(Indicator.COMPLETED)
        assert get_indicator_severity(Indicator.COMPLETED) < get_indicator_severity(
            Indicator.COMPLETED_RECENTLY
        )
        assert get_indicator_severity(Indicator.NOT_STARTED) < get_indicator_severity(
            Indicator.STARTING_SOON
        )
        assert get_indicator_severity(Indicator.IN_PROGRESS) < get_indicator_severity(
            Indicator.FINISHING_SOON
        )
        assert get_indicator_severity(Indicator.FINISHING_SOON) < get_indicator_severity(
            Indicator.TRENDING_LATE
        )
        assert get_indicator_severity(Indicator.TRENDING_LATE) < get_indicator_severity(
            Indicator.LATE_START
        )
        assert get_indicator_severity(Indicator.LATE_START) < get_indicator_severity(
            Indicator.LATE_FINISH
        )
        assert get_indicator_severity(Indicator.LATE_FINISH) < get_indicator_severity(
            Indicator.BEYOND_DEADLINE
        )

    def test_beyond_deadline_highest_severity(self):
        """Beyond Deadline should have highest severity."""
        assert get_indicator_severity(Indicator.BEYOND_DEADLINE) == 10

    def test_none_lowest_severity(self):
        """None should have lowest severity."""
        assert get_indicator_severity(None) == 0


class TestEdgeCases:
    """Tests for edge cases and boundary conditions."""

    def test_same_start_and_finish_date(self):
        """Item with same start and finish date shows Finishing Soon (takes precedence)."""
        today = date.today()
        item = make_item(
            start_date=today + timedelta(days=5),
            finish_date=today + timedelta(days=5),
            percent_complete=0,
        )
        # Finishing Soon (Rule 7) takes precedence over Starting Soon (Rule 8)
        assert calculate_indicator(item, today) == Indicator.FINISHING_SOON

    def test_only_start_date(self):
        """Item with only start date."""
        today = date.today()
        item = make_item(
            start_date=today + timedelta(days=5),
            percent_complete=0,
        )
        # Has start date within threshold, 0%, should be Starting Soon
        assert calculate_indicator(item, today) == Indicator.STARTING_SOON

    def test_only_finish_date(self):
        """Item with only finish date."""
        today = date.today()
        item = make_item(
            finish_date=today + timedelta(days=5),
            percent_complete=50,
        )
        # Has finish date within threshold, should be Finishing Soon
        assert calculate_indicator(item, today) == Indicator.FINISHING_SOON

    def test_only_deadline(self):
        """Item with only deadline."""
        item = make_item(
            deadline=date.today() + timedelta(days=30),
            percent_complete=50,
        )
        # Only deadline, not passed, partial progress -> In Progress
        assert calculate_indicator(item) == Indicator.IN_PROGRESS

    def test_percent_complete_over_100(self):
        """Item with percent_complete > 100 treated as complete."""
        item = make_item(percent_complete=150)
        assert calculate_indicator(item) == Indicator.COMPLETED

    def test_negative_percent_complete(self):
        """Item with negative percent_complete has no indicator (not == 0)."""
        today = date.today()
        item = make_item(
            start_date=today + timedelta(days=30),
            finish_date=today + timedelta(days=60),
            percent_complete=-10,
        )
        # Negative is not == 0, so Not Started rule doesn't apply
        # Also not in progress (which requires > 0)
        # Falls through to None
        assert calculate_indicator(item, today) is None

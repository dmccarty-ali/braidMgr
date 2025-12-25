"""
Indicator calculation service for braidMgr.

Calculates status indicators for items based on dates, completion,
and deadlines. Implements the indicator state machine from PROCESS_FLOWS.md.

Usage:
    from src.services.indicator_service import calculate_indicator

    indicator = calculate_indicator(item, today=date.today())
"""

from datetime import date, timedelta
from typing import Optional

from src.domain.core import Item, Indicator


# =============================================================================
# CONSTANTS
# =============================================================================
# Configuration for indicator calculation thresholds.
# =============================================================================

# Number of days to consider "soon" for starting/finishing
SOON_THRESHOLD_DAYS = 14

# Number of days after completion to show "Completed Recently"
COMPLETED_RECENTLY_DAYS = 14


# =============================================================================
# INDICATOR CALCULATION
# =============================================================================


def calculate_indicator(item: Item, today: Optional[date] = None) -> Optional[Indicator]:
    """
    Calculate the status indicator for an item.

    Implements the indicator precedence rules from item-lifecycle.md.
    Higher severity indicators take precedence over lower ones.

    Precedence (highest to lowest):
    1. Draft items -> None (no indicator)
    2. 100% complete -> Completed Recently or Completed
    3. Deadline passed -> Beyond Deadline!!!
    4. Finish date passed, <100% -> Late Finish!!
    5. Start date passed, 0% -> Late Start!!
    6. Remaining work > remaining time -> Trending Late!
    7. Finish date within 14 days -> Finishing Soon!
    8. Start date within 14 days, 0% -> Starting Soon!
    9. 1-99% complete -> In Progress
    10. Has dates, 0% complete -> Not Started

    Args:
        item: The item to calculate indicator for
        today: Reference date for calculation (defaults to today)

    Returns:
        Calculated Indicator enum value, or None for draft items
    """
    if today is None:
        today = date.today()

    # ==========================================================================
    # RULE 1: Draft items have no indicator
    # ==========================================================================
    if item.draft:
        return None

    # ==========================================================================
    # RULE 2: Completed items
    # ==========================================================================
    if item.percent_complete >= 100:
        # Check if completed recently (within threshold days)
        if item.updated_at is not None:
            completion_date = item.updated_at.date()
            days_since_completion = (today - completion_date).days
            if days_since_completion <= COMPLETED_RECENTLY_DAYS:
                return Indicator.COMPLETED_RECENTLY
        return Indicator.COMPLETED

    # ==========================================================================
    # RULE 3: Beyond deadline (overrides all other active states)
    # ==========================================================================
    if item.deadline is not None and item.deadline < today:
        return Indicator.BEYOND_DEADLINE

    # ==========================================================================
    # RULE 4: Late finish (finish date passed, not complete)
    # ==========================================================================
    if item.finish_date is not None and item.finish_date < today:
        return Indicator.LATE_FINISH

    # ==========================================================================
    # RULE 5: Late start (start date passed, still at 0%)
    # ==========================================================================
    if (
        item.start_date is not None
        and item.start_date < today
        and item.percent_complete == 0
    ):
        return Indicator.LATE_START

    # ==========================================================================
    # RULE 6: Trending late (remaining work exceeds remaining time)
    # ==========================================================================
    if _is_trending_late(item, today):
        return Indicator.TRENDING_LATE

    # ==========================================================================
    # RULE 7: Finishing soon (finish date within threshold)
    # ==========================================================================
    if item.finish_date is not None:
        days_until_finish = (item.finish_date - today).days
        if 0 <= days_until_finish <= SOON_THRESHOLD_DAYS:
            return Indicator.FINISHING_SOON

    # ==========================================================================
    # RULE 8: Starting soon (start date within threshold, still at 0%)
    # ==========================================================================
    if item.start_date is not None and item.percent_complete == 0:
        days_until_start = (item.start_date - today).days
        if 0 <= days_until_start <= SOON_THRESHOLD_DAYS:
            return Indicator.STARTING_SOON

    # ==========================================================================
    # RULE 9: In progress (1-99% complete)
    # ==========================================================================
    if 0 < item.percent_complete < 100:
        return Indicator.IN_PROGRESS

    # ==========================================================================
    # RULE 10: Not started (has dates, 0% complete)
    # ==========================================================================
    if item.has_dates and item.percent_complete == 0:
        return Indicator.NOT_STARTED

    # No indicator if no dates and 0% complete
    return None


def _is_trending_late(item: Item, today: date) -> bool:
    """
    Check if item is trending late based on remaining work vs remaining time.

    An item is trending late if:
    - It has both start and finish dates
    - It has started (start_date <= today)
    - It is not complete (percent_complete < 100)
    - Remaining work percentage > remaining time percentage

    Args:
        item: The item to check
        today: Reference date

    Returns:
        True if item is trending late
    """
    # Must have both dates to calculate
    if item.start_date is None or item.finish_date is None:
        return False

    # Must have started
    if item.start_date > today:
        return False

    # Must not be complete
    if item.percent_complete >= 100:
        return False

    # Calculate total duration
    total_days = (item.finish_date - item.start_date).days
    if total_days <= 0:
        return False

    # Calculate elapsed time
    elapsed_days = (today - item.start_date).days
    if elapsed_days < 0:
        elapsed_days = 0

    # Calculate expected progress based on time elapsed
    expected_progress = (elapsed_days / total_days) * 100

    # Item is trending late if actual progress is behind expected
    # Use a small buffer (5%) to avoid false positives
    return item.percent_complete < (expected_progress - 5)


# =============================================================================
# BATCH OPERATIONS
# =============================================================================


def calculate_indicators_batch(
    items: list[Item], today: Optional[date] = None
) -> list[tuple[Item, Optional[Indicator]]]:
    """
    Calculate indicators for a batch of items.

    Args:
        items: List of items to calculate indicators for
        today: Reference date for calculation (defaults to today)

    Returns:
        List of (item, indicator) tuples
    """
    if today is None:
        today = date.today()

    return [(item, calculate_indicator(item, today)) for item in items]


def get_indicator_severity(indicator: Optional[Indicator]) -> int:
    """
    Get the severity level of an indicator for sorting.

    Higher values = more severe/urgent.

    Args:
        indicator: The indicator to get severity for

    Returns:
        Severity level (0-10, higher is more severe)
    """
    severity_map = {
        None: 0,
        Indicator.COMPLETED: 1,
        Indicator.COMPLETED_RECENTLY: 2,
        Indicator.NOT_STARTED: 3,
        Indicator.STARTING_SOON: 4,
        Indicator.IN_PROGRESS: 5,
        Indicator.FINISHING_SOON: 6,
        Indicator.TRENDING_LATE: 7,
        Indicator.LATE_START: 8,
        Indicator.LATE_FINISH: 9,
        Indicator.BEYOND_DEADLINE: 10,
    }
    return severity_map.get(indicator, 0)

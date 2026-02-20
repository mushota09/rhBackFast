"""Leave management utility functions"""
from datetime import date, timedelta
from typing import List


def is_weekend(d: date) -> bool:
    """
    Check if a date is a weekend (Saturday or Sunday)

    Args:
        d: Date to check

    Returns:
        True if the date is Saturday (5) or Sunday (6), False otherwise
    """
    return d.weekday() >= 5


def count_working_days(
    date_debut: date,
    date_fin: date,
    holidays: List[date]
) -> int:
    """
    Count working days between two dates, excluding weekends and holidays

    Args:
        date_debut: Start date (inclusive)
        date_fin: End date (inclusive)
        holidays: List of holiday dates to exclude

    Returns:
        Number of working days (excluding weekends and holidays)
    """
    if date_debut > date_fin:
        return 0

    count = 0
    current = date_debut

    while current <= date_fin:
        if not is_weekend(current) and current not in holidays:
            count += 1
        current += timedelta(days=1)

    return count


def dates_overlap(
    start1: date,
    end1: date,
    start2: date,
    end2: date
) -> bool:
    """
    Check if two date ranges overlap

    Args:
        start1: Start date of first range
        end1: End date of first range
        start2: Start date of second range
        end2: End date of second range

    Returns:
        True if the date ranges overlap, False otherwise
    """
    return start1 <= end2 and start2 <= end1

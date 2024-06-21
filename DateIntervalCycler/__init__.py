"""
DateIntervalCycler(cycles, first_interval_start, last_interval_end, start_before_first_interval)

A class that cycles through datetime intervals based on provided (month, day) tuples.

This class is used to generate a datetime series of intervals that follow the user
specified interval cycles. If cycles contains (2, 29), then it will honor leap years
by setting the interval date time (2, 28) for non-leap years. However, if the cycles
contains both (2, 28) and (2, 29), then it will skip using (2, 29) for non-leap years.

This docstring uses dt as shorthand for a datetime.datetime object; dt.date for a
datetime.date object; and cycler for a DateIntervalCycler object.

Args:
    cycles (Sequence[tuple[int, int]]): Sequence of (month, day) tuples defining the interval cycles.
    first_interval_start (Union[dt, dt.date]): The start date of the first interval.
    last_interval_end (Union[None, dt, dt.date]): The end date of the last interval. Defaults to None.
    start_before_first_interval (bool): Flag to start before the first interval. Defaults to False.
                                        If False, then first call to next() moves to the second interval.
                                        If True, then it requires two calls to next() to get the second interval.

Attributes:
    cycles (np.ndarray): Immutable numpy array whose rows are the (month, day) that each interval cycles through.

    size (int): The number of intervals from first_interval_start to last_interval_end.
                If last_interval_end is None, returns MAX_INTERVAL.

    first_interval_start (dt): The start date of the first interval.
    last_interval_end (Union[dt, None]): The end date of the last interval, or None if not set.

    at_first_interval(bool): Check if the current interval is the first.
    at_last_interval(bool): Check if the current interval is the last.

    index (int): The current interval index.

    interval (tuple[dt, dt]): The current interval start and end dates.
    interval_start (dt): The start date of the current interval.
    interval_end (dt): The end date of the current interval.
    interval_length (float): The number of days between interval_end and interval_start.


    MONTH_DAYS_LEAP (np.ndarray): Days in each month of a leap year.
    MONTH_DAYS_NOLEAP (np.ndarray): Days in each month of a non-leap year.
    MAX_INTERVAL (int): Maximum number of allowed intervals.



Methods:

    from_year(cycles, year_start, starting_cycle_index=0, year_end=None, ending_cycle_index=0):
        Create a DateIntervalCycler from a starting year and cycles index.

    with_monthly(first_interval_start, last_interval_end=None, start_before_first_interval=False):
        Create a DateIntervalCycler with monthly interval's starting on the first of each month.

    with_monthly_end(first_interval_start, last_interval_end=None, start_before_first_interval=False):
        Create a DateIntervalCycler with monthly interval's ending on the last day of each month.

    with_daily(first_interval_start, last_interval_end=None, start_before_first_interval=False):
        Create a DateIntervalCycler with daily intervals.

    copy(reset=False, shallow_copy_cycles=True):
        Creates a copy of the DateIntervalCycler object.

    reset(start_before_first_interval=False):
        Resets the current interval to the first interval.

    tolist(start_override=None, end_override=None, from_current_position=False):
        Converts the intervals to a list.

    set_first_interval_start(first_interval_start, start_before_first_interval=False):
        Sets the start date of the interval range. Changing the start date invokes reset().

    set_last_interval_end(date):
        Sets the end date of the interval range. It must be greater than first_interval_start.

    next(allowStopIteration=False) -> int:
        Advances to the next date interval.

    back(allowStopIteration=False) -> int:
        Moves back to the previous date interval.

    next_get(allowStopIteration=False) -> tuple[dt, dt]:
        Advances to the next interval and returns its start and end dates.

    back_get(allowStopIteration=False) -> tuple[dt, dt]:
        Moves back to the previous interval and returns its start and end dates.

    iter(reset_to_start=False) -> Iterator[tuple[dt, dt]]:
        Returns an iterator for the intervals.

    index_to_interval(index, only_start=False, only_end=False) -> tuple[dt, dt]:
        Given an index, returns the corresponding interval.***

    index_from_date(date) -> int:
        Returns the index of the interval that contains the given date.

    interval_from_date(date) -> int:
        Given a date, return the corresponding interval that contains it.

    is_leap(year: int) -> bool:
        Checks if a given year is a leap year.

    month_days(month: int, leap: bool = False) -> int:
        Returns the number of days in a given month, considering leap years.

Examples:
    >>> from datetime import datetime
    >>> cycles = [(3, 1), (6, 1), (9, 1), (12, 1)]
    >>> cid = DateIntervalCycler(cycles, datetime(2020, 1, 1))
    >>> cid.next_get()
    (datetime.datetime(2020, 3, 1, 0, 0), datetime.datetime(2020, 6, 1, 0, 0))
    >>> cid.next_get()
    (datetime.datetime(2020, 6, 1, 0, 0), datetime.datetime(2020, 9, 1, 0, 0))
    >>> cid.back_get()
    (datetime.datetime(2020, 3, 1, 0, 0), datetime.datetime(2020, 6, 1, 0, 0))

    >>> cid = DateIntervalCycler.with_monthly(datetime(2020, 1, 1))
    >>> cid.next_get()
    (datetime.datetime(2020, 1, 1, 0, 0), datetime.datetime(2020, 2, 1, 0, 0))
    >>> cid.next_get()
    (datetime.datetime(2020, 2, 1, 0, 0), datetime.datetime(2020, 3, 1, 0, 0))

    >>> cid = DateIntervalCycler.with_daily(datetime(2020, 1, 1))
    >>> cid.next_get()
    (datetime.datetime(2020, 1, 1, 0, 0), datetime.datetime(2020, 1, 2, 0, 0))
    >>> cid.next_get()
    (datetime.datetime(2020, 1, 2, 0, 0), datetime.datetime(2020, 1, 3, 0, 0))

***interval_from_date is much faster than index_to_interval.
    If you need both the index and interval for a given date, then do not do

    >>> from datetime import datetime
    >>> cid = DateIntervalCycler.with_monthly(datetime(2020, 1, 1))
    >>> #
    >>> # this is slower:
    >>> #
    >>> index = DateIntervalCycler.index_from_date(date)       # slow method
    >>> interval = DateIntervalCycler.index_to_interval(index) # slow method
    >>> #
    >>> # then doing this:
    >>> #
    >>> index = DateIntervalCycler.index_from_date(date)       # slow method
    >>> interval = DateIntervalCycler.interval_from_date(date) # fast method

"""

from .DateIntervalCycler import DateIntervalCycler

__all__ = [
    "DateIntervalCycler",
]

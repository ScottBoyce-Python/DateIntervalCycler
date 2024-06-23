from typing import Sequence, Union, Optional, Iterator
import datetime as dt

try:
    from _metadata import (
        __version__,
        __author__,
        __email__,
        __license__,
        __status__,
        __maintainer__,
        __credits__,
        __url__,
        __description__,
        __copyright__,
    )
except ImportError:
    __version__ = "Failed to load from _metadata.py"
    __author__ = __version__
    __email__ = __version__
    __license__ = __version__
    __status__ = __version__
    __maintainer__ = __version__
    __credits__ = __version__
    __url__ = __version__
    __description__ = __version__
    __copyright__ = __version__

FEB28 = (2, 28)
FEB29 = (2, 29)
NUL = dt.datetime(1, 1, 1)

__all__ = [
    "DateIntervalCycler",
]

# Days in each month of a leap year, used for validation.
_month_days_29 = (0, 31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)
_month_days_28 = (0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)


def _is_leap(year: int) -> bool:
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)


def _intervals_to_array(cycles: Sequence[tuple[int, int]]) -> tuple[tuple[int, int]]:
    """
    Safely build a tuple[tuple[int, int]] from cycle intervals from a list of tuples.

    This method drops duplicates, sorts the list of tuples, and converts it to a tuple[tuple[int, int]] object.

    Args:
        cycles (Sequence[tuple[int, int]]): A sequence of (month, day) tuples.

    Returns:
        tuple[tuple[int, int]]: A sorted and deduplicated array of intervals.
    """
    return tuple(sorted(set([(r[0], r[1]) for r in cycles])))


class DateIntervalCycler:
    """
    A class that efficiently cycles through datetime intervals generated from a
    start date and list of (month, day) tuples.

    This class is used to generate a datetime series of intervals that follow the user
    specified interval cycles. If cycles contains (2, 29), then it will honor leap years
    by setting the interval date time (2, 28) for non-leap years. However, if the cycles
    contains both (2, 28) and (2, 29), then it will skip using (2, 29) for non-leap years.

    Supports basic indexing, cid[4], cid[date], cid[4:10], which are syntactic sugar
    for the index_to_interval, interval_from_date, and tolist methods, respectively.

    This docstring uses `dt` as shorthand for a `datetime.datetime` object; `dt.date` for a
    `datetime.date` object.

    cid = DateIntervalCycler(cycles, first_interval_start, last_interval_end, start_before_first_interval)

    Args:
        cycles (Sequence[tuple[int, int]]):                     Sequence of (month, day) tuples that
                                                                are cycled through to construct the
                                                                datetime intervals.
        first_interval_start (Union[dt, dt.date]):              The start date of the first interval.
        last_interval_end (Union[None, dt, dt.date], optional): The end date of the last interval.
                                                                Defaults to None.
        start_before_first_interval (bool, optional):           Flag to start before the first interval.
                                                                Defaults to False.
                                                                If False, then first call to next() moves to the second interval.
                                                                If True, then it requires two calls to next() to get the second interval.

    Attributes:
        cycles (tuple[tuple[int, int]]): Tuple of (month, day) tuples that are cycled
                                         through to construct the datetime intervals.

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


        MONTH_DAYS_LEAP (tuple): Days in each month of a leap year (non-zero month number is index).
        MONTH_DAYS_NOLEAP (tuple): Days in each month of a non-leap year (non-zero month number is index).
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

        copy(reset=False):
            Creates a copy of the DateIntervalCycler object.

        reset(start_before_first_interval=False):
            Resets the current interval to the first interval.

        tolist(start_override=None, end_override=None, from_current_position=False,
               only_start=False, only_end=False, step=1) -> list[Union[dt.datetime, tuple[dt.datetime, dt.datetime]]]:
            Converts the intervals to a list.

        totuple(start_override=None, end_override=None, from_current_position=False
                ) -> list[Union[dt.datetime, tuple[dt.datetime, dt.datetime]]]:
            Return a tuple containing the first_interval_start, and then all the remaining
            interval_end dates (including last_interval_end).
            Note: `cid.totuple() == tuple(cid.tolist(only_start=True)) + (cid.last_interval_end,)`

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

        iter(only_start=False, only_end=False, reset_to_start=False) -> Iterator[Union[dt,tuple[dt, dt]]]:
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

    MONTH_DAYS_LEAP = _month_days_29
    MONTH_DAYS_NOLEAP = _month_days_28

    MAX_INTERVAL: int = 2000000000  # int32 maxval is 2,147,483,647

    cycles: tuple[tuple[int, int]]

    _dim: int  # size of cycles
    _len: int  # Interval count from _first_start_date to _last_end_date, is MAX_INTERVAL if _last_end_date is None
    _y: int  # The year of interval_start (start date of the current interval)
    _p: int  # cycles index for interval_start, unless at the first interval, then interval_end index
    _p0: int  # cycles index of interval_end for the first interval
    _ind: int  # current interval index

    _end_of_feb_check: bool  # If true then february needs to adjust for 28/29 based on year
    _end_of_feb_check_has_28: bool  # If true then _end_of_feb_check is true and cycle intervals contains (2, 28)
    _p_feb_29: int  # Index to (2, 29) in cycles, otherwise MAX_INTERVAL

    _at_first_interval: int  # 0 indicates not at first, 1 is at first, -1 is before first, >1 is error call from back
    _at_last_interval: int  # 0 indicates not at end, 1 is at end
    _started_before_first_interval: bool

    _p0_date: dt.datetime  # datetime at self._p0
    _first_start_date: dt.datetime  # datetime at start of series
    _last_end_date: dt.datetime  # datetime at the end of series, is None if no ending specified
    _has_last_end_date: bool  # True if _last_end_date is not None

    def __init__(
        self,
        cycles: Sequence[tuple[int, int]],
        first_interval_start: Union[dt.datetime, dt.date],
        last_interval_end: Union[None, dt.datetime, dt.date] = None,
        start_before_first_interval: bool = False,
        *,
        _internal_copy_init: int = 0,
    ):
        """
        Initialize the DateIntervalCycler.

        Args:
            cycles (Sequence[tuple[int, int]]): Sequence of (month, day) tuples defining the intervals.
            first_interval_start (Union[dt.datetime, dt.date]): The start date of the first interval.
            last_interval_end (Union[None, dt.datetime, dt.date], optional): The end date of the last
                                                                             interval. Defaults to None.
            start_before_first_interval (bool, optional): Flag to start before the first interval. Defaults to False.
                                                          If False, then first call to next() moves to the second interval.
                                                          If True, then it requires two calls to next() to get the second interval.
                                                             This is useful if you need to call next() at the start of a loop,
                                                             but want the first loop to include the first interval
            _internal_copy_init (int, optional): Internal flag used by class for fast copying. Defaults to 0.
        """
        if _internal_copy_init:
            self.cycles = cycles

            self._first_start_date = first_interval_start
            self._last_end_date = last_interval_end
            self._dim = len(cycles)
            self._started_before_first_interval = start_before_first_interval

            self._has_last_end_date = False
            self._end_of_feb_check = False
            self._end_of_feb_check_has_28 = False
            self._p_feb_29 = DateIntervalCycler.MAX_INTERVAL
            self._y = 0
            self._p = 0
            self._p0 = 0
            self._p0_date = NUL
            self._ind = 0
            self._len = 0
            self._at_first_interval = 0
            self._at_last_interval = 0
            return

        # Extract rows, drop duplicates, sort rows, then store as tuple[tuple[int, int]] array
        self.cycles = _intervals_to_array(cycles)

        self._dim = len(cycles)
        self._end_of_feb_check = False
        self._end_of_feb_check_has_28 = False
        self._p_feb_29 = DateIntervalCycler.MAX_INTERVAL
        self._p0_date = NUL

        self._has_last_end_date = False
        self._at_first_interval = 0
        self._at_last_interval = 0

        if self._dim < 1:
            raise ValueError("\nDateIntervalCycler: len(cycles) must be greater than zero.")

        # Validate the date intervals and check for leap year considerations
        for i, (vm, vd) in enumerate(cycles):
            if vd < 1 or vm < 1 or vm > 12 or _month_days_29[vm] < vd:
                raise ValueError(f"\nDateIntervalCycler: Invalid (month, day) entry at cycles[{i}] = ({vm}, {vd})")

        self._end_of_feb_check = FEB29 in self.cycles

        if self._end_of_feb_check:
            self._p_feb_29 = self.cycles.index(FEB29)

        self._end_of_feb_check_has_28 = self._end_of_feb_check and FEB28 in self.cycles

        self.set_first_interval_start(first_interval_start, start_before_first_interval)
        self.set_last_interval_end(last_interval_end)

    @property
    def size(self) -> int:
        """
        Returns the number of intervals. If last_interval_end is None,
        returns DateIntervalCycler.MAX_INTERVAL.

        Returns:
            int: The number of intervals.
        """
        return self._len

    @property
    def first_interval_start(self) -> dt.datetime:
        """
        Get the start date of the first interval.

        Returns:
            dt.datetime: The start date of the first interval.
        """
        return self._first_start_date

    @property
    def last_interval_end(self) -> Union[dt.datetime, None]:
        """
        Get the end date of the last interval.

        Returns:
            Union[dt.datetime, None]: The end date of the last interval.
        """
        return self._last_end_date

    @property
    def at_first_interval(self) -> bool:
        """
        Check if the current interval is the first.

        Returns:
            bool: If current interval is the first.
        """
        return self._at_first_interval != 0

    @property
    def at_last_interval(self) -> Union[dt.datetime, None]:
        """
        Check if the current interval is the last.

        Returns:
            bool: If current interval is the last.
        """
        return self._at_last_interval != 0

    @property
    def index(self) -> int:
        """
        Get the current interval index.

        Returns:
            int: The current interval index.
        """
        return self._ind

    @property
    def interval(self) -> tuple[dt.datetime, dt.datetime]:
        """
        Get the current interval start and end dates.

        Returns:
            tuple[dt.datetime, dt.datetime]: The start and end dates of the current interval.
        """
        return self.interval_start, self.interval_end

    @property
    def interval_start(self) -> dt.datetime:
        """
        Get the start date of the current interval.

        Returns:
            dt.datetime: The start date of the current interval.
        """
        if self._at_first_interval:
            return self._first_start_date
        if self._end_of_feb_check:
            return self._get_end_of_feb_check_date(self._p)

        return self._to_datetime(self._p)

    @property
    def interval_end(self) -> dt.datetime:
        """
        Get the end date of the current interval.

        Returns:
            dt.datetime: The end date of the current interval.
        """
        if self._at_last_interval:
            return self._last_end_date
        if self._at_first_interval:
            if self._end_of_feb_check:
                return self._get_end_of_feb_check_date(self._p)
            return self._to_datetime(self._p)
        if self._end_of_feb_check:
            return self._get_end_of_feb_check_date(self._p + 1)
        return self._to_datetime(self._p + 1)

    @property
    def interval_length(self) -> float:
        """
        Get the length of the current interval in days.

        Returns:
            float: The length of the current interval in days.
        """
        return (self.interval_end - self.interval_start).total_seconds() / 86400.0

    @classmethod
    def from_year(
        cls,
        cycles: Sequence[tuple[int, int]],
        year_start: int,
        starting_cycle_index=0,
        year_end: Optional[int] = None,
        ending_cycle_index: Optional[int] = 0,
    ) -> "DateIntervalCycler":
        """
        Create a DateIntervalCycler from a starting year and cycles index.
        Equivalent to:
           DateIntervalCycler(cycles, dt.datetime(year_start, *cycles[starting_cycle_index]))

        Args:
            cycles (Sequence[tuple[int, int]]): Sequence of (month, day) tuples defining the interval cycles.
            year_start (int): The year assigned to the start of the first interval.
            starting_cycle_index (int, optional): Index of cycle that is the month and day assigned
                                                  to the start of the first interval. Defaults to 0.
            year_end (Optional[int], optional): The year assigned to the end of the last interval. Defaults to None.
            ending_cycle_index (Optional[int], optional):  Index of cycle that is the month and day assigned
                                                           to the end of the last interval. Defaults to 0.

        Returns:
            DateIntervalCycler: The initialized DateIntervalCycler object.
        """
        cycles = _intervals_to_array(cycles)
        m, d = cycles[starting_cycle_index]
        start = dt.datetime(year_start, m, d)
        if year_end is None:
            end = None
        else:
            m, d = cycles[ending_cycle_index]
            end = dt.datetime(year_end, m, d)

        return cls(cycles, start, end)

    @classmethod
    def with_monthly(
        cls,
        first_interval_start: Union[dt.datetime, dt.date],
        last_interval_end: Union[None, dt.datetime, dt.date] = None,
        start_before_first_interval: bool = False,
    ) -> "DateIntervalCycler":
        """
        Create a DateIntervalCycler with monthly intervals starting on the first of each month.

        Args:
            first_interval_start (Union[dt.datetime, dt.date]): The start date of the first interval.
            last_interval_end (Union[None, dt.datetime, dt.date], optional): The end date of the last interval.
                                                                             Defaults to None.
            start_before_first_interval (bool, optional): Flag to start before the first interval. Defaults to False.
                                                          If False, then first call to next() moves to the second interval.
                                                          If True, then it requires two calls to next() to get the second interval.

        Returns:
            DateIntervalCycler: The initialized DateIntervalCycler object with monthly intervals.
        """
        return cls([(m, 1) for m in range(1, 13)], first_interval_start, last_interval_end, start_before_first_interval)

    @classmethod
    def with_monthly_end(
        cls,
        first_interval_start: Union[dt.datetime, dt.date],
        last_interval_end: Union[None, dt.datetime, dt.date] = None,
        start_before_first_interval: bool = False,
    ) -> "DateIntervalCycler":
        """
        Create a DateIntervalCycler with monthly interval's ending on the last day of each month.

        Args:
            first_interval_start (Union[dt.datetime, dt.date]): The start date of the first interval.
            last_interval_end (Union[None, dt.datetime, dt.date], optional): The end date of the last interval.
                                                                             Defaults to None.
            start_before_first_interval (bool, optional): Flag to start before the first interval. Defaults to False.
                                                          If False, then first call to next() moves to the second interval.
                                                          If True, then it requires two calls to next() to get the second interval.

        Returns:
            DateIntervalCycler: The initialized DateIntervalCycler object with monthly interval's ending on the last day of each month.
        """
        return cls(
            [(m, _month_days_29[m]) for m in range(1, 13)],
            first_interval_start,
            last_interval_end,
            start_before_first_interval,
        )

    @classmethod
    def with_daily(
        cls,
        first_interval_start: Union[dt.datetime, dt.date],
        last_interval_end: Union[None, dt.datetime, dt.date] = None,
        start_before_first_interval: bool = False,
    ) -> "DateIntervalCycler":
        """
        Create a DateIntervalCycler with daily intervals.

        Args:
            first_interval_start (Union[dt.datetime, dt.date]): The start date of the first interval.
            last_interval_end (Union[None, dt.datetime, dt.date], optional): The end date of the last interval.
                                                                             Defaults to None.
            start_before_first_interval (bool, optional): Flag to start before the first interval. Defaults to False.
                                                          If False, then first call to next() moves to the second interval.
                                                          If True, then it requires two calls to next() to get the second interval.

        Returns:
            DateIntervalCycler: The initialized DateIntervalCycler object with daily intervals.
        """
        return cls(
            [(m, d) for m in range(1, 13) for d in range(1, _month_days_29[m] + 1)],
            first_interval_start,
            last_interval_end,
            start_before_first_interval,
        )

    @staticmethod
    def is_leap(year: int) -> bool:
        """
        Check if a given year is a leap year.

        Args:
            year (int): The year to check.

        Returns:
            bool: True if the year is a leap year, False otherwise.
        """
        return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)

    @staticmethod
    def month_days(month: int, leap: bool = False) -> int:
        """
        Get the number of days in a given month, considering leap years.

        Args:
            month (int): The month to check.
            leap (bool, optional): Flag to consider leap year. Defaults to False.

        Returns:
            int: The number of days in the month.
        """
        if month < 1 or 12 < month:
            raise ValueError(f"\nDateIntervalCycler.month_days: month must be between 1 and 12, but received: {month}")
        if leap:
            return _month_days_29[month]
        return _month_days_28[month]

    def copy(self, reset: bool = False) -> "DateIntervalCycler":
        """
        Creates a copy of the DateIntervalCycler object.

        Args:
            reset (bool, optional): Reset the copy to the first interval. Defaults to False.

        Returns:
            DateIntervalCycler: The copied DateIntervalCycler object.
        """
        copy_flag = 1

        cid = DateIntervalCycler(
            self.cycles,
            self._first_start_date,
            self._last_end_date,
            self._started_before_first_interval,
            _internal_copy_init=copy_flag,
        )

        cid._has_last_end_date = self._has_last_end_date
        cid._end_of_feb_check = self._end_of_feb_check
        cid._end_of_feb_check_has_28 = self._end_of_feb_check_has_28
        cid._p_feb_29 = self._p_feb_29
        cid._y = self._y
        cid._p = self._p
        cid._p0 = self._p0
        cid._p0_date = self._p0_date
        cid._ind = self._ind
        cid._len = self._len
        cid._at_first_interval = self._at_first_interval
        cid._at_last_interval = self._at_last_interval

        if reset:
            cid.reset(self._started_before_first_interval)

        return cid

    def set_first_interval_start(
        self, first_interval_start: Union[dt.datetime, dt.date], start_before_first_interval: bool = False
    ):
        """
        Set the start date of the interval range.

        Args:
            first_interval_start (Union[dt.datetime, dt.date]): The start date of the first interval.
            start_before_first_interval (bool, optional): Flag to start before the first interval. Defaults to False.
                                                          If False, then first call to next() moves to the second interval.
                                                          If True, then it requires two calls to next() to get the second interval.
        """
        date = first_interval_start
        if type(date) is not dt.datetime:
            try:
                date = dt.datetime(date.year, date.month, date.day)
            except AttributeError:
                raise ValueError(
                    "\nDateIntervalCycler.set_first_interval_start: Invalid first_interval_start.\n"
                    f"Received: {first_interval_start}"
                )

        self._first_start_date = date
        self._at_first_interval = 1

        self.reset(start_before_first_interval, set_p0=True)  # must reset p0 and p0_date

        if self._has_last_end_date and self._last_end_date <= self._p0_date:
            self._started_before_first_interval = (
                False  # No intervals, only contains (first_interval_start, last_interval_end)
            )
            self._at_last_interval = 1
            self._len = 1

    def set_last_interval_end(self, last_interval_end: Union[None, dt.datetime, dt.date]):
        """
        Set the end date of the interval range.

        Args:
            last_interval_end (Union[None, dt.datetime, dt.date], optional): The end date of the last interval.
        """
        date = last_interval_end
        if date is not None and type(date) is not dt.datetime:
            try:
                date = dt.datetime(date.year, date.month, date.day)
            except AttributeError:
                raise ValueError(
                    "\nDateIntervalCycler.set_last_interval_end: Invalid last_interval_end.\n"
                    f"Received: {last_interval_end}"
                )

        self._last_end_date = date
        self._has_last_end_date = date is not None
        self._start_less_end_check()

        if self._has_last_end_date and self._last_end_date <= self._p0_date:
            self._started_before_first_interval = False  # No intervals, only contains (start, end)
            self._at_first_interval = 1
            self._at_last_interval = 1
            self._len = 1
        elif self._has_last_end_date:
            self._len = self.index_from_date(date)
        else:
            self._len = DateIntervalCycler.MAX_INTERVAL

    def reset(self, start_before_first_interval: bool = False, *, set_p0: bool = False):
        """
        Reset the DateIntervalCycler to the first interval.

        Args:
            start_before_first_interval (bool, optional): Flag to start before the first interval. Defaults to False.
                                                          If False, then first call to next() moves to the second interval.
                                                          If True, then it requires two calls to next() to get the second interval.
            set_p0 (bool, optional): Internal flag to update self._p0 and self._p0_date. Defaults to False.
        """
        self._y = self._first_start_date.year

        if set_p0:
            self._p0 = len(self.cycles)
            for i, (vm, vd) in enumerate(self.cycles):
                if self._end_of_feb_check and i == self._p_feb_29 and not _is_leap(self._y):
                    # Feb 29 is invalid, either use Feb 28 or move to next cycle
                    vd = 28
                    if self._end_of_feb_check_has_28:
                        continue  # 28 was previous cycle move to next cycle
                if self._first_start_date < dt.datetime(self._y, vm, vd):
                    self._p0 = i
                    break
            self._p0_date = self._to_datetime(self._p0, self._y)

        self._p = self._p0
        self._ind = 0
        if not (self._at_first_interval != 0 and self._at_last_interval != 0):
            # Do not set if only one interval defined
            self._started_before_first_interval = start_before_first_interval
            self._at_first_interval = -1 if start_before_first_interval else 1
            self._at_last_interval = 0

    def next_get(self, allowStopIteration=False) -> tuple[dt.datetime, dt.datetime]:
        """
        Advance to the next interval and return its start and end dates.
        If at the last interval, then continues to return the last interval, unless
        allowStopIteration is True, then raises a StopIteration exception.

        Args:
            allowStopIteration (bool, optional): Flag to allow StopIteration exception if current
                                                 interval is the last. Defaults to False.

        Returns:
            tuple[dt.datetime, dt.datetime]: The start and end dates of the next interval.
        """
        self.next(allowStopIteration)
        return self.interval_start, self.interval_end

    def back_get(self, allowStopIteration=False) -> tuple[dt.datetime, dt.datetime]:
        """
        Move back to the previous interval and return its start and end dates.
        If at the first interval, then continues to return the first interval, unless
        allowStopIteration is True, then raises a StopIteration exception.

        Args:
            allowStopIteration (bool, optional): Flag to allow StopIteration exception if current
                                                 interval is the first. Defaults to False.

        Returns:
            tuple[dt.datetime, dt.datetime]: The start and end dates of the previous interval.
        """
        self.back(allowStopIteration)
        return self.interval_start, self.interval_end

    def next(self, allowStopIteration=False) -> int:
        """
        Advance to the next date interval.

        Args:
            allowStopIteration (bool, optional): Flag to allow StopIteration exception if current
                                                 interval is the last. Defaults to False.

        Returns:
            int: 0 if successful, otherwise the fail count.
        """
        if self._at_last_interval:
            self._at_last_interval += 1
            if allowStopIteration:
                raise StopIteration("\nDateIntervalCycler.next cannot go beyond the ending date")
            return self._at_last_interval - 1

        if self._at_first_interval:
            if self._at_first_interval == -1:
                # Flag to indicate before start of intervals, enable flag for first and return
                self._at_first_interval = 1
                return 0
            self._at_first_interval = 0
            self._p -= 1

        self._p_next()  # p += 1
        self._ind += 1

        if self._has_last_end_date and self._y + 1 >= self._last_end_date.year:
            # if self._y == self._last_end_date.year or (self._p + 1 == self._dim and self._y+1 == self._last_end_date.year):
            if self._last_end_date <= self._to_datetime(self._p + 1):
                if self._end_of_feb_check_has_28 and self._p == self._p_feb_29:
                    # at (2, 29) and know there is (2, 28)
                    if not _is_leap(self._y):
                        self._p_back()  # p -= 1
                self._at_last_interval = 1
                return 0

        if self._end_of_feb_check_has_28 and self._p == self._p_feb_29:
            # at (2, 29) and know there is (2, 28)
            if not _is_leap(self._y):
                self._p_next()  # p += 1 because Feb 29 is invalid for this year and 28 is defined
        return 0

    def back(self, allowStopIteration=False) -> int:
        """
        Move back to the previous date interval, wrapping around to the previous year if necessary.

        Args:
            allowStopIteration (bool, optional): Flag to allow StopIteration exception if current
                                                 interval is the first. Defaults to False.

        Returns:
            int: 0 if successful, otherwise the fail count.
        """
        if self._at_first_interval:
            if self._at_first_interval == -1:  # Flag to indicate before start of intervals, but requested back?
                self._at_first_interval = 1
            self._at_first_interval += 1
            if allowStopIteration:
                raise StopIteration("\nDateIntervalCycler.back cannot go beyond the starting date.")
            return self._at_first_interval - 1  # Number of times a StopIteration would have occurred

        if self._at_last_interval:
            self._at_last_interval = 0

        self._p_back()  # p -= 1
        self._ind -= 1

        if self._y <= self._first_start_date.year + 1:
            if self._to_datetime(self._p) <= self._first_start_date:
                self.reset()
                return 0

        if self._end_of_feb_check_has_28 and self._p == self._p_feb_29:
            if not _is_leap(self._y):
                self._p_back()  # p -= 1 because Feb 29 is invalid for this year and 28 is defined
        return 0

    def iter(
        self, only_start: bool = False, only_end: bool = False, reset_to_start=False
    ) -> Iterator[Union[dt.datetime, tuple[dt.datetime, dt.datetime]]]:
        """
        Returns an iterator for the intervals. The first next call returns the
        current interval start and end dates. Each subsequent next call returns the
        next interval's start and end date. This continues until the last interval.
        If last_interval_end is None, then iterator will continue indefinitely.

        Args:
            reset_to_start (bool, optional): Flag to have the iterator start at the first interval,
                                             otherwise returns current interval. Defaults to False.
            only_start (bool, optional): Flag to iterate only the start date.
                                         Defaults to False.
            only_end (bool, optional): Flag to iterate only the end date.
                                       Defaults to False.

        Returns:
            Iterator[tuple[dt.datetime, dt.datetime]]: The iterator object.
        """
        if self._at_first_interval != 0 and self._at_last_interval != 0:
            if only_start:
                yield self.interval_start
            elif only_end:
                yield self.interval_end
            else:
                yield self.interval
            return

        if reset_to_start:
            self.reset()

        if only_start:
            if self._started_before_first_interval:
                while not self.next():
                    yield self.interval_start
            else:
                while True:
                    yield self.interval_start
                    if self.next():  # reached end of range
                        return
        elif only_end:
            if self._started_before_first_interval:
                while not self.next():
                    yield self.interval_end
            else:
                while True:
                    yield self.interval_end
                    if self.next():  # reached end of range
                        return
        else:
            if self._started_before_first_interval:
                while not self.next():
                    yield self.interval
            else:
                while True:
                    yield self.interval
                    if self.next():  # reached end of range
                        return

    def index_to_interval(
        self, index, only_start: bool = False, only_end: bool = False
    ) -> Union[dt.datetime, tuple[dt.datetime, dt.datetime], None, tuple[None, None]]:
        """
        Given an index, return the corresponding date interval.

        Args:
            index (int): The index of the interval.
            only_start (bool, optional): Flag to return only the start date.
                                         Defaults to False.
            only_end (bool, optional): Flag to return only the end date.
                                       Defaults to False.

        Returns:
            Union[dt.datetime, tuple[dt.datetime, dt.datetime], None, tuple[None, None]]: The start
                                 and end dates of the interval. Returns None if a bad date is given.
        """
        if only_start and only_end:
            only_start = False
            only_end = False

        if index < 0 or index > self._len:
            if only_start or only_end:
                return None
            return (None, None)

        if index == 0:
            if only_start:
                return self._first_start_date
            if only_end:
                return self._p0_date  # self._to_datetime(self._p0, self._first_start_date.year)
            return (self._first_start_date, self._p0_date)

        if index == self._len:
            if only_start or only_end:
                return self._last_end_date
            return (self._last_end_date, self._last_end_date)

        if index == self._len - 1:
            if only_end:
                return self._last_end_date
            y = self._last_end_date.year
            pN = self._dim - 1
            for p in range(self._dim):
                if self._last_end_date <= self._to_datetime(p, y):
                    pN = p - 1
                    break
            if pN < 0:
                pN = self._dim - 1
                y -= 1
            if only_start:
                return self._to_datetime(pN, y)
            return (self._to_datetime(pN, y), self._last_end_date)

        if self._end_of_feb_check_has_28:
            return self._index_to_interval_end_of_feb_check(index, only_start, only_end)

        y = self._first_start_date.year

        if index + self._p0 - 1 < self._dim:  # within the first year
            return self._index_to_interval_return(index + self._p0 - 1, y, only_start, only_end)

        y += 1
        index -= self._dim - self._p0 + 1
        while index >= self._dim:
            index -= self._dim
            y += 1
        return self._index_to_interval_return(index, y, only_start, only_end)

    def index_from_date(self, date: Union[dt.datetime, dt.date]) -> int:
        """
        Return the index of the interval that contains the given date.

        Args:
            date (Union[dt.datetime, dt.date]): The date to find the index for.

        Returns:
            int: The index of the interval that contains the date.
        """
        if not isinstance(date, dt.datetime):
            date = dt.datetime(date.year, date.month, date.day)
        if date < self._first_start_date:
            return -1
        if self._has_last_end_date and date > self._last_end_date:
            return -2
        if self._at_first_interval != 0 and self._at_last_interval != 0:
            return 0
        if date < self._p0_date:  # self._to_datetime(self._p0, self._first_start_date.year)
            return 0
        if self._end_of_feb_check_has_28:
            return self._index_from_date_end_of_feb_check(date)

        end_date_add = 0
        if self._has_last_end_date and date == self._last_end_date:
            date += dt.timedelta(days=-1)  # ensures it will capture the last interval
            end_date_add = 1  # add one more because this date is technically beyond the series

        sy = self._first_start_date.year
        vy, vm, vd = date.year, date.month, date.day
        if sy == vy:
            ind = 0
            for i in range(self._p0, self._dim):
                m, d = self.cycles[i]
                if vm < m or (vm <= m and vd < d):
                    break
                ind += 1
            return ind + end_date_add

        # number of years * interval count + intervals of the first year
        ind = (vy - sy - 1) * self._dim + self._dim - self._p0
        for i in range(self._dim):
            m, d = self.cycles[i]
            if vm < m or (vm <= m and vd < d):
                break
            ind += 1
        return ind + end_date_add

    def interval_from_date(
        self, date: Union[dt.datetime, dt.date], only_start: bool = False, only_end: bool = False
    ) -> Union[dt.datetime, tuple[dt.datetime, dt.datetime], None, tuple[None, None]]:
        """
        Given a date, return the corresponding interval that contains it.

        Args:
            date (Union[dt.datetime, dt.date]): The date to find the interval with.
            only_start (bool, optional): Flag to return only the start date.
                                         Defaults to False.
            only_end (bool, optional): Flag to return only the end date.
                                       Defaults to False.

        Returns:
            Union[dt.datetime, tuple[dt.datetime, dt.datetime], None, tuple[None, None]]: The start
                                 and end dates of the interval. Returns None if a bad date is given.
        """
        if only_start and only_end:
            only_start = False
            only_end = False

        if date < self._first_start_date or date > self._last_end_date:
            if only_start or only_end:
                return None
            return (None, None)

        if date < self._p0_date:
            if only_start:
                return self._first_start_date
            if only_end:
                return self._p0_date
            return (self._first_start_date, self._p0_date)

        dim = len(self.cycles)
        yN = date.year
        pN = dim
        for i, (vm, vd) in enumerate(self.cycles):
            if self._end_of_feb_check and i == self._p_feb_29 and not _is_leap(yN):
                # Feb 29 is invalid, either use Feb 28 or move to next cycle
                vd = 28
                if self._end_of_feb_check_has_28:
                    continue  # 28 was previous cycle move to next cycle
            if date < dt.datetime(yN, vm, vd):
                pN = i
                break

        interval_end = self._to_datetime(pN, yN)

        if interval_end > self._last_end_date:
            interval_end = self._last_end_date

        if only_end:
            return interval_end

        if 0 < pN < dim:
            p0 = pN - 1
            y0 = yN
        else:
            p0 = dim - 1
            y0 = yN if pN == dim else yN - 1

        if only_start:
            return self._to_datetime(p0, y0)
        return (self._to_datetime(p0, y0, False), interval_end)

    def tolist(
        self,
        start_override: Union[None, dt.datetime, dt.date, int] = None,
        end_override: Union[None, dt.datetime, dt.date, int] = None,
        from_current_position: bool = False,
        only_start: bool = False,
        only_end: bool = False,
        step: int = 1,
    ) -> list[Union[dt.datetime, tuple[dt.datetime, dt.datetime]]]:
        """
        Convert the intervals to a list of datetime tuples.

        The list can use the current interval as the start or use all the intervals.
        The list can optionally specify a different starting and/or ending date.
        If last_interval_end is None, then end_override must be specified,
        so there is an end to the list.

        Note, both the end date and end_override dates are inclusive.

        Args:
            start_override (Union[None, dt.datetime, dt.date, int], optional): Override for the start date of the list.
                                                                               If int, then the interval at index is the
                                                                               start of the list. Defaults to None.
            end_override (Union[None, dt.datetime, dt.date, int], optional): Override for the end date of the list.
                                                                             If int, then the (index-1) interval is the
                                                                             end of the list. Defaults to None.
            from_current_position (bool, optional): Flag to start list from current interval. Defaults to False.
            only_start (bool, optional): Flag to return only the start date.
                                         Defaults to False.
            only_end (bool, optional): Flag to return only the end date.
                                       Defaults to False.
            step (int, optional): specifies the increment (or decrement) of included intervals.


        Returns:
            list[tuple[dt.datetime, dt.datetime]]: The DateIntervalCycler object as a list.
        """
        if step == 0:
            return []

        if not self._has_last_end_date and end_override is None:
            raise ValueError(
                "\nDateIntervalCycler.tolist must specify an ending date\n"
                "either when initializing the DateIntervalCycler object with `end=` or\n"
                "or by passing `end_override` into this function."
            )

        if only_start and only_end:
            only_start = False
            only_end = False

        cid = self.copy()  # No reset, but do a shallow copy

        if start_override is not None:
            if isinstance(start_override, int):
                cid.set_first_interval_start(self[start_override][0])
            else:
                cid.set_first_interval_start(start_override)

        elif not from_current_position:
            cid.reset()

        if end_override is not None:
            if isinstance(end_override, int):
                end_override = self[end_override][0]
            elif type(end_override) is not dt.datetime:
                try:
                    end_override = dt.datetime(end_override.year, end_override.month, end_override.day)
                except AttributeError:
                    raise ValueError(
                        "\nDateIntervalCycler.set_last_interval_end: Invalid last_interval_end.\n"
                        f"Received: {end_override}"
                    )
            cid._last_end_date = end_override
            cid._has_last_end_date = True
            cid._len = -999  # no need to recalculate for dummy variable
            if end_override <= cid._p0_date:
                cid._at_last_interval = 1
            if end_override <= cid._first_start_date:
                return []

        return cid._tolist_intervals(only_start, only_end, step)

    def _tolist_intervals(self, only_start: bool, only_end: bool, step: int):
        # Only call from tolist method via its cid object
        if step == 1:
            if only_start:
                return [it for it in self.iter(only_start=True)]
            if only_end:
                return [it for it in self.iter(only_end=True)]
            return [it for it in self]

        if step < 0:
            if only_start:
                return [it for it in self.iter(only_start=True)][::step]
            if only_end:
                return [it for it in self.iter(only_end=True)][::step]
            return [it for it in self][::step]

        if only_start:
            lst = [self.interval_start]
        elif only_end:
            lst = [self.interval_end]
        else:
            lst = [self.interval]

        it = 0
        if only_start:
            while not self.next():
                it += 1
                if it == step:
                    it = 0
                    lst.append(self.interval_start)
        elif only_end:
            while not self.next():
                it += 1
                if it == step:
                    it = 0
                    lst.append(self.interval_end)
        else:
            while not self.next():
                it += 1
                if it == step:
                    it = 0
                    lst.append(self.interval)
        return lst

    def totuple(
        self,
        start_override: Union[None, dt.datetime, dt.date, int] = None,
        end_override: Union[None, dt.datetime, dt.date, int] = None,
        from_current_position: bool = False,
    ) -> tuple[dt.datetime, ...]:
        """
        Return a tuple containing the first_interval_start, and then all
        the remaining interval_end dates (including last_interval_end).

        The tuple can use the current interval as the start or use all the intervals.
        The tuple can optionally specify a different starting and/or ending date.
        If last_interval_end is None, then end_override must be specified,
        so there is an end to the tuple.

        Note, both the end date and end_override dates are inclusive.

        Note2, self.totuple() == tuple(self.tolist(only_start=True)) + (self.last_interval_end,)
               len(self.totuple()) == len(self.tolist()) + 1

        Args:
            start_override (Union[None, dt.datetime, dt.date, int], optional): Override for the start date of the list.
                                                                               If int, then the interval at index is the
                                                                               start of the list. Defaults to None.
            end_override (Union[None, dt.datetime, dt.date, int], optional): Override for the end date of the list.
                                                                             If int, then the (index-1) interval is the
                                                                             end of the list. Defaults to None.
            from_current_position (bool, optional): Flag to start list from current interval. Defaults to False.


        Returns:
            tuple[dt.datetime, ...]: The DateIntervalCycler date series as a tuple.
        """

        if not self._has_last_end_date and end_override is None:
            raise ValueError(
                "\nDateIntervalCycler.totuple must specify an ending date\n"
                "either when initializing the DateIntervalCycler object with `end=` or\n"
                "or by passing `end_override` into this function."
            )

        cid = self.copy()  # No reset, but do a shallow copy

        if start_override is not None:
            if isinstance(start_override, int):
                cid.set_first_interval_start(self[start_override][0])
            else:
                cid.set_first_interval_start(start_override)

        elif not from_current_position:
            cid.reset()

        if end_override is not None:
            if isinstance(end_override, int):
                end_override = self[end_override][0]
            elif type(end_override) is not dt.datetime:
                try:
                    end_override = dt.datetime(end_override.year, end_override.month, end_override.day)
                except AttributeError:
                    raise ValueError(
                        "\nDateIntervalCycler.set_last_interval_end: Invalid last_interval_end.\n"
                        f"Received: {end_override}"
                    )
            cid._last_end_date = end_override
            cid._has_last_end_date = True
            cid._len = -999  # no need to recalculate for dummy variable
            if end_override <= cid._p0_date:
                cid._at_last_interval = 1
            if end_override <= cid._first_start_date:
                return ()

        return tuple(it for it in cid.iter(only_start=True)) + (cid._last_end_date,)

    def _to_datetime(self, p, y: Optional[int] = None, feb29_move_next_fix=True) -> dt.datetime:
        """
        Internal method that converts a cycle index to a datetime object using current interval's
        year or specified year.

        Args:
            p (int): The cycle index.
            y (Optional[int], optional): The year. Defaults to None.
            feb29_move_next_fix(bool, optional): Specify cycle shift direction if non-leap year and
                                                 cycles[p] is (2,29). If True, then move to next cycle,
                                                 otherwise move to previous cycle. Defaults to True.

        Returns:
            dt.datetime: The corresponding datetime object.
        """
        if p > self._dim:
            raise RuntimeError(
                "\nCode error, bad index passed to DateIntervalCycler._to_datetime(p)\n"
                f"p > len(cycles), which is {p} > {self._dim}\n"
            )
        if y is None:
            y = self._y

        if p != self._p_feb_29 or _is_leap(y):  # No need to worry about invalid Feb29
            if p < self._dim:
                return dt.datetime(y, *self.cycles[p])
            return self._to_datetime(0, y + 1, feb29_move_next_fix)  # evaluate again with p=0 for next year

        if not self._end_of_feb_check_has_28:
            # Year is not a leap, but cycle=(2, 29), return (2, 28) if it is not in cycles
            return dt.datetime(y, 2, 28)

        if feb29_move_next_fix:
            return self._to_datetime(p + 1, y, feb29_move_next_fix)  # has 28 and no 29, so move to next
        return self._to_datetime(p - 1, y, feb29_move_next_fix)  # has 28 and no 29, so move to previous

        # if p < self._dim:
        #     m, d = self.cycles[p]
        # else:
        #     m, d = self.cycles[0]
        #     y += 1
        # if m != 2 or _is_leap(y) or (m == 2 and d < 29):
        #     return dt.datetime(y, m, d)

        # if self._end_of_feb_check_has_28:
        #     return self._to_datetime(p + 1)  # has 28 so move forward cause 29 does not exist
        # return dt.datetime(y, m, 28)

    def _start_less_end_check(self):
        if self._last_end_date is not None and self._last_end_date < self._first_start_date:
            raise ValueError("\nDateIntervalCycler requires that the start date be strictly less than the end date.")

    def _p_next(self):
        """Internal function to move cycle index forward."""
        self._p += 1
        if self._p == self._dim:
            self._p = 0
            self._y += 1

    def _p_back(self):
        """Internal function to move cycle index backward."""
        self._p -= 1
        if self._p == -1:
            self._p = self._dim - 1
            self._y -= 1

    def _get_end_of_feb_check_date(self, p) -> dt.datetime:
        """
        Internal method that helps return the correct date when cycles contains (2, 29).
        If a non-leap year then there are two fixes to the date.
          A) if (2, 28) is not in cycles, then return it as the date
          B) if (2, 28) is     in cycles, then return the next cycle as the date

        Args:
            p (int): The cycle index.

        Returns:
            dt.datetime: The corresponding datetime object.
        """
        if p < 0 or p > self._dim:
            raise RuntimeError(
                "\nCode error, bad index passed to DateIntervalCycler._get_end_of_feb_check_date(p)\n"
                f"Index must be between 0 and {self._dim}, but received {p}\n"
            )
        y = self._y
        if p == self._dim:
            y += 1
            p = 0

        m, d = self.cycles[p]

        if self._end_of_feb_check and p == self._p_feb_29 and not _is_leap(y):
            # Feb 29 is invalid, either use Feb 28 or move to next cycle
            d = 28
            if self._end_of_feb_check_has_28:
                return self._get_end_of_feb_check_date(p + 1)  # 28 was previous cycle move to next cycle
        return dt.datetime(y, m, d)

    def _index_to_interval_return(
        self, p, y, only_start, only_end
    ) -> Union[dt.datetime, tuple[dt.datetime, dt.datetime]]:
        """
        Internal method that simplifies the return from the index_to_interval method
        if it is NOT the first interval.

        Args:
            p (int): The cycle index.
            y (int): The year.
            only_start (bool): Flag to return only the start date.
            only_end (bool): Flag to return only the end date.

        Returns:
            Union[dt.datetime, tuple[dt.datetime, dt.datetime]]: The start and end dates of the interval.
        """
        if only_start:
            return self._to_datetime(p, y)
        if only_end:
            return self._to_datetime(p + 1, y)
        return self._to_datetime(p, y), self._to_datetime(p + 1, y)

    def _index_to_interval_end_of_feb_check(
        self, index, only_start, only_end
    ) -> Union[dt.datetime, tuple[dt.datetime, dt.datetime]]:
        """
        Internal method to convert index to interval when cycles contains (2, 28) and (2, 29).

        Args:
            index (int): The index of the interval.
            only_start (bool): Flag to return only the start date.
            only_end (bool): Flag to return only the end date.

        Returns:
            Union[dt.datetime, tuple[dt.datetime, dt.datetime]]: The start and end dates of the interval.
        """
        y = self._first_start_date.year
        leap_year = _is_leap(y)
        p = index + self._p0 - 1
        if leap_year or p < self._p_feb_29 or self._p_feb_29 < self._p0:
            if p < self._dim:  # within the first year and include Feb 29 interval
                return self._index_to_interval_return(p, y, only_start, only_end)
            index -= self._dim - self._p0 + 1
        elif index + self._p0 < self._dim:  # within the first year and must skip the extra feb29 interval
            return self._index_to_interval_return(index + self._p0, y, only_start, only_end)
        else:
            index -= self._dim - self._p0
        y += 1
        dim = self._dim if _is_leap(y) else self._dim - 1
        while index >= dim:
            index -= dim
            y += 1
            dim = self._dim if _is_leap(y) else self._dim - 1

        if _is_leap(y) or index < self._p_feb_29:
            return self._index_to_interval_return(index, y, only_start, only_end)
        else:  # must skip the feb29 interval
            return self._index_to_interval_return(index + 1, y, only_start, only_end)

    def _index_from_date_end_of_feb_check(self, date: Union[dt.datetime, dt.date]) -> int:
        """
        Internal method to find index from date when cycles contains (2, 28) and (2, 29).

        Args:
            date (Union[dt.datetime, dt.date]): The date to find the index for.

        Returns:
            int: The index of the interval that contains the date.
        """
        end_date_add = 0
        if self._has_last_end_date and date == self._last_end_date:
            date += dt.timedelta(days=-1)  # ensures it will capture the last interval
            end_date_add = 1  # add one more because this date is technically beyond the series

        sy = self._first_start_date.year
        vy, vm, vd = date.year, date.month, date.day
        leap_year = _is_leap(sy)

        if sy == vy:
            ind = 0
            if leap_year or self._p_feb_29 < self._p0:
                for i in range(self._p0, self._dim):
                    m, d = self.cycles[i]
                    if vm < m or (vm == m and vd < d):
                        break
                    ind += 1
            else:
                for i in range(self._p0, self._dim):
                    if i == self._p_feb_29:
                        continue
                    m, d = self.cycles[i]
                    if vm < m or (vm == m and vd < d):
                        break
                    ind += 1
            return ind + end_date_add  # date within first year

        if leap_year or self._p_feb_29 < self._p0:
            ind = self._dim - self._p0
        else:
            ind = self._dim - self._p0 - 1

        for y in range(sy + 1, vy):
            ind += self._dim if _is_leap(y) else self._dim - 1
            # if _is_leap(y):
            #     ind += self._dim
            # else:
            #     ind += self._dim - 1

        if _is_leap(vy):
            for m, d in self.cycles:
                if vm < m or (vm == m and vd < d):
                    break
                ind += 1
        else:
            for i in range(self._dim):
                if i == self._p_feb_29:
                    continue
                m, d = self.cycles[i]
                if vm < m or (vm == m and vd < d):
                    break
                ind += 1
        return ind + end_date_add

    def __getitem__(self, ind) -> Union[int, tuple[dt.datetime, dt.datetime]]:
        """
        Based on the index (ind) type either return the interval index or interval date start and end.
        If ind is int, then it is the interval index and the corresponding date interval is returned.
        If ind is dt.datetime, then it is a date and the corresponding the interval index that
        contains the date is returned.

        Args:
            ind (Union[int, dt.datetime, None]): The index that is of interest.

        Returns:
            Union[int, tuple[dt.datetime, dt.datetime]]: The corresponding interval date or index.
        """
        if ind is None:
            return self.copy()
        if isinstance(ind, int):
            return self.index_to_interval(ind)
        if isinstance(ind, slice):
            st, sp, stp = ind.start, ind.stop, ind.step
            if st is None:
                st = 0
            if sp is None:
                sp = self._len
            if stp is not None:
                raise IndexError(
                    "\nDateIntervalCycler: index does not support a step/stride.\n"
                    'Requested slice index: "' + str(ind) + '"    ->(start, stop, step)\n'
                )
            if not isinstance(st, int) or not isinstance(sp, int):
                raise IndexError(
                    "\nDateIntervalCycler: index slices may only be integers.\n"
                    'Requested slice index: "' + str(ind) + '"    ->(start, stop, step)\n'
                )
            if not self._has_last_end_date:
                if st < 0 or sp < 0 or sp >= self._len:
                    raise IndexError(
                        "\nDateIntervalCycler: index out of range.\n"
                        "If last_interval_end is None, then\n"
                        "the end index must be specified and negative indices are not allowed.\n"
                        'Requested slice index: "' + str(ind) + '"    ->(start, stop, step)\n'
                    )
            if st < 0:
                st += self._len
            if sp < 0:
                sp += self._len
            if sp <= st:
                return []

            start = self.index_to_interval(st, only_start=True)

            if st == self._len:
                end = self._last_end_date
            else:
                end = self.index_to_interval(sp, only_start=True)

            return self.tolist(start, end, False)

        if isinstance(ind, tuple) or isinstance(ind, list):
            dates = []
            for i in ind:
                dates.append(self.index_to_interval(i))

        if isinstance(ind, dt.datetime) or isinstance(ind, dt.date):
            return self.index_from_date(ind)

        raise IndexError(f"\nDateIntervalCycler: unsupported index:\n{ind}\n")

    def __copy__(self) -> "DateIntervalCycler":
        return self.copy()

    def __deepcopy__(self, unused=None) -> "DateIntervalCycler":
        return self.copy()

    def __str__(self) -> str:
        """
        Return a string representation of the current interval.

        Returns:
            str: The string representation of the current interval.
        """
        return f"({self.interval_start.strftime('%Y-%m-%d')}, {self.interval_end.strftime('%Y-%m-%d')})"

    def __repr__(self) -> str:
        """
        Return a detailed string representation of the DateIntervalCycler.

        Returns:
            str: The detailed string representation of the DateIntervalCycler.
        """
        if self._dim < 7:
            cy = f"[{str(self.cycles)[1:-1]}]"
        else:
            cy = f"[{self.cycles[0]}, {self.cycles[1]}, ..., {self.cycles[-2]}, {self.cycles[-1]}]"

        s = f"DateIntervalCycler(cycles={cy}, start={self._first_start_date.strftime('%Y-%m-%d')}, "
        if self._has_last_end_date:
            s += f"end={self._last_end_date.strftime('%Y-%m-%d')})"
        else:
            s += "end=None)"

        return s

    def __len__(self) -> int:
        return self._len

    def __iter__(self) -> Iterator[tuple[dt.datetime, dt.datetime]]:
        """
        Returns an iterator that moves through all the intervals from the start.

        Returns:
            Iterator[tuple[dt.datetime, dt.datetime]]: The iterator object.
        """
        return self.iter()

    def __next__(self) -> tuple[dt.datetime, dt.datetime]:
        """
        Advance to the next interval and return its start and end dates.

        Returns:
            tuple[dt.datetime, dt.datetime]: The start and end dates of the next interval.

        Raises:
            RuntimeError: If the iterator is not properly initialized.
            StopIteration: If there are no more intervals to iterate over.
        """
        if self._started_before_first_interval:
            self.next(True)
            return self.interval
        else:
            raise RuntimeError(
                "\nnext(DateIntervalCycler) is only allowed initialized"
                "and/or DateIntervalCycler.reset with start_before_first_interval=True"
            )
        # rng = self.interval
        # if self.next() < 2:  # 0 or 1, indicates interval is still valid
        #     return rng
        raise StopIteration


if __name__ == "__main__":
    print(f"Version: {__version__}")
    print(f"Author: {__author__}")
    print(f"Email: {__email__}")
    print(f"License: {__license__}")
    print(f"Status: {__status__}")
    print(f"Maintainer: {__maintainer__}")
    print(f"Credits: {__credits__}")
    print(f"URL: {__url__}")
    print(f"Description: {__description__}")
    print(f"Copyright: {__copyright__}")

    print("\nExample 1\n")

    # from DateIntervalCycler import DateIntervalCycler
    from datetime import datetime

    # Initialize the cycler with a start date, end date
    start_date = datetime(2000, 1, 15)
    end_date = datetime(2002, 2, 10)

    cid_monthly = DateIntervalCycler.with_monthly(start_date, end_date)  # Cycles first of each month between two dates
    cid_monthly_end = DateIntervalCycler.with_monthly_end(
        start_date, end_date
    )  # Cycles last day of each month between two dates
    cid_daily = DateIntervalCycler.with_daily(start_date, end_date)  # Cycles every day between two dates

    # Iterate through the intervals
    print("Index,       Start,  End")
    for interval_start, interval_end in cid_monthly:
        if 4 < cid_monthly.index < cid_monthly.size - 4:
            continue
        print(f"{cid_monthly.index:>5},  {interval_start.strftime('%Y-%m-%d')},  {interval_end.strftime('%Y-%m-%d')}")

    print("\nIndex,       Start,  End")
    for interval_start, interval_end in cid_monthly_end:
        if 4 < cid_monthly_end.index < cid_monthly_end.size - 4:
            continue
        print(
            f"{cid_monthly_end.index:>5},  {interval_start.strftime('%Y-%m-%d')},  {interval_end.strftime('%Y-%m-%d')}"
        )

    print("\nIndex,       Start,  End")
    for interval_start, interval_end in cid_daily:
        if 4 < cid_daily.index < cid_daily.size - 4:
            continue
        print(f"{cid_daily.index:>5},  {interval_start.strftime('%Y-%m-%d')},  {interval_end.strftime('%Y-%m-%d')}")

    print("\nExample 2\n")

    # Initialize the cycler with a start date, end date, and interval pattern
    start_date = datetime(2000, 1, 1)
    end_date = datetime(2005, 6, 1)

    cycles = [
        (1, 1),  # (month, day)
        (4, 1),
        (7, 1),
        (10, 1),
    ]

    cid = DateIntervalCycler(cycles, start_date, end_date)

    # Iterate through the intervals
    print("Index,       Start,  End")
    for interval_start, interval_end in cid:
        print(f"{cid.index:>5},  {interval_start.strftime('%Y-%m-%d')},  {interval_end.strftime('%Y-%m-%d')}")

    cid.reset()  # reset to start of series

    print("\nIndex,       Start,  End")
    for i in range(4):
        interval_start, interval_end = cid.interval  # get current interval
        cid.next()  # move to next interval
        print(f"{cid.index:>5},  {interval_start.strftime('%Y-%m-%d')},  {interval_end.strftime('%Y-%m-%d')}")

    cid.reset(start_before_first_interval=True)  # first call to next() sets first interval as current
    # rather than second interval

    print("\nIndex,       Start,  End")
    for i in range(4):
        interval_start, interval_end = cid.next_get()  # equivalent to: cid.next(); cid.interval
        print(f"{cid.index:>5},  {interval_start.strftime('%Y-%m-%d')},  {interval_end.strftime('%Y-%m-%d')}")

    # Example of index and date lookup
    lookup_date = datetime(2003, 4, 15)
    lookup_index = 20

    index = cid.index_from_date(lookup_date)  # find index of interval that contains the date
    interval_start0, interval_end0 = cid.index_to_interval(lookup_index)  # find interval for given index
    interval_start1, interval_end1 = cid.interval_from_date(lookup_date)  # find interval for given date

    interval_start2, interval_end2 = cid.index_to_interval(
        cid.index_from_date(lookup_date)
    )  # find interval for given index

    interval0 = f"{interval_start0.strftime('%Y-%m-%d')},  {interval_end0.strftime('%Y-%m-%d')}"
    interval1 = f"{interval_start1.strftime('%Y-%m-%d')},  {interval_end1.strftime('%Y-%m-%d')}"
    interval2 = f"{interval_start2.strftime('%Y-%m-%d')},  {interval_end2.strftime('%Y-%m-%d')}"

    print("\nindex_to_ and  index_from_ results")
    print(index)  # from cid.index_from_date(lookup_date)
    print(interval0)  # from cid.index_to_interval(lookup_index)
    print(interval1)  # from cid.interval_from_date(lookup_date); faster than index_to_interval(index_from_date(date))
    print(interval2)  # from index_to_interval(index_from_date(date))

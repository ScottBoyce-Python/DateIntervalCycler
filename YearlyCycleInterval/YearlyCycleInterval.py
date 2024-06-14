"""
Developed by Scott E. Boyce
Boyce@engineer.com

YearlyIntervalCycler(
        cycles: Sequence[tuple[int, int]],
        first_interval_start: Union[dt.datetime, dt.date],
        last_interval_end: Union[None, dt.datetime, dt.date] = None,
        start_before_first_interval: bool = False
        )

"""

from typing import Sequence, Union, Optional
import datetime as dt
import numpy as np

# int32 maxval is 2,147,483,647
FEB28_CHECK = np.array([2, 28], dtype=int)
FEB29_CHECK = np.array([2, 29], dtype=int)
NUL = dt.datetime(1, 1, 1)

__all__ = [
    "YearlyIntervalCycler",
]

# Days in each month of a leap year, used for validation.
_month_days_29 = np.array((0, 31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31), dtype=int)
_month_days_28 = np.array((0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31), dtype=int)

_month_days_29.setflags(write=False)
_month_days_28.setflags(write=False)


def _is_leap(year):
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)


def _intervals_to_ndarray(cycles):
    """Method safely builds a np.ndarray from cycle intervals from a list of tuples.
    It uses set to drops duplicates, then sorts to make a list of tuples
    that is converted to np.ndarray object.

    This method rebuilds the list of tuples because np.sort was failing occasionally,
    this ensures it works for all object types that intervals could be."""
    return np.array(sorted(set([(r[0], r[1]) for r in cycles])), dtype=int)


class YearlyIntervalCycler:
    MONTH_DAYS_LEAP = _month_days_29
    MONTH_DAYS_NOLEAP = _month_days_28

    MAX_INTERVAL: int = 2000000000

    cycles: np.array

    # day_diff: int  # Difference in days between the start and end dates

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
        if _internal_copy_init:
            if _internal_copy_init < 0:  # Negative is Shallow Copy
                self.cycles = cycles
            else:
                self.cycles = cycles.copy()
            self._lock_cycles()

            self._first_start_date = first_interval_start
            self._last_end_date = last_interval_end
            self._dim = self.cycles.shape[0]
            self._started_before_first_interval = start_before_first_interval

            self._has_last_end_date = False
            self._end_of_feb_check = False
            self._end_of_feb_check_has_28 = False
            self._p_feb_29 = YearlyIntervalCycler.MAX_INTERVAL
            self._y = 0
            self._p = 0
            self._p0 = 0
            self._p0_date = NUL
            self._ind = 0
            self._len = 0
            self._at_first_interval = 0
            self._at_last_interval = 0
            return

        # Extract rows, drop duplicates, sort rows, then store as numpy ndarray
        self.cycles = _intervals_to_ndarray(cycles)
        self._lock_cycles()

        self._dim = self.cycles.shape[0]
        self._end_of_feb_check = False
        self._end_of_feb_check_has_28 = False
        self._p_feb_29 = YearlyIntervalCycler.MAX_INTERVAL
        self._p0_date = NUL

        self._has_last_end_date = False
        self._at_first_interval = 0
        self._at_last_interval = 0

        if self._dim < 1:
            raise ValueError("\nYearlyIntervalCycler: len(cycles) must be greater than zero.")

        # Validate the date intervals and check for leap year considerations
        for i, (vm, vd) in enumerate(cycles):
            if vd < 1 or vm < 1 or vm > 12 or _month_days_29[vm] < vd:
                raise ValueError(f"YearlyIntervalCycler: Invalid (month, day) entry at cycles[{i}] = ({vm}, {vd})")

        p_feb29 = np.where(np.all(self.cycles == FEB29_CHECK, axis=1))[0]
        self._end_of_feb_check = p_feb29.size == 1
        if self._end_of_feb_check:
            self._p_feb_29 = p_feb29[0]
        # self._end_of_feb_check = np.any(np.all(self.cycles == FEB29_CHECK, axis=1))

        self._end_of_feb_check_has_28 = self._end_of_feb_check and np.any(np.all(self.cycles == FEB28_CHECK, axis=1))

        self.set_start_range_date(first_interval_start, start_before_first_interval)
        self.set_end_range_date(last_interval_end)

    @property
    def size(self):
        return self._len

    @property
    def first_interval_start(self):
        return self._first_start_date

    @property
    def last_interval_end(self):
        return self._last_end_date

    @property
    def index(self):
        return self._ind

    @property
    def interval(self) -> tuple[dt.datetime, dt.datetime]:
        """Returns a tuple of the current cycle interval start and end dates."""
        return self.interval_start, self.interval_end

    @property
    def interval_length(self) -> float:
        """Returns the length in days of the current interval."""
        return (self.interval_end - self.interval_start).total_seconds() / 86400.0

    @property
    def interval_start(self) -> dt.datetime:
        """Returns the current cycle interval start date as a datetime object."""
        if self._at_first_interval:
            return self._first_start_date
        if self._end_of_feb_check:
            return self._get_end_of_feb_check_date(self._p)

        return self._to_datetime(self._p)

    @property
    def interval_end(self) -> dt.datetime:
        """Returns the current cycle interval end date as a datetime object."""
        if self._at_last_interval:
            return self._last_end_date
        if self._at_first_interval:
            if self._end_of_feb_check:
                return self._get_end_of_feb_check_date(self._p)
            return self._to_datetime(self._p)
        if self._end_of_feb_check:
            return self._get_end_of_feb_check_date(self._p + 1)
        return self._to_datetime(self._p + 1)

    @classmethod
    def from_year(
        cls,
        cycles: Sequence[tuple[int, int]],
        year_start: int,
        starting_cycle_index=0,
        year_end: Optional[int] = None,
        ending_cycle_index: Optional[int] = 0,
    ):
        cycles = _intervals_to_ndarray(cycles)
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
    ):
        return cls([(m, 1) for m in range(1, 13)], first_interval_start, last_interval_end)

    @classmethod
    def with_monthly_end(
        cls,
        first_interval_start: Union[dt.datetime, dt.date],
        last_interval_end: Union[None, dt.datetime, dt.date] = None,
    ):
        return cls([(m, _month_days_29[m]) for m in range(1, 13)], first_interval_start, last_interval_end)

    @classmethod
    def with_daily(
        cls,
        first_interval_start: Union[dt.datetime, dt.date],
        last_interval_end: Union[None, dt.datetime, dt.date] = None,
    ):
        return cls(
            [(m, d) for m in range(1, 13) for d in range(1, _month_days_29[m] + 1)],
            first_interval_start,
            last_interval_end,
        )

    @staticmethod
    def is_leap(year: int):
        return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)

    @staticmethod
    def month_days(month, leap: bool = False):
        if month < 1 or 12 < month:
            raise ValueError(
                f"\nYearlyIntervalCycler.month_days: month must be between 1 and 12, but received: {month}"
            )
        if leap:
            return _month_days_29[month]
        return _month_days_28[month]

    def copy(self, reset: bool = False, shallow_copy_cycles=True):
        """Returns a new instance of YearlyIntervalCycler that has the exact same state as the current."""
        copy_flag = -1 if shallow_copy_cycles else 1

        cad = YearlyIntervalCycler(
            self.cycles,
            self._first_start_date,
            self._last_end_date,
            self._started_before_first_interval,
            _internal_copy_init=copy_flag,
        )

        cad._has_last_end_date = self._has_last_end_date
        cad._end_of_feb_check = self._end_of_feb_check
        cad._end_of_feb_check_has_28 = self._end_of_feb_check_has_28
        cad._p_feb_29 = self._p_feb_29
        cad._y = self._y
        cad._p = self._p
        cad._p0 = self._p0
        cad._p0_date = self._p0_date
        cad._ind = self._ind
        cad._len = self._len
        cad._at_first_interval = self._at_first_interval
        cad._at_last_interval = self._at_last_interval

        if reset:
            cad.reset(self._started_before_first_interval)

        return cad

    def set_start_range_date(self, date: Union[dt.datetime, dt.date], start_before_first_interval: bool = False):
        if type(date) is not dt.datetime:
            date = dt.datetime(date.year, date.month, date.day)
        self._first_start_date = date
        self._at_first_interval = 1

        self.reset(start_before_first_interval, set_p0=True)  # must reset p0 and p0_date

        if self._has_last_end_date and self._last_end_date <= self._p0_date:
            self._started_before_first_interval = (
                False  # No intervals, only contains (first_interval_start, last_interval_end)
            )
            self._at_last_interval = 1
            self._len = 1

    def set_end_range_date(self, date: Union[None, dt.datetime, dt.date]):
        if date is not None and type(date) is not dt.datetime:
            date = dt.datetime(date.year, date.month, date.day)

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
            self._len = YearlyIntervalCycler.MAX_INTERVAL

    def reset(self, start_before_first_interval: bool = False, return_self: bool = False, *, set_p0: bool = False):
        """Resets YearlyIntervalCycler to the first interval."""
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

    def next_get(self, allowStopIteration=False) -> int:
        self.next(allowStopIteration)
        return self.interval_start, self.interval_end

    def back_get(self, allowStopIteration=False) -> int:
        self.back(allowStopIteration)
        return self.interval_start, self.interval_end

    def next(self, allowStopIteration=False) -> int:
        """Advances to the next date interval.
        Returns 0 if successful, otherwise returns the the fail count."""
        if self._at_last_interval:
            self._at_last_interval += 1
            if allowStopIteration:
                raise StopIteration("YearlyIntervalCycler.next cannot go beyond the ending date")
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
        """Moves back to the previous date, wrapping around to the previous year if necessary."""
        if self._at_first_interval:
            if self._at_first_interval == -1:  # Flag to indicate before start of intervals, but requested back?
                self._at_first_interval = 1
            self._at_first_interval += 1
            if allowStopIteration:
                raise StopIteration("YearlyIntervalCycler.back cannot go beyond the starting date.")
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

    def iter(self, reset_to_start=False):
        if self._at_first_interval != 0 and self._at_last_interval != 0:
            return self.interval
        if reset_to_start:
            self.reset()

        if self._started_before_first_interval:
            while True:
                if self.next():  # reached end of range
                    return self.interval
                yield self.interval
        else:
            while True:
                yield self.interval
                if self.next():  # reached end of range
                    return self.interval

    def index_to_interval(
        self, index, only_start: bool = False, only_end: bool = False
    ) -> Union[dt.datetime, tuple[dt.datetime, dt.datetime]]:
        """Given an index, return the corresponding date interval."""
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
        """Returns the index of the interval that contains the date."""
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

    def tolist(
        self,
        start_override: Union[None, dt.datetime, dt.date] = None,
        end_override: Union[None, dt.datetime, dt.date] = None,
        from_current_position: bool = False,
        as_date: bool = False,
    ):
        if not self._has_last_end_date and end_override is None:
            raise ValueError(
                "\nYearlyIntervalCycler.tolist must specify an ending date\n"
                "either when initializing the YearlyIntervalCycler object with `end=` or\n"
                "or by passing `end_override` into this function."
            )
        cad = self.copy()  # No reset, but do a shallow copy

        if start_override is not None:
            cad.set_start_range_date(start_override)
        elif not from_current_position:
            cad.reset()

        if end_override is not None:
            if type(end_override) is not dt.datetime:
                end_override = dt.datetime(end_override.year, end_override.month, end_override.day)

            cad._last_end_date = end_override
            cad._has_last_end_date = True
            cad._len = -999  # no need to recalculate for dummy variable
            cad._start_less_end_check()

        if as_date:
            return [(d0.date(), d1.date()) for (d0, d1) in cad]
        return [it for it in cad]

    def _lock_cycles(self):
        # Locks the cycles array so it cannot be altered, even when shadow copied.
        self.cycles.setflags(write=False)

    def _unlock_cycles(self):
        # Dangerous, allows editing cycles array
        self.cycles.setflags(write=True)

    def _to_datetime(self, p, y: Optional[int] = None) -> dt.datetime:
        if p > self._dim:
            raise RuntimeError(
                "\nCode error, bad index passed to YearlyIntervalCycler._to_datetime(p)\n"
                f"p > len(cycles), which is {p} > {self._dim}\n"
            )
        if y is None:
            y = self._y
        if not self._end_of_feb_check:
            if p < self._dim:
                return dt.datetime(y, *self.cycles[p])
            return dt.datetime(y + 1, *self.cycles[0])

        if p < self._dim:
            m, d = self.cycles[p]
        else:
            m, d = self.cycles[0]
            y += 1
        if m != 2 or _is_leap(y) or (m == 2 and d < 29):
            return dt.datetime(y, m, d)

        if self._end_of_feb_check_has_28:
            return self._to_datetime(p + 1)  # has 28 so move forward cause 29 does not exist
        return dt.datetime(y, m, 28)

    def _start_less_end_check(self):
        if self._last_end_date is not None and self._last_end_date < self._first_start_date:
            raise ValueError("YearlyIntervalCycler requires that the start date be strictly less than the end date.")

    def _p_next(self):
        self._p += 1
        if self._p == self._dim:
            self._p = 0
            self._y += 1

    def _p_back(self):
        self._p -= 1
        if self._p == -1:
            self._p = self._dim - 1
            self._y -= 1

    def _get_end_of_feb_check_date(self, p):
        if p < 0 or p > self._dim:
            raise RuntimeError(
                "\nCode error, bad index passed to YearlyIntervalCycler._get_end_of_feb_check_date(p)\n"
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
        # Only for use within index_to_interval function.
        # Does not deal with the first interval correctly
        if only_start:
            return self._to_datetime(p, y)
        if only_end:
            return self._to_datetime(p + 1, y)
        return self._to_datetime(p, y), self._to_datetime(p + 1, y)

    def _index_to_interval_end_of_feb_check(self, index, only_start, only_end):
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
        if ind is None:
            return self.copy()
        if isinstance(ind, int):
            return self.index_to_interval(ind)
        return self.index_from_date(ind)

    def __copy__(self):
        return self.copy()

    def __deepcopy__(self, unused=None):
        return self.copy(shallow_copy_cycles=False)

    def __str__(self):
        return f"({self.interval_start.strftime('%Y-%m-%d')}, {self.interval_end.strftime('%Y-%m-%d')})"

    def __repr__(self):
        if self._dim < 7:
            cy = str(self.cycles.tolist())
        else:
            cy = f"[{self.cycles[0]}, {self.cycles[1]}, ..., {self.cycles[-2]}, {self.cycles[-1]}]"

        s = f"YearlyIntervalCycler(cycles={cy}, start={self._first_start_date.strftime('%Y-%m-%d')}, "
        if self._has_last_end_date:
            s += f"end={self._last_end_date.strftime('%Y-%m-%d')})"
        else:
            s += "end=None)"

        return s

    def __len__(self):
        return self._len

    def __iter__(self):
        return self.iter()

    def __next__(self):
        if self._started_before_first_interval:
            self.next(True)
            return self.interval
        else:
            raise RuntimeError(
                "\nnext(YearlyIntervalCycler) is only allowed initialized"
                "and/or YearlyIntervalCycler.reset with start_before_first_interval=True"
            )
        # rng = self.interval
        # if self.next() < 2:  # 0 or 1, indicates interval is still valid
        #     return rng
        raise StopIteration


if __name__ == "__main__":
    print("Starting Main Tests")

    def daily_dates(start_date, end_date=None, reverse=False):
        date = start_date
        inc = -1 if reverse else 1
        while end_date is None or date <= end_date:
            yield date
            date += dt.timedelta(days=inc)

    def d(y, m, d) -> dt.datetime:
        return dt.datetime(y, m, d)

    def st(date) -> str:
        return date.strftime("%Y-%m-%d")

    def half(d1, d2):
        if d1 > d2:
            d1, d2 = d2, d1
        return d1 + (d2 - d1) / 2

    cycles = [
        (6, 1),  # Duplicate should be dropped
    ]

    cad = YearlyIntervalCycler(cycles, dt.datetime(2000, 3, 1))
    assert cad.next_get()[0] == dt.datetime(2000, 6, 1)
    assert cad.next_get()[0] == dt.datetime(2001, 6, 1)
    assert cad.next_get()[0] == dt.datetime(2002, 6, 1)
    cad = YearlyIntervalCycler(cycles, dt.datetime(2000, 7, 1))
    assert cad.next_get()[0] == dt.datetime(2001, 6, 1)
    assert cad.next_get()[0] == dt.datetime(2002, 6, 1)
    assert cad.next_get()[0] == dt.datetime(2003, 6, 1)
    cad = YearlyIntervalCycler(cycles, dt.datetime(2000, 3, 1), dt.datetime(2019, 7, 1))
    lst = cad.tolist()
    assert lst == [
        (dt.datetime.strptime(start_date, "%Y-%m-%d"), dt.datetime.strptime(end_date, "%Y-%m-%d"))
        for start_date, end_date in [
            ("2000-3-1", "2000-6-1"),  # Note, it honors the starting date
            ("2000-6-1", "2001-6-1"),  # Follows the month and day defined by "cycles"
            ("2001-6-1", "2002-6-1"),
            ("2002-6-1", "2003-6-1"),
            ("2003-6-1", "2004-6-1"),
            ("2004-6-1", "2005-6-1"),
            ("2005-6-1", "2006-6-1"),
            ("2006-6-1", "2007-6-1"),
            ("2007-6-1", "2008-6-1"),
            ("2008-6-1", "2009-6-1"),
            ("2009-6-1", "2010-6-1"),
            ("2010-6-1", "2011-6-1"),
            ("2011-6-1", "2012-6-1"),
            ("2012-6-1", "2013-6-1"),
            ("2013-6-1", "2014-6-1"),
            ("2014-6-1", "2015-6-1"),
            ("2015-6-1", "2016-6-1"),
            ("2016-6-1", "2017-6-1"),
            ("2017-6-1", "2018-6-1"),
            ("2018-6-1", "2019-6-1"),
            ("2019-6-1", "2019-7-1"),  # Note, it honors the ending date
        ]
    ]

    cad = YearlyIntervalCycler(cycles, dt.datetime(2000, 7, 1), dt.datetime(2019, 2, 1))
    lst = cad.tolist()
    assert lst == [
        (dt.datetime.strptime(start_date, "%Y-%m-%d"), dt.datetime.strptime(end_date, "%Y-%m-%d"))
        for start_date, end_date in [
            ("2000-7-1", "2001-6-1"),  # Note, it honors the starting date
            ("2001-6-1", "2002-6-1"),  # Follows the month and day defined by "cycles"
            ("2002-6-1", "2003-6-1"),
            ("2003-6-1", "2004-6-1"),
            ("2004-6-1", "2005-6-1"),
            ("2005-6-1", "2006-6-1"),
            ("2006-6-1", "2007-6-1"),
            ("2007-6-1", "2008-6-1"),
            ("2008-6-1", "2009-6-1"),
            ("2009-6-1", "2010-6-1"),
            ("2010-6-1", "2011-6-1"),
            ("2011-6-1", "2012-6-1"),
            ("2012-6-1", "2013-6-1"),
            ("2013-6-1", "2014-6-1"),
            ("2014-6-1", "2015-6-1"),
            ("2015-6-1", "2016-6-1"),
            ("2016-6-1", "2017-6-1"),
            ("2017-6-1", "2018-6-1"),
            ("2018-6-1", "2019-2-1"),  # Note, it honors the ending date
        ]
    ]

    cad = YearlyIntervalCycler.from_year(cycles, 1960)
    assert cad.next_get()[0] == dt.datetime(1961, 6, 1)
    assert cad.next_get()[0] == dt.datetime(1962, 6, 1)
    assert cad.next_get()[0] == dt.datetime(1963, 6, 1)

    cad = YearlyIntervalCycler.with_monthly(dt.datetime(2000, 3, 1))
    assert cad.next_get()[0] == dt.datetime(2000, 4, 1)
    assert cad.next_get()[0] == dt.datetime(2000, 5, 1)
    assert cad.next_get()[0] == dt.datetime(2000, 6, 1)

    cad = YearlyIntervalCycler.with_monthly_end(dt.datetime(2000, 3, 1))
    assert cad.next_get()[0] == dt.datetime(2000, 3, 31)
    assert cad.next_get()[0] == dt.datetime(2000, 4, 30)
    assert cad.next_get()[0] == dt.datetime(2000, 5, 31)

    cad = YearlyIntervalCycler.with_daily(dt.datetime(2000, 2, 27))
    assert cad.next_get()[0] == dt.datetime(2000, 2, 28)
    assert cad.next_get()[0] == dt.datetime(2000, 2, 29)
    assert cad.next_get()[0] == dt.datetime(2000, 3, 1)
    assert cad.next_get()[0] == dt.datetime(2000, 3, 2)

    cad = YearlyIntervalCycler.with_daily(dt.datetime(2001, 2, 27))
    assert cad.next_get()[0] == dt.datetime(2001, 2, 28)
    assert cad.next_get()[0] == dt.datetime(2001, 3, 1)
    assert cad.next_get()[0] == dt.datetime(2001, 3, 2)

    cad = YearlyIntervalCycler.with_daily(dt.datetime(2000, 3, 1))
    assert cad.next_get()[0] == dt.datetime(2000, 3, 2)
    assert cad.next_get()[0] == dt.datetime(2000, 3, 3)
    assert cad.next_get()[0] == dt.datetime(2000, 3, 4)

    try:
        cad = YearlyIntervalCycler.with_daily(dt.datetime(2000, 3, 1), dt.datetime(2000, 1, 1))
    except ValueError:
        pass

    try:
        lst = YearlyIntervalCycler.with_daily(dt.datetime(2000, 1, 1)).tolist(
            start_override=dt.datetime(2000, 3, 1), end_override=dt.datetime(2000, 1, 1)
        )
    except ValueError:
        pass

    DUMMY_START = dt.datetime(2000, 1, 1)
    DUMMY_END = dt.datetime(2005, 1, 1)

    cad = YearlyIntervalCycler.with_daily(DUMMY_START, DUMMY_END)
    lst = cad.tolist()
    ind = 0
    for date0, date1 in cad:
        i0 = cad.index_from_date(date0)
        i1 = cad.index_from_date(date1)
        assert ind == i0
        assert ind + 1 == i1
        assert lst[ind] == (date0, date1)

        assert cad.index_to_interval(ind) == (date0, date1)
        assert cad.index_to_interval(ind, True) == date0
        assert cad.index_to_interval(ind, False, True) == date1
        assert cad[ind] == (date0, date1)
        ind += 1

    year_start = 1950

    cycles = [
        (1, 1),  # (month, day)
        (4, 1),
        (7, 1),
        (10, 1),
    ]

    cad = YearlyIntervalCycler.from_year(cycles, year_start)
    cad.next()
    cad.next()
    assert cad.interval_start == dt.datetime(1950, 7, 1)
    assert cad.interval_end == dt.datetime(1950, 10, 1)
    cad.back()
    assert cad.next_get() == (dt.datetime(1950, 7, 1), dt.datetime(1950, 10, 1))
    assert cad.next_get() == (dt.datetime(1950, 10, 1), dt.datetime(1951, 1, 1))
    assert cad.next_get() == (dt.datetime(1951, 1, 1), dt.datetime(1951, 4, 1))

    cad.reset()
    assert cad.interval_start == dt.datetime(1950, 1, 1)

    cad2 = cad.copy()

    cad.next()
    cad.next()
    assert cad.interval_start == dt.datetime(1950, 7, 1)
    assert cad.interval == (dt.datetime(1950, 7, 1), dt.datetime(1950, 10, 1))

    assert cad2.interval_start == dt.datetime(1950, 1, 1)  # Should remain unchanged
    del cad2

    next_time_day_diff = (dt.datetime(1951, 1, 1) - dt.datetime(1950, 10, 1)).total_seconds() / 86400.0

    cad.next()
    assert cad.interval_length == next_time_day_diff  # Advance time and return day difference

    start = dt.datetime(2000, 2, 1)
    end = dt.datetime(2005, 11, 1)

    assert cad.tolist(start, end) == [
        (dt.datetime.strptime(start_date, "%Y-%m-%d"), dt.datetime.strptime(end_date, "%Y-%m-%d"))
        for start_date, end_date in [
            ("2000-02-01", "2000-04-01"),  # Note, it honors the starting date
            ("2000-04-01", "2000-07-01"),  # Follows the month and day defined by "cycles"
            ("2000-07-01", "2000-10-01"),
            ("2000-10-01", "2001-01-01"),
            ("2001-01-01", "2001-04-01"),
            ("2001-04-01", "2001-07-01"),
            ("2001-07-01", "2001-10-01"),
            ("2001-10-01", "2002-01-01"),
            ("2002-01-01", "2002-04-01"),
            ("2002-04-01", "2002-07-01"),
            ("2002-07-01", "2002-10-01"),
            ("2002-10-01", "2003-01-01"),
            ("2003-01-01", "2003-04-01"),
            ("2003-04-01", "2003-07-01"),
            ("2003-07-01", "2003-10-01"),
            ("2003-10-01", "2004-01-01"),
            ("2004-01-01", "2004-04-01"),
            ("2004-04-01", "2004-07-01"),
            ("2004-07-01", "2004-10-01"),
            ("2004-10-01", "2005-01-01"),
            ("2005-01-01", "2005-04-01"),
            ("2005-04-01", "2005-07-01"),
            ("2005-07-01", "2005-10-01"),
            ("2005-10-01", "2005-11-01"),  # Note, it honors the ending date
        ]
    ]

    cycles = [
        (7, 1),  # Values out of order should be sorted
        (4, 5),
        (4, 3),
        (4, 1),
        (1, 1),
        (4, 3),  # Duplicate should be dropped
        (10, 1),
    ]

    cad = YearlyIntervalCycler.from_year(cycles, 2000)

    assert (cad.cycles == np.array([(1, 1), (4, 1), (4, 3), (4, 5), (7, 1), (10, 1)], dtype=int)).all()

    cad = YearlyIntervalCycler.with_monthly(DUMMY_START)
    assert (
        cad.cycles
        == np.array(
            [(1, 1), (2, 1), (3, 1), (4, 1), (5, 1), (6, 1), (7, 1), (8, 1), (9, 1), (10, 1), (11, 1), (12, 1)],
            dtype=int,
        )
    ).all()

    cad = YearlyIntervalCycler.with_monthly_end(DUMMY_START)
    assert (
        cad.cycles
        == np.array(
            [
                (1, 31),
                (2, 29),
                (3, 31),
                (4, 30),
                (5, 31),
                (6, 30),
                (7, 31),
                (8, 31),
                (9, 30),
                (10, 31),
                (11, 30),
                (12, 31),
            ],
            dtype=int,
        )
    ).all()

    cad = YearlyIntervalCycler.with_daily(DUMMY_START)

    assert cad.interval_start == DUMMY_START

    for i in range(56):  # Move to Feb 26 as start date
        cad.next()

    assert cad.next_get() == (dt.datetime(2000, 2, 27), dt.datetime(2000, 2, 28))
    assert cad.next_get() == (dt.datetime(2000, 2, 28), dt.datetime(2000, 2, 29))
    assert cad.next_get() == (dt.datetime(2000, 2, 29), dt.datetime(2000, 3, 1))

    cad.reset()
    assert cad.interval_start == DUMMY_START

    dd = daily_dates(DUMMY_START)
    for i in range(12000):  # Check about 30 years of daily
        if cad.interval_start != next(dd):
            date = next(dd) - dt.timedelta(days=1)
            raise RuntimeError(
                "\nDaily date dose not match expected datetime for the "
                f"{i} iteration,\nwhich returned a date of {cad.interval_start}\nbut expected {date}"
            )
        cad.next()

    if cad.interval_start != next(dd):
        date = next(dd) - dt.timedelta(days=1)
        raise RuntimeError(
            "\nDaily date dose not match expected datetime for the "
            f"{i+1} iteration,\nwhich returned a date of {cad.interval_start}\nbut expected {date}"
        )

    dd = daily_dates(cad.interval_start, reverse=True)
    for i in range(12000):  # Check about 30 years of daily
        if cad.interval_start != next(dd):
            date = next(dd) + dt.timedelta(days=1)
            raise RuntimeError(
                "\nDaily date in reverse dose not match expected datetime for the "
                f"{i} iteration,\nwhich returned a date of {cad.interval_start}\nbut expected {date}"
            )
        cad.back()

    if cad.interval_start != next(dd):
        date = next(dd) - dt.timedelta(days=1)
        raise RuntimeError(
            "\nDaily date in reverse dose not match expected datetime for the "
            f"{i+1} iteration,\nwhich returned a date of {cad.interval_start}\nbut expected {date}"
        )

    assert cad.interval_start == DUMMY_START  # Should be back to the start

    cycles = [
        (1, 1),
        (4, 1),
        (7, 1),
        (10, 1),
    ]

    start = dt.datetime(1950, 3, 1)
    end = dt.datetime(1970, 11, 1)

    cad = YearlyIntervalCycler(cycles, start, end)

    assert cad.interval_start == dt.datetime(1950, 3, 1)
    assert cad.interval_end == dt.datetime(1950, 4, 1)
    cad.next()
    assert cad.interval_start == dt.datetime(1950, 4, 1)
    assert cad.interval_end == dt.datetime(1950, 7, 1)
    cad.next()
    assert cad.interval_start == dt.datetime(1950, 7, 1)
    assert cad.interval_end == dt.datetime(1950, 10, 1)
    cad.back()
    assert cad.interval_start == dt.datetime(1950, 4, 1)
    assert cad.interval_end == dt.datetime(1950, 7, 1)
    cad.back()
    assert cad.interval_start == dt.datetime(1950, 3, 1)
    assert cad.interval_end == dt.datetime(1950, 4, 1)

    start = dt.datetime(1952, 2, 1)
    end = dt.datetime(2020, 11, 1)
    cad = YearlyIntervalCycler.with_daily(start, end)

    assert cad.interval_start == start
    assert cad.interval_end == dt.datetime(1952, 2, 2)

    for i in range(25):  # Move to Feb 26 as start date
        cad.next()

    assert cad.next_get() == (dt.datetime(1952, 2, 27), dt.datetime(1952, 2, 28))
    assert cad.next_get() == (dt.datetime(1952, 2, 28), dt.datetime(1952, 2, 29))
    assert cad.next_get() == (dt.datetime(1952, 2, 29), dt.datetime(1952, 3, 1))

    cad.reset()
    assert cad.interval_start == start

    dd = daily_dates(start)
    for i in range(12000):  # Check about 30 years of daily
        if cad.interval_start != next(dd):
            date = next(dd) - dt.timedelta(days=1)
            raise RuntimeError(
                "\nDaily date dose not match expected datetime for the "
                f"{i} iteration,\nwhich returned a date of {cad.interval_start}\nbut expected {date}"
            )
        cad.next()

    if cad.interval_start != next(dd):
        date = next(dd) - dt.timedelta(days=1)
        raise RuntimeError(
            "\nDaily date dose not match expected datetime for the "
            f"{i+1} iteration,\nwhich returned a date of {cad.interval_start}\nbut expected {date}"
        )

    dd = daily_dates(cad.interval_start, reverse=True)
    for i in range(12000):  # Check about 30 years of daily
        if cad.interval_start != next(dd):
            date = next(dd) + dt.timedelta(days=1)
            raise RuntimeError(
                "\nDaily date in reverse dose not match expected datetime for the "
                f"{i} iteration,\nwhich returned a date of {cad.interval_start}\nbut expected {date}"
            )
        cad.back()

    if cad.interval_start != next(dd):
        date = next(dd) - dt.timedelta(days=1)
        raise RuntimeError(
            "\nDaily date in reverse dose not match expected datetime for the "
            f"{i+1} iteration,\nwhich returned a date of {cad.interval_start}\nbut expected {date}"
        )

    assert cad.interval_start == start  # Should be back to the start

    start = dt.datetime(2000, 2, 1)
    end = dt.datetime(2020, 11, 1)
    cad = YearlyIntervalCycler.with_daily(start, end)

    dd = daily_dates(start)
    for i in range(12000):  # Check about 30 years of daily
        if cad.interval_start != next(dd):
            date = next(dd) - dt.timedelta(days=1)
            raise RuntimeError(
                "\nDaily date dose not match expected datetime for the "
                f"{i} iteration,\nwhich returned a date of {cad.interval_start}\nbut expected {date}"
            )
        if cad.next() > 0:
            break

    assert cad.interval_start == end - dt.timedelta(days=1)
    assert cad.interval_end == end

    cad.back()
    assert cad.interval_start == end - dt.timedelta(days=2)
    assert cad.interval_end == end - dt.timedelta(days=1)
    cad.back()
    assert cad.interval_start == end - dt.timedelta(days=3)
    assert cad.interval_end == end - dt.timedelta(days=2)

    cad.reset()
    dd = daily_dates(start)
    for interval in cad:  # Check about 30 years of daily
        if interval[0] != next(dd):
            date = next(dd) - dt.timedelta(days=1)
            raise RuntimeError(
                "\nDaily date dose not match expected datetime for the "
                f"{i} iteration,\nwhich returned a date of {cad.interval_start}\nbut expected {date}"
            )

    assert cad.interval_start == end - dt.timedelta(days=1)
    assert cad.interval_end == end

    cad.back()
    assert cad.interval_start == end - dt.timedelta(days=2)
    assert cad.interval_end == end - dt.timedelta(days=1)
    cad.back()
    assert cad.interval_start == end - dt.timedelta(days=3)
    assert cad.interval_end == end - dt.timedelta(days=2)

    cad.reset()
    dd = daily_dates(start)
    for interval in cad.iter():  # Check about 30 years of daily
        if interval[0] != next(dd):
            date = next(dd) - dt.timedelta(days=1)
            raise RuntimeError(
                "\nDaily date dose not match expected datetime for the "
                f"{i} iteration,\nwhich returned a date of {cad.interval_start}\nbut expected {date}"
            )

    assert cad.interval_start == end - dt.timedelta(days=1)
    assert cad.interval_end == end

    cad.back()
    assert cad.interval_start == end - dt.timedelta(days=2)
    assert cad.interval_end == end - dt.timedelta(days=1)
    cad.back()
    assert cad.interval_start == end - dt.timedelta(days=3)
    assert cad.interval_end == end - dt.timedelta(days=2)

    # ----------------------------------------------------------------------------------------

    cycles = [
        (2, 1),  # (month, day)
        (4, 1),
        (6, 1),
        (8, 1),
        (10, 1),
    ]

    y0 = 2000  # Must be leap year
    yN = 2020  # Must be leap year

    start_list = (
        [dt.datetime(y0, m, 1) for m in range(1, 13)]
        + [dt.datetime(y0, m, 5) for m in range(1, 13)]
        + [dt.datetime(y0 - 1, m, 1) for m in range(1, 13)]
        + [dt.datetime(y0 - 1, m, 5) for m in range(1, 13)]
        + [dt.datetime(y0 + 1, m, 1) for m in range(1, 13)]
        + [dt.datetime(y0 + 1, m, 5) for m in range(1, 13)]
        + [dt.datetime(y0, m, _month_days_29[m]) for m in range(1, 13)]
        + [dt.datetime(y0 - 1, m, (0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)[m]) for m in range(1, 13)]
        + [dt.datetime(y0 + 1, m, (0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)[m]) for m in range(1, 13)]
        + [
            dt.datetime(y0, 2, 28),
            dt.datetime(y0, 2, 29),
            dt.datetime(y0, 3, 1),
            dt.datetime(y0 + 1, 2, 28),
            dt.datetime(y0 + 1, 3, 1),
        ]
    )

    end_list = (
        [dt.datetime(yN, m, 1) for m in range(1, 13)]
        + [dt.datetime(yN, m, 5) for m in range(1, 13)]
        + [dt.datetime(yN - 1, m, 1) for m in range(1, 13)]
        + [dt.datetime(yN - 1, m, 5) for m in range(1, 13)]
        + [dt.datetime(yN + 1, m, 1) for m in range(1, 13)]
        + [dt.datetime(yN + 1, m, 5) for m in range(1, 13)]
        + [dt.datetime(yN, m, _month_days_29[m]) for m in range(1, 13)]
        + [dt.datetime(yN - 1, m, (0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)[m]) for m in range(1, 13)]
        + [dt.datetime(yN + 1, m, (0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)[m]) for m in range(1, 13)]
        + [
            dt.datetime(yN, 2, 28),
            dt.datetime(yN, 2, 29),
            dt.datetime(yN, 3, 1),
            dt.datetime(yN + 1, 2, 28),
            dt.datetime(yN + 1, 3, 1),
        ]
    )

    print("\nTwo-month cycle tests")
    it = 0
    dm = len(start_list)
    for start in start_list:
        it += 1
        print(f"   2M Test {it} of {dm}")
        for end in end_list:
            cad = YearlyIntervalCycler(cycles, start, end)
            ind = 0
            e_old = start
            for s, e in cad:
                # print(f"{st(start)}, {st(end)}, {cad.index}, {st(s)}, {st(e)}, ")
                assert s == e_old
                assert cad.index == ind
                assert cad.index == cad.index_from_date(s)
                assert cad.index == cad.index_from_date(half(s, e))
                assert cad.index_to_interval(ind) == (s, e)
                assert cad.index + 1 == cad.index_from_date(e)

                assert cad.index_to_interval(cad.index) == (s, e)
                assert cad.index_to_interval(cad.index, True) == s
                assert cad.index_to_interval(cad.index, False, True) == e

                e_old = e
                ind += 1

    y0 = 2000  # Must be leap year
    yN = 2004  # Must be leap year

    start_list = (
        [dt.datetime(y0, m, 1) for m in range(1, 13)]
        + [dt.datetime(y0, m, 5) for m in range(1, 13)]
        + [dt.datetime(y0 - 1, m, 1) for m in range(1, 13)]
        + [dt.datetime(y0 - 1, m, 5) for m in range(1, 13)]
        + [dt.datetime(y0 + 1, m, 1) for m in range(1, 13)]
        + [dt.datetime(y0 + 1, m, 5) for m in range(1, 13)]
        + [dt.datetime(y0, m, _month_days_29[m]) for m in range(1, 13)]
        + [dt.datetime(y0 - 1, m, (0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)[m]) for m in range(1, 13)]
        + [dt.datetime(y0 + 1, m, (0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)[m]) for m in range(1, 13)]
        + [
            dt.datetime(y0, 2, 28),
            dt.datetime(y0, 2, 29),
            dt.datetime(y0, 3, 1),
            dt.datetime(y0 + 1, 2, 28),
            dt.datetime(y0 + 1, 3, 1),
        ]
    )

    end_list = (
        [dt.datetime(yN, m, 1) for m in range(1, 13)]
        + [dt.datetime(yN, m, 5) for m in range(1, 13)]
        + [dt.datetime(yN - 1, m, 1) for m in range(1, 13)]
        + [dt.datetime(yN - 1, m, 5) for m in range(1, 13)]
        + [dt.datetime(yN + 1, m, 1) for m in range(1, 13)]
        + [dt.datetime(yN + 1, m, 5) for m in range(1, 13)]
        + [dt.datetime(yN, m, _month_days_29[m]) for m in range(1, 13)]
        + [dt.datetime(yN - 1, m, (0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)[m]) for m in range(1, 13)]
        + [dt.datetime(yN + 1, m, (0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)[m]) for m in range(1, 13)]
        + [
            dt.datetime(yN, 2, 28),
            dt.datetime(yN, 2, 29),
            dt.datetime(yN, 3, 1),
            dt.datetime(yN + 1, 2, 28),
            dt.datetime(yN + 1, 3, 1),
        ]
    )

    print("\nDaily cycle tests")
    it = 0
    dm = len(start_list)
    for start in start_list:
        it += 1
        print(f"   D Test {it} of {dm}")
        for end in end_list:
            cad = YearlyIntervalCycler.with_daily(start, end)
            ind = 0
            e_old = start
            for s, e in cad:
                # print(f"{st(start)}, {st(end)}, {cad.index}, {st(s)}, {st(e)}, ")
                assert s == e_old
                assert cad.index == ind
                assert cad.index == cad.index_from_date(s)
                assert cad.index_to_interval(ind) == (s, e)

                e_old = e
                ind += 1
            assert cad.index + 1 == cad.index_from_date(e)  # e = end date

    start_list = (
        [dt.datetime(y0, 1, 1), dt.datetime(y0, 5, 1), dt.datetime(y0, 6, 1), dt.datetime(y0, 7, 1)]
        + [dt.datetime(y0 - 1, 1, 1), dt.datetime(y0 - 1, 5, 1), dt.datetime(y0 - 1, 6, 1), dt.datetime(y0 - 1, 7, 1)]
        + [dt.datetime(y0 + 1, 1, 1), dt.datetime(y0 + 1, 5, 1), dt.datetime(y0 + 1, 6, 1), dt.datetime(y0 + 1, 7, 1)]
        + [dt.datetime(y0, m, 1) for m in range(2, 13)]
        + [dt.datetime(y0 - 1, m, 1) for m in range(2, 13)]
        + [dt.datetime(y0 + 1, m, 1) for m in range(2, 13)]
        + [
            dt.datetime(y0, 2, 28),
            dt.datetime(y0, 2, 29),
            dt.datetime(y0, 3, 1),
            dt.datetime(y0 + 1, 2, 28),
            dt.datetime(y0 + 1, 3, 1),
        ]
    )

    end_list = (
        [dt.datetime(yN, 1, 1), dt.datetime(yN, 5, 1), dt.datetime(yN, 6, 1), dt.datetime(yN, 7, 1)]
        + [dt.datetime(yN - 1, 1, 1), dt.datetime(yN - 1, 5, 1), dt.datetime(yN - 1, 6, 1), dt.datetime(yN - 1, 7, 1)]
        + [dt.datetime(yN + 1, 1, 1), dt.datetime(yN + 1, 5, 1), dt.datetime(yN + 1, 6, 1), dt.datetime(yN + 1, 7, 1)]
        + [dt.datetime(yN, m, 1) for m in range(2, 13)]
        + [dt.datetime(yN - 1, m, 1) for m in range(2, 13)]
        + [dt.datetime(yN + 1, m, 1) for m in range(2, 13)]
        + [
            dt.datetime(yN, 2, 28),
            dt.datetime(yN, 2, 29),
            dt.datetime(yN, 3, 1),
            dt.datetime(yN + 1, 2, 28),
            dt.datetime(yN + 1, 3, 1),
        ]
    )

    cycles = [(m, d) for m in range(1, 13) for d in range(1, _month_days_29[m] + 1)][6:]
    print("\nSemi-Daily cycle tests")
    it = 0
    dm = len(start_list)
    for start in start_list:
        it += 1
        print(f"   SD Test {it} of {dm}")
        for end in end_list:
            cad = YearlyIntervalCycler(cycles, start, end)
            ind = 0
            e_old = start
            for s, e in cad:
                assert s == e_old
                assert cad.index == ind
                assert cad.index == cad.index_from_date(s)
                assert cad.index_to_interval(ind) == (s, e)

                e_old = e
                ind += 1
            assert cad.index + 1 == cad.index_from_date(e)  # e = end date
    pass

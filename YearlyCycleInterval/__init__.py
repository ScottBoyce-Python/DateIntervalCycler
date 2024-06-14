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

from .YearlyCycleInterval import YearlyCycleInterval

__all__ = [
    "YearlyCycleInterval",
]

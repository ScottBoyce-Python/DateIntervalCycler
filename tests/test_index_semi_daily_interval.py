"""
test_index_semi_daily_interval.py

Full test_index_semi_daily_interval test. However it takes 7 minutes and pytest-xdist does not
distribute the workload well, so it was split into multiple files to improve speed.
"""

from DateIntervalCycler import DateIntervalCycler
import datetime as dt
import pytest

_month_days_29 = DateIntervalCycler.MONTH_DAYS_LEAP

cycles = [(m, d) for m in range(1, 13) for d in range(1, _month_days_29[m] + 1)][6:]  # skip first six days

y0 = 2000  # Must be leap year
yN = 2004  # Must be leap year

start_lists = (
    [dt.datetime(y0, 1, 1), dt.datetime(y0, 5, 1), dt.datetime(y0, 6, 1), dt.datetime(y0, 7, 1)]
    + [dt.datetime(y0 - 1, 1, 1), dt.datetime(y0 - 1, 5, 1), dt.datetime(y0 - 1, 6, 1), dt.datetime(y0 - 1, 7, 1)]
    + [dt.datetime(y0 + 1, 1, 1), dt.datetime(y0 + 1, 5, 1), dt.datetime(y0 + 1, 6, 1), dt.datetime(y0 + 1, 7, 1)]
    + [
        dt.datetime(y0, 2, 28),
        dt.datetime(y0, 2, 29),
        dt.datetime(y0, 3, 1),
        dt.datetime(y0 + 1, 2, 28),
        dt.datetime(y0 + 1, 3, 1),
    ],
    [dt.datetime(y0, m, 1) for m in range(2, 13)],
    [dt.datetime(y0 - 1, m, 1) for m in range(2, 13)],
    [dt.datetime(y0 + 1, m, 1) for m in range(2, 13)],
)

end_list = (
    [dt.datetime(yN, 1, 1), dt.datetime(yN, 5, 1), dt.datetime(yN, 6, 1), dt.datetime(yN, 7, 1)]
    + [dt.datetime(yN - 1, 1, 1), dt.datetime(yN - 1, 5, 1), dt.datetime(yN - 1, 6, 1), dt.datetime(yN - 1, 7, 1)]
    + [dt.datetime(yN + 1, 1, 1), dt.datetime(yN + 1, 5, 1), dt.datetime(yN + 1, 6, 1), dt.datetime(yN + 1, 7, 1)]
    + [
        dt.datetime(yN, 2, 28),
        dt.datetime(yN, 2, 29),
        dt.datetime(yN, 3, 1),
        dt.datetime(yN + 1, 2, 28),
        dt.datetime(yN + 1, 3, 1),
    ]
    + [dt.datetime(yN, m, 1) for m in range(2, 13)]
    + [dt.datetime(yN - 1, m, 1) for m in range(2, 13)]
    + [dt.datetime(yN + 1, m, 1) for m in range(2, 13)]
)


@pytest.mark.skip(
    reason="Test is split into multiple files, test_index_semi_daily_interval_X.py, for better parallel execution"
)
@pytest.mark.slow
@pytest.mark.slow_skip
@pytest.mark.parametrize("start_list, end_list, cycles", [(start_list, end_list, cycles) for start_list in start_lists])
def test_index_semi_daily_interval(start_list, end_list, cycles):
    for start in start_list:
        index_semi_daily_interval_end_list_loop(start, end_list)


def index_semi_daily_interval_end_list_loop(start, end_list):
    for end in end_list:
        cid = DateIntervalCycler(cycles, start, end)
        ind = 0
        e_old = start
        for s, e in cid:
            assert s == e_old
            assert cid.index == ind
            assert cid.index == cid.index_from_date(s)
            assert cid.index_to_interval(ind) == (s, e)

            e_old = e
            ind += 1
        assert cid.index + 1 == cid.index_from_date(e)  # e = end date

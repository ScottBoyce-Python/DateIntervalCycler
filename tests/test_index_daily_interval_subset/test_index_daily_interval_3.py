"""
Subset test derived from test_index_daily_interval.py

The full test_index_daily_interval takes 40 minutes and pytest-xdist does not
distribute the workload well, so it was split into multiple files to improve speed.
"""

from ..test_index_daily_interval import start_lists, end_list
from DateIntervalCycler import DateIntervalCycler
import pytest


@pytest.mark.slow
@pytest.mark.parametrize("start, end_list", [(start, end_list) for start in start_lists[3]])
def test_index_daily_interval(start, end_list):
    for end in end_list:
        cid = DateIntervalCycler.with_daily(start, end)
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

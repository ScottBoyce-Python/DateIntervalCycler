"""
test_index_semi_daily_interval.py

Full index_daily_interval test. However it takes 7 minutes and pytest-xdist does not
distribute the workload well, so it was split into multiple files to improve speed.
"""

from ..test_index_semi_daily_interval import start_lists, end_list, cycles
from DateIntervalCycler import DateIntervalCycler
import pytest


@pytest.mark.parametrize("start, end_list, cycles", [(start, end_list, cycles) for start in start_lists[0]])
def test_index_semi_daily_interval(start, end_list, cycles):
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

"""
test_index_semi_daily_interval.py

Full index_daily_interval test. However it takes 7 minutes and pytest-xdist does not
distribute the workload well, so it was split into multiple files to improve speed.
"""

from ..test_index_semi_daily_interval import start_lists, end_list, cycles, index_semi_daily_interval_end_list_loop
import pytest


@pytest.mark.subset
@pytest.mark.slow
@pytest.mark.parametrize("start, end_list, cycles", [(start, end_list, cycles) for start in start_lists[3]])
def test_index_semi_daily_interval(start, end_list, cycles):
    index_semi_daily_interval_end_list_loop(start, end_list)

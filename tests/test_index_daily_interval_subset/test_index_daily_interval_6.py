"""
Subset test derived from test_index_daily_interval.py

The full test_index_daily_interval takes 40 minutes and pytest-xdist does not
distribute the workload well, so it was split into multiple files to improve speed.
"""

from ..test_index_daily_interval import start_lists, end_list, index_daily_interval_end_list_loop
import pytest


@pytest.mark.subset
@pytest.mark.slow
@pytest.mark.parametrize("start, end_list", [(start, end_list) for start in start_lists[6]])
def test_index_daily_interval(start, end_list):
    # loop defined in skipped test located in test_index_daily_interval.py
    index_daily_interval_end_list_loop(start, end_list)

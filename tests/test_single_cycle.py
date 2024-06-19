from DateIntervalCycler import DateIntervalCycler
import datetime as dt
from collections import deque
import pytest


def _generate_month_datetime(year, month):
    m = month
    y = year - 1

    def gen_dt():
        nonlocal y, m
        y += 1
        return dt.datetime(y, m, 1)

    return gen_dt


@pytest.mark.parametrize(
    "start, end, cycles, mxiter",
    [(dt.datetime(2000, m1, 1), None, [(m2, 1)], 100) for m1 in range(1, 13) for m2 in range(1, 13)]
    + [
        (dt.datetime(2000, m1, 1), dt.datetime(2030, m3, 1), [(m2, 1)], 100)
        for m1 in range(1, 13)
        for m2 in range(1, 13)
        for m3 in [1, 3, 6, 9]
    ],
)
def test_single_cycle(start, end, cycles, mxiter):
    first_interval_start = start
    last_interval_end = end

    year = start.year
    month = cycles[0][0]
    if start.month >= month:
        year += 1

    gen_date = _generate_month_datetime(year, month)

    cid = DateIntervalCycler(cycles, first_interval_start)

    assert cid.interval_start == first_interval_start

    max_hist = 10  # must be >3 and max_hist << mxiter
    date_result = deque(maxlen=max_hist)
    date_expect = deque(maxlen=max_hist)
    for it in range(max_hist):
        date_result.append(cid.next_get()[0])  # 2nd interval to 11th interval
        date_expect.append(gen_date())

    assert date_result == date_expect
    del date_result

    for it in range(mxiter):
        ind = -1  # current interval is equal to the end of date_expect
        for it in range(max_hist - 1):  # move back five intervals
            d1, d2 = cid.back_get()
            ind -= 1
            assert d1 == date_expect[ind]
            assert d2 == date_expect[ind + 1]

        for it in range(max_hist):
            d1, d2 = cid.next_get()
            ind += 1
            if ind == 0:
                date_expect.append(gen_date())
                ind = -1
                assert d1 == date_expect[ind]
            else:
                assert d1 == date_expect[ind]
                if ind < -1:
                    assert d2 == date_expect[ind + 1]

            if cid.at_last_interval:
                assert d2 == last_interval_end
                break

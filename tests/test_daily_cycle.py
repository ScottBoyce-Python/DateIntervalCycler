from DateIntervalCycler import DateIntervalCycler
import datetime as dt
from collections import deque


def daily_dates_generator(start, end):
    one_day = dt.timedelta(days=1)
    yield start, start + one_day
    for it in range(1, (end - start).days):
        start += one_day
        yield start, start + one_day


def daily_dates_function(start, end):
    dg = daily_dates_generator(start, end)
    return lambda: next(dg)


def test_daily_cycle():
    start = dt.datetime(1800, 1, 1)
    end = dt.datetime(2050, 12, 31)
    cid = DateIntervalCycler.with_daily(start, end, start_before_first_interval=True)
    daily = daily_dates_function(start, end)
    max_hist = 33
    date_result = deque(maxlen=max_hist)
    date_expect = deque(maxlen=max_hist)

    assert cid.interval_start == start

    # because of start_before_first_interval=True, the first cid.next_get()
    # returns the first interval, otherwise it would have returned the second.
    for it in range(max_hist):
        date_result.append(cid.next_get())
        date_expect.append(daily())

    assert date_result == date_expect
    del date_result

    for index, new_interval in enumerate(cid, start=max_hist):
        assert cid.index == index
        ind = -1
        for it in range(max_hist):
            interval = cid.back_get()
            assert interval == date_expect[ind]
            assert cid.index == index + ind
            ind -= 1

        ind += 1
        for it in range(max_hist - 1):  #
            ind += 1
            interval = cid.next_get()
            assert interval == date_expect[ind]
            assert cid.index == index + ind

        date_expect.append(daily())
        assert new_interval == date_expect[-1]
        assert new_interval == cid[index]
        assert new_interval == cid.next_get()
        assert index == cid.index

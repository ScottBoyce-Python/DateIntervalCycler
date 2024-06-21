from DateIntervalCycler import DateIntervalCycler
import datetime as dt
import pytest


def half(d1, d2):
    # return date in the middle of d1 and d2
    if d1 > d2:
        d1, d2 = d2, d1
    return d1 + (d2 - d1) / 2


_month_days_29 = DateIntervalCycler.MONTH_DAYS_LEAP

y0 = 2000  # Must be leap year
yN = 2020  # Must be leap year

start_lists = (
    [dt.datetime(y0, m, 1) for m in range(1, 13)],
    [dt.datetime(y0, m, 5) for m in range(1, 13)],
    [dt.datetime(y0 - 1, m, 1) for m in range(1, 13)],
    [dt.datetime(y0 - 1, m, 5) for m in range(1, 13)],
    [dt.datetime(y0 + 1, m, 1) for m in range(1, 13)],
    [dt.datetime(y0 + 1, m, 5) for m in range(1, 13)],
    [dt.datetime(y0, m, _month_days_29[m]) for m in range(1, 13)],
    [dt.datetime(y0 - 1, m, (0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)[m]) for m in range(1, 13)],
    [dt.datetime(y0 + 1, m, (0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)[m]) for m in range(1, 13)],
    [
        dt.datetime(y0, 2, 28),
        dt.datetime(y0, 2, 28),
        dt.datetime(y0, 2, 29),
        dt.datetime(y0, 3, 1),
        dt.datetime(y0 + 1, 2, 28),
        dt.datetime(y0 + 1, 3, 1),
    ],
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


@pytest.mark.parametrize("start_list, end_list", [(start_list, end_list) for start_list in start_lists])
def test_index_2month_interval(start_list, end_list):
    cycles = [
        (2, 1),  # (month, day)
        (4, 1),
        (6, 1),
        (8, 1),
        (10, 1),
    ]
    for start in start_list:
        for end in end_list:
            cid = DateIntervalCycler(cycles, start, end)
            ind = 0
            e_old = start
            for s, e in cid:
                assert s == e_old
                assert cid.index == ind
                assert cid.index == cid.index_from_date(s)
                assert cid.index == cid.index_from_date(half(s, e))
                assert cid.index_to_interval(ind) == (s, e)
                assert cid.index + 1 == cid.index_from_date(e)

                assert cid.index_to_interval(cid.index) == (s, e)
                assert cid.index_to_interval(cid.index, True) == s
                assert cid.index_to_interval(cid.index, False, True) == e

                assert cid.interval_from_date(s) == (s, e)
                assert cid.interval_from_date(half(s, e)) == (s, e)

                e_old = e
                ind += 1

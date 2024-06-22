import pytest
from datetime import datetime as dt
from DateIntervalCycler import DateIntervalCycler


# Test edge cases
def test_empty_intervals():
    with pytest.raises(ValueError):
        DateIntervalCycler([], dt(2020, 1, 1), dt(2021, 1, 1))


def test_invalid_date_order():
    with pytest.raises(ValueError):
        DateIntervalCycler([(1, 1)], dt(2021, 1, 1), dt(2020, 1, 1))


def test_nonexistent_dates():
    with pytest.raises(ValueError):
        DateIntervalCycler([(2, 30)], dt(2020, 1, 1), dt(2021, 1, 1))

    with pytest.raises(ValueError):
        DateIntervalCycler([(-1, 30)], dt(2020, 1, 1), dt(2021, 1, 1))

    with pytest.raises(ValueError):
        DateIntervalCycler([(1, 0)], dt(2020, 1, 1), dt(2021, 1, 1))



def test_leap_year_handling_len1():
    cid = DateIntervalCycler([(2, 29)], dt(2019, 1, 1), dt(2019, 2, 1))
    intervals = cid.tolist()
    assert len(intervals) == 1
    assert len(intervals) == len(cid)
    assert intervals == [(dt(2019, 1, 1), dt(2019, 2, 1))]

    cid = DateIntervalCycler([(2, 29)], dt(2020, 1, 1), dt(2020, 2, 1))
    intervals = cid.tolist()
    assert len(intervals) == 1
    assert len(intervals) == len(cid)
    assert intervals == [(dt(2020, 1, 1), dt(2020, 2, 1))]


def test_leap_year_handling_len2():
    cid = DateIntervalCycler([(2, 29)], dt(2019, 1, 1), dt(2020, 1, 1))
    intervals = cid.tolist()
    assert len(intervals) == 2
    assert len(intervals) == len(cid)
    assert intervals == [
        (dt(2019, 1, 1), dt(2019, 2, 28)),
        (dt(2019, 2, 28), dt(2020, 1, 1)),
    ]

    cid = DateIntervalCycler([(2, 29)], dt(2020, 1, 1), dt(2021, 1, 1))
    intervals = cid.tolist()
    assert len(intervals) == 2
    assert len(intervals) == len(cid)
    assert intervals == [
        (dt(2020, 1, 1), dt(2020, 2, 29)),
        (dt(2020, 2, 29), dt(2021, 1, 1)),
    ]


def test_leap_year_handling_len3():
    cid = DateIntervalCycler([(2, 29)], dt(2019, 1, 1), dt(2021, 1, 1))
    intervals = cid.tolist()
    assert len(intervals) == 3
    assert len(intervals) == len(cid)
    assert intervals == [
        (dt(2019, 1, 1), dt(2019, 2, 28)),
        (dt(2019, 2, 28), dt(2020, 2, 29)),
        (dt(2020, 2, 29), dt(2021, 1, 1)),
    ]

    cid = DateIntervalCycler([(2, 29)], dt(2020, 1, 1), dt(2022, 1, 1))
    intervals = cid.tolist()
    assert len(intervals) == 3
    assert len(intervals) == len(cid)
    assert intervals == [
        (dt(2020, 1, 1), dt(2020, 2, 29)),
        (dt(2020, 2, 29), dt(2021, 2, 28)),
        (dt(2021, 2, 28), dt(2022, 1, 1)),
    ]


def test_leap_year_handling_len4():
    cid = DateIntervalCycler([(2, 29)], dt(2019, 1, 1), dt(2022, 1, 1))
    intervals = cid.tolist()
    assert len(intervals) == 4
    assert len(intervals) == len(cid)
    assert intervals == [
        (dt(2019, 1, 1), dt(2019, 2, 28)),
        (dt(2019, 2, 28), dt(2020, 2, 29)),
        (dt(2020, 2, 29), dt(2021, 2, 28)),
        (dt(2021, 2, 28), dt(2022, 1, 1)),
    ]


def test_leap_year_handling_len6():
    cid = DateIntervalCycler([(2, 29)], dt(2019, 1, 1), dt(2024, 1, 1))
    intervals = cid.tolist()
    assert len(intervals) == 6
    assert len(intervals) == len(cid)
    assert intervals == [
        (dt(2019, 1, 1), dt(2019, 2, 28)),
        (dt(2019, 2, 28), dt(2020, 2, 29)),
        (dt(2020, 2, 29), dt(2021, 2, 28)),
        (dt(2021, 2, 28), dt(2022, 2, 28)),
        (dt(2022, 2, 28), dt(2023, 2, 28)),
        (dt(2023, 2, 28), dt(2024, 1, 1)),
    ]


def test_leap_year_handling_len7():
    cid = DateIntervalCycler([(2, 29)], dt(2019, 1, 1), dt(2025, 1, 1))
    intervals = cid.tolist()
    assert len(intervals) == 7
    assert len(intervals) == len(cid)
    assert intervals == [
        (dt(2019, 1, 1), dt(2019, 2, 28)),
        (dt(2019, 2, 28), dt(2020, 2, 29)),
        (dt(2020, 2, 29), dt(2021, 2, 28)),
        (dt(2021, 2, 28), dt(2022, 2, 28)),
        (dt(2022, 2, 28), dt(2023, 2, 28)),
        (dt(2023, 2, 28), dt(2024, 2, 29)),
        (dt(2024, 2, 29), dt(2025, 1, 1)),
    ]


def test_leap_year_handling_len8():
    cid = DateIntervalCycler([(2, 29)], dt(2019, 1, 1), dt(2026, 1, 1))
    intervals = cid.tolist()
    assert len(intervals) == 8
    assert len(intervals) == len(cid)
    assert intervals == [
        (dt(2019, 1, 1), dt(2019, 2, 28)),
        (dt(2019, 2, 28), dt(2020, 2, 29)),
        (dt(2020, 2, 29), dt(2021, 2, 28)),
        (dt(2021, 2, 28), dt(2022, 2, 28)),
        (dt(2022, 2, 28), dt(2023, 2, 28)),
        (dt(2023, 2, 28), dt(2024, 2, 29)),
        (dt(2024, 2, 29), dt(2025, 2, 28)),
        (dt(2025, 2, 28), dt(2026, 1, 1)),
    ]


def test_leap_year_handling():
    cid = DateIntervalCycler([(2, 29)], dt(2019, 1, 1), dt(2021, 1, 1))
    intervals = cid.tolist()
    assert len(intervals) == 3
    assert len(intervals) == len(cid)
    assert intervals == [
        (dt(2019, 1, 1), dt(2019, 2, 28)),
        (dt(2019, 2, 28), dt(2020, 2, 29)),
        (dt(2020, 2, 29), dt(2021, 1, 1)),
    ]


def test_cycle_on_year_edge():
    cid = DateIntervalCycler([(1, 1), (12, 31)], dt(2020, 1, 1), dt(2021, 1, 1))
    intervals = cid.tolist()
    assert len(intervals) == 2
    assert len(intervals) == len(cid)
    assert intervals == [
        (dt(2020, 1, 1), dt(2020, 12, 31)),
        (dt(2020, 12, 31), dt(2021, 1, 1)),
    ]


def test_monthly_cycle():
    cid = DateIntervalCycler([(1, 15), (2, 15)], dt(2020, 1, 1), dt(2021, 1, 1))
    intervals = cid.tolist()
    assert len(intervals) == 3
    assert len(intervals) == len(cid)
    assert intervals == [
        (dt(2020, 1, 1), dt(2020, 1, 15)),
        (dt(2020, 1, 15), dt(2020, 2, 15)),
        (dt(2020, 2, 15), dt(2021, 1, 1)),
    ]


def test_one_day_cycle():
    cid = DateIntervalCycler([(1, 1)], dt(2020, 1, 1), dt(2020, 1, 2))
    intervals = cid.tolist()
    assert len(intervals) == 1
    assert intervals == [(dt(2020, 1, 1), dt(2020, 1, 2))]

    cid = DateIntervalCycler([(1, 1),(1, 2)], dt(2020, 1, 1), dt(2020, 1, 3))
    intervals = cid.tolist()
    assert len(intervals) == 2
    assert intervals == [(dt(2020, 1, 1), dt(2020, 1, 2)), (dt(2020, 1, 2),dt(2020, 1, 3))]


def test_large_date_range():
    cid = DateIntervalCycler([(1, 1)], dt(2000, 1, 1), dt(2100, 1, 1))
    intervals = cid.tolist()
    assert len(intervals) == len(cid) == 100

    cid = DateIntervalCycler([(1, 1)], dt(2000, 1, 1), dt(2100, 1, 2))
    intervals = cid.tolist()
    assert len(intervals) == len(cid) == 101  # extra interval for (dt(2100, 1, 1), dt(2100, 1, 2)) 

    cid = DateIntervalCycler([(1, 1)], dt(2000, 1, 30), dt(2100, 1, 1))
    intervals = cid.tolist()
    assert len(intervals) == len(cid) == 100


def test_invalid_month():
    with pytest.raises(ValueError):
        DateIntervalCycler([(13, 1)], dt(2020, 1, 1), dt(2021, 1, 1))


def test_invalid_day():
    with pytest.raises(ValueError):
        DateIntervalCycler([(4, 31)], dt(2020, 1, 1), dt(2021, 1, 1))

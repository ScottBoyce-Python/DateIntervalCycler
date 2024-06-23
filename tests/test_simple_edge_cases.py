import pytest
from datetime import datetime as dt
from DateIntervalCycler import DateIntervalCycler


def test_str_intervals():
    cid = DateIntervalCycler([(1, 15), (6, 20)], dt(2019, 1, 4), dt(2020, 2, 4))
    assert repr(cid) == "DateIntervalCycler(cycles=[(1, 15), (6, 20)], start=2019-01-04, end=2020-02-04)"

    assert str(cid) == "(2019-01-04, 2019-01-15)"
    cid.next()
    assert str(cid) == "(2019-01-15, 2019-06-20)"
    cid.next()
    assert str(cid) == "(2019-06-20, 2020-01-15)"
    cid.next()
    assert str(cid) == "(2020-01-15, 2020-02-04)"


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

    cid = DateIntervalCycler([(1, 1), (1, 2)], dt(2020, 1, 1), dt(2020, 1, 3))
    intervals = cid.tolist()
    assert len(intervals) == 2
    assert intervals == [(dt(2020, 1, 1), dt(2020, 1, 2)), (dt(2020, 1, 2), dt(2020, 1, 3))]


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


def test_leap_year_handling_len1_totuple():
    cid = DateIntervalCycler([(2, 29)], dt(2019, 1, 1), dt(2019, 2, 1))
    date_series = cid.totuple()
    assert len(date_series) == 1 + 1
    assert len(date_series) == len(cid) + 1
    assert date_series == tuple((dt(2019, 1, 1), dt(2019, 2, 1)))

    cid = DateIntervalCycler([(2, 29)], dt(2020, 1, 1), dt(2020, 2, 1))
    date_series = cid.totuple()
    assert len(date_series) == 2
    assert len(date_series) == len(cid) + 1
    assert date_series == tuple((dt(2020, 1, 1), dt(2020, 2, 1)))


def test_leap_year_handling_len2_totuple():
    cid = DateIntervalCycler([(2, 29)], dt(2019, 1, 1), dt(2020, 1, 1))
    date_series = cid.totuple()
    assert len(date_series) == 2 + 1
    assert len(date_series) == len(cid) + 1
    assert date_series == tuple(
        (dt(2019, 1, 1), dt(2019, 2, 28), dt(2020, 1, 1)),
    )
    cid = DateIntervalCycler([(2, 29)], dt(2020, 1, 1), dt(2021, 1, 1))
    date_series = cid.totuple()
    assert len(date_series) == 2 + 1
    assert len(date_series) == len(cid) + 1
    assert date_series == tuple(
        (dt(2020, 1, 1), dt(2020, 2, 29), dt(2021, 1, 1)),
    )


def test_leap_year_handling_len3_totuple():
    cid = DateIntervalCycler([(2, 29)], dt(2019, 1, 1), dt(2021, 1, 1))
    date_series = cid.totuple()
    assert len(date_series) == 3 + 1
    assert len(date_series) == len(cid) + 1
    assert date_series == tuple(
        (dt(2019, 1, 1), dt(2019, 2, 28), dt(2020, 2, 29), dt(2021, 1, 1)),
    )

    cid = DateIntervalCycler([(2, 29)], dt(2020, 1, 1), dt(2022, 1, 1))
    date_series = cid.totuple()
    assert len(date_series) == 3 + 1
    assert len(date_series) == len(cid) + 1
    assert date_series == tuple(
        (dt(2020, 1, 1), dt(2020, 2, 29), dt(2021, 2, 28), dt(2022, 1, 1)),
    )


def test_leap_year_handling_len4_totuple():
    cid = DateIntervalCycler([(2, 29)], dt(2019, 1, 1), dt(2022, 1, 1))
    date_series = cid.totuple()
    assert len(date_series) == 4 + 1
    assert len(date_series) == len(cid) + 1
    assert date_series == tuple(
        (dt(2019, 1, 1), dt(2019, 2, 28), dt(2020, 2, 29), dt(2021, 2, 28), dt(2022, 1, 1)),
    )


def test_leap_year_handling_len6_totuple():
    cid = DateIntervalCycler([(2, 29)], dt(2019, 1, 1), dt(2024, 1, 1))
    date_series = cid.totuple()
    assert len(date_series) == 6 + 1
    assert len(date_series) == len(cid) + 1
    assert date_series == tuple(
        (
            dt(2019, 1, 1),
            dt(2019, 2, 28),
            dt(2020, 2, 29),
            dt(2021, 2, 28),
            dt(2022, 2, 28),
            dt(2023, 2, 28),
            dt(2024, 1, 1),
        ),
    )


def test_leap_year_handling_len7_totuple():
    cid = DateIntervalCycler([(2, 29)], dt(2019, 1, 1), dt(2025, 1, 1))
    date_series = cid.totuple()
    assert len(date_series) == 7 + 1
    assert len(date_series) == len(cid) + 1
    assert date_series == tuple(
        (
            dt(2019, 1, 1),
            dt(2019, 2, 28),
            dt(2020, 2, 29),
            dt(2021, 2, 28),
            dt(2022, 2, 28),
            dt(2023, 2, 28),
            dt(2024, 2, 29),
            dt(2025, 1, 1),
        ),
    )


def test_leap_year_handling_len8_totuple():
    cid = DateIntervalCycler([(2, 29)], dt(2019, 1, 1), dt(2026, 1, 1))
    date_series = cid.totuple()
    assert len(date_series) == 8 + 1
    assert len(date_series) == len(cid) + 1
    assert date_series == tuple(
        (
            dt(2019, 1, 1),
            dt(2019, 2, 28),
            dt(2020, 2, 29),
            dt(2021, 2, 28),
            dt(2022, 2, 28),
            dt(2023, 2, 28),
            dt(2024, 2, 29),
            dt(2025, 2, 28),
            dt(2026, 1, 1),
        ),
    )


def test_leap_year_handling_totuple():
    cid = DateIntervalCycler([(2, 29)], dt(2019, 1, 1), dt(2021, 1, 1))
    date_series = cid.totuple()
    assert len(date_series) == 4
    assert len(date_series) == len(cid) + 1
    assert date_series == tuple(
        (dt(2019, 1, 1), dt(2019, 2, 28), dt(2020, 2, 29), dt(2021, 1, 1)),
    )


def test_cycle_on_year_edge_totuple():
    cid = DateIntervalCycler([(1, 1), (12, 31)], dt(2020, 1, 1), dt(2021, 1, 1))
    date_series = cid.totuple()
    assert len(date_series) == 3
    assert len(date_series) == len(cid) + 1
    assert date_series == tuple(
        (dt(2020, 1, 1), dt(2020, 12, 31), dt(2021, 1, 1)),
    )


def test_monthly_cycle_totuple():
    cid = DateIntervalCycler([(1, 15), (2, 15)], dt(2020, 1, 1), dt(2021, 1, 1))
    date_series = cid.totuple()
    assert len(date_series) == 4
    assert len(date_series) == len(cid) + 1
    assert date_series == tuple(
        (dt(2020, 1, 1), dt(2020, 1, 15), dt(2020, 2, 15), dt(2021, 1, 1)),
    )


def test_one_day_cycle_totuple():
    cid = DateIntervalCycler([(1, 1)], dt(2020, 1, 1), dt(2020, 1, 2))
    date_series = cid.totuple()
    assert len(date_series) == 2
    assert date_series == tuple((dt(2020, 1, 1), dt(2020, 1, 2)))

    cid = DateIntervalCycler([(1, 1), (1, 2)], dt(2020, 1, 1), dt(2020, 1, 3))
    date_series = cid.totuple()
    assert len(date_series) == 3
    assert date_series == tuple((dt(2020, 1, 1), dt(2020, 1, 2), dt(2020, 1, 3)))


def test_large_date_range_totuple():
    cid = DateIntervalCycler([(1, 1)], dt(2000, 1, 1), dt(2100, 1, 1))
    date_series = cid.totuple()
    assert len(date_series) == len(cid) + 1 == 100 + 1

    cid = DateIntervalCycler([(1, 1)], dt(2000, 1, 1), dt(2100, 1, 2))
    date_series = cid.totuple()
    assert len(date_series) == len(cid) + 1 == 101 + 1  # extra interval for (dt(2100, 1, 1), dt(2100, 1, 2))

    cid = DateIntervalCycler([(1, 1)], dt(2000, 1, 30), dt(2100, 1, 1))
    date_series = cid.totuple()
    assert len(date_series) == len(cid) + 1 == 100 + 1


def test_invalid_month():
    with pytest.raises(ValueError):
        DateIntervalCycler([(13, 1)], dt(2020, 1, 1), dt(2021, 1, 1))


def test_invalid_day():
    with pytest.raises(ValueError):
        DateIntervalCycler([(4, 31)], dt(2020, 1, 1), dt(2021, 1, 1))


def test_cycle_sort_and_remove_duplicate():
    cycles = [
        (1, 2),
        (6, 12),  # should sort tuples to be in chronological order
        (1, 2),  # should remove duplicates
        (4, 31),  # should raise exception for invalid entries (april has 30 days)
        (9, 20),
        (1, 2),
        (4, 30),
        (10, 21),
        (1, 2),
        (5, 21),
        (9, 8),
        (6, 28),
        (1, 1),
        (9, 29),
        (2, 29),
        (11, 25),
        (9, 9),
        (2, 10),
        (6, 26),
        (6, 4),
        (12, 26),
        (2, 13),
        (11, 28),
        (11, 5),
        (5, 24),
        (8, 16),
        (4, 1),
        (1, 19),
        (8, 21),
        (8, 20),
        (7, 2),
        (10, 7),
        (12, 27),
        (2, 7),
        (1, 8),
        (12, 26),
        (1, 26),
        (6, 1),
        (9, 5),
        (1, 13),
        (12, 26),
        (8, 19),
        (4, 24),
        (9, 11),
        (10, 20),
        (3, 23),
        (7, 1),
        (6, 5),
        (4, 30),
        (7, 13),
        (10, 16),
        (10, 22),
        (5, 24),
    ]

    with pytest.raises(ValueError):
        DateIntervalCycler(cycles, dt(2021, 1, 1))

    cycles.remove((4, 31))

    cid = DateIntervalCycler(cycles, dt(2020, 1, 1))

    assert tuple(map(tuple, cid.cycles.tolist())) == (
        (1, 1),
        (1, 2),
        (1, 8),
        (1, 13),
        (1, 19),
        (1, 26),
        (2, 7),
        (2, 10),
        (2, 13),
        (2, 29),
        (3, 23),
        (4, 1),
        (4, 24),
        (4, 30),
        (5, 21),
        (5, 24),
        (6, 1),
        (6, 4),
        (6, 5),
        (6, 12),
        (6, 26),
        (6, 28),
        (7, 1),
        (7, 2),
        (7, 13),
        (8, 16),
        (8, 19),
        (8, 20),
        (8, 21),
        (9, 5),
        (9, 8),
        (9, 9),
        (9, 11),
        (9, 20),
        (9, 29),
        (10, 7),
        (10, 16),
        (10, 20),
        (10, 21),
        (10, 22),
        (11, 5),
        (11, 25),
        (11, 28),
        (12, 26),
        (12, 27),
    )

    assert cid.interval == (dt(2020, 1, 1), dt(2020, 1, 2))
    assert cid.next_get() == (dt(2020, 1, 2), dt(2020, 1, 8))
    assert cid.next_get() == (dt(2020, 1, 8), dt(2020, 1, 13))
    assert cid.next_get() == (dt(2020, 1, 13), dt(2020, 1, 19))
    assert cid.next_get() == (dt(2020, 1, 19), dt(2020, 1, 26))
    assert cid.next_get() == (dt(2020, 1, 26), dt(2020, 2, 7))

    lst = cid.tolist(end_override=dt(2022, 1, 1))

    assert lst == [
        (dt.strptime(start_date, "%Y-%m-%d"), dt.strptime(end_date, "%Y-%m-%d"))
        for start_date, end_date in [
            ("2020-01-01", "2020-01-02"),
            ("2020-01-02", "2020-01-08"),
            ("2020-01-08", "2020-01-13"),
            ("2020-01-13", "2020-01-19"),
            ("2020-01-19", "2020-01-26"),
            ("2020-01-26", "2020-02-07"),
            ("2020-02-07", "2020-02-10"),
            ("2020-02-10", "2020-02-13"),
            ("2020-02-13", "2020-02-29"),
            ("2020-02-29", "2020-03-23"),
            ("2020-03-23", "2020-04-01"),
            ("2020-04-01", "2020-04-24"),
            ("2020-04-24", "2020-04-30"),
            ("2020-04-30", "2020-05-21"),
            ("2020-05-21", "2020-05-24"),
            ("2020-05-24", "2020-06-01"),
            ("2020-06-01", "2020-06-04"),
            ("2020-06-04", "2020-06-05"),
            ("2020-06-05", "2020-06-12"),
            ("2020-06-12", "2020-06-26"),
            ("2020-06-26", "2020-06-28"),
            ("2020-06-28", "2020-07-01"),
            ("2020-07-01", "2020-07-02"),
            ("2020-07-02", "2020-07-13"),
            ("2020-07-13", "2020-08-16"),
            ("2020-08-16", "2020-08-19"),
            ("2020-08-19", "2020-08-20"),
            ("2020-08-20", "2020-08-21"),
            ("2020-08-21", "2020-09-05"),
            ("2020-09-05", "2020-09-08"),
            ("2020-09-08", "2020-09-09"),
            ("2020-09-09", "2020-09-11"),
            ("2020-09-11", "2020-09-20"),
            ("2020-09-20", "2020-09-29"),
            ("2020-09-29", "2020-10-07"),
            ("2020-10-07", "2020-10-16"),
            ("2020-10-16", "2020-10-20"),
            ("2020-10-20", "2020-10-21"),
            ("2020-10-21", "2020-10-22"),
            ("2020-10-22", "2020-11-05"),
            ("2020-11-05", "2020-11-25"),
            ("2020-11-25", "2020-11-28"),
            ("2020-11-28", "2020-12-26"),
            ("2020-12-26", "2020-12-27"),
            ("2020-12-27", "2021-01-01"),
            ("2021-01-01", "2021-01-02"),
            ("2021-01-02", "2021-01-08"),
            ("2021-01-08", "2021-01-13"),
            ("2021-01-13", "2021-01-19"),
            ("2021-01-19", "2021-01-26"),
            ("2021-01-26", "2021-02-07"),
            ("2021-02-07", "2021-02-10"),
            ("2021-02-10", "2021-02-13"),
            ("2021-02-13", "2021-02-28"),
            ("2021-02-28", "2021-03-23"),
            ("2021-03-23", "2021-04-01"),
            ("2021-04-01", "2021-04-24"),
            ("2021-04-24", "2021-04-30"),
            ("2021-04-30", "2021-05-21"),
            ("2021-05-21", "2021-05-24"),
            ("2021-05-24", "2021-06-01"),
            ("2021-06-01", "2021-06-04"),
            ("2021-06-04", "2021-06-05"),
            ("2021-06-05", "2021-06-12"),
            ("2021-06-12", "2021-06-26"),
            ("2021-06-26", "2021-06-28"),
            ("2021-06-28", "2021-07-01"),
            ("2021-07-01", "2021-07-02"),
            ("2021-07-02", "2021-07-13"),
            ("2021-07-13", "2021-08-16"),
            ("2021-08-16", "2021-08-19"),
            ("2021-08-19", "2021-08-20"),
            ("2021-08-20", "2021-08-21"),
            ("2021-08-21", "2021-09-05"),
            ("2021-09-05", "2021-09-08"),
            ("2021-09-08", "2021-09-09"),
            ("2021-09-09", "2021-09-11"),
            ("2021-09-11", "2021-09-20"),
            ("2021-09-20", "2021-09-29"),
            ("2021-09-29", "2021-10-07"),
            ("2021-10-07", "2021-10-16"),
            ("2021-10-16", "2021-10-20"),
            ("2021-10-20", "2021-10-21"),
            ("2021-10-21", "2021-10-22"),
            ("2021-10-22", "2021-11-05"),
            ("2021-11-05", "2021-11-25"),
            ("2021-11-25", "2021-11-28"),
            ("2021-11-28", "2021-12-26"),
            ("2021-12-26", "2021-12-27"),
            ("2021-12-27", "2022-01-01"),
        ]
    ]

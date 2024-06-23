from DateIntervalCycler import DateIntervalCycler
import datetime as dt


def test_with_monthly():
    start = dt.datetime(1900, 1, 1)
    end = dt.datetime(2050, 12, 31)

    cid = DateIntervalCycler.with_monthly(start, end)

    assert len(cid) == 1812  # months
    assert cid.size == 1812

    assert tuple(map(tuple, cid.cycles.tolist())) == (
        (1, 1),
        (2, 1),
        (3, 1),
        (4, 1),
        (5, 1),
        (6, 1),
        (7, 1),
        (8, 1),
        (9, 1),
        (10, 1),
        (11, 1),
        (12, 1),
    )

    cid2 = DateIntervalCycler.with_monthly(start)

    assert len(cid2) == DateIntervalCycler.MAX_INTERVAL  # no end date specified
    assert cid2.size == DateIntervalCycler.MAX_INTERVAL

    assert tuple(map(tuple, cid.cycles)) == tuple(map(tuple, cid2.cycles))
    assert tuple(map(tuple, cid.cycles)) == tuple(map(tuple, cid2.copy().cycles))  # generate a copy


def test_with_monthly_end():
    start = dt.datetime(1900, 1, 1)
    end = dt.datetime(2050, 12, 31)

    cid = DateIntervalCycler.with_monthly_end(start, end)

    assert len(cid) == 1812  # months
    assert cid.size == 1812

    assert tuple(map(tuple, cid.cycles)) == (
        (1, 31),
        (2, 29),
        (3, 31),
        (4, 30),
        (5, 31),
        (6, 30),
        (7, 31),
        (8, 31),
        (9, 30),
        (10, 31),
        (11, 30),
        (12, 31),
    )

    cid2 = DateIntervalCycler.with_monthly_end(start)

    assert len(cid2) == DateIntervalCycler.MAX_INTERVAL  # no end date specified
    assert cid2.size == DateIntervalCycler.MAX_INTERVAL

    assert tuple(map(tuple, cid.cycles)) == tuple(map(tuple, cid2.cycles))
    assert tuple(map(tuple, cid.cycles)) == tuple(map(tuple, cid2.copy().cycles))  # generate a copy


def test_with_daily():
    def month_day_tuples():
        date = dt.datetime(2000, 1, 1)  # must be leap year to include (2, 29)
        md = [(1, 1)]
        for it in range(365):
            date += dt.timedelta(days=1)
            md.append((date.month, date.day))
        return tuple(md)

    start = dt.datetime(1900, 1, 1)
    end = dt.datetime(2050, 12, 31)

    cid = DateIntervalCycler.with_daily(start, end)

    assert len(cid) == (end - start).days
    assert cid.size == len(cid)

    assert tuple(map(tuple, cid.cycles)) == month_day_tuples()

    cid2 = DateIntervalCycler.with_daily(start)

    assert len(cid2) == DateIntervalCycler.MAX_INTERVAL  # no end date specified
    assert cid2.size == DateIntervalCycler.MAX_INTERVAL

    assert tuple(map(tuple, cid.cycles)) == tuple(map(tuple, cid2.cycles))
    assert tuple(map(tuple, cid.cycles)) == tuple(map(tuple, cid2.copy().cycles))  # generate a copy


def test_from_year_start():
    cycles = [
        (1, 1),  # (month, day)
        (4, 1),
        (7, 1),
        (10, 1),
    ]

    dates = [
        dt.datetime(2000, 1, 1),
        dt.datetime(2000, 4, 1),
        dt.datetime(2000, 7, 1),
        dt.datetime(2000, 10, 1),
        dt.datetime(2001, 1, 1),
        dt.datetime(2001, 4, 1),
        dt.datetime(2001, 7, 1),
        dt.datetime(2001, 10, 1),
        dt.datetime(2002, 1, 1),
        dt.datetime(2002, 4, 1),
        dt.datetime(2002, 7, 1),
        dt.datetime(2002, 10, 1),
    ]

    it = -1
    for date in dates:
        it += 1
        if it == len(cycles):
            it = 0
        cid1 = DateIntervalCycler.from_year(cycles, date.year, starting_cycle_index=it)
        cid2 = DateIntervalCycler(cycles, date)

        assert cid1.first_interval_start == cid2.first_interval_start

        assert cid1.next_get() == cid2.next_get()
        assert cid1.next_get() == cid2.next_get()
        assert cid1.next_get() == cid2.next_get()
        assert cid1.next_get() == cid2.next_get()
        assert cid1.next_get() == cid2.next_get()
        assert cid1.next_get() == cid2.next_get()
        assert cid1.back_get() == cid2.back_get()
        assert cid1.back_get() == cid2.back_get()
        assert cid1.next_get() == cid2.next_get()
        assert cid1.next_get() == cid2.next_get()
        assert cid1.next_get() == cid2.next_get()

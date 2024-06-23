from DateIntervalCycler import DateIntervalCycler
import datetime as dt

_month_days_29 = DateIntervalCycler.MONTH_DAYS_LEAP

y0 = 2000  # Must be leap year
yN = 2016  # Must be leap year

start_list = (
    [dt.datetime(y0, m, 1) for m in range(1, 13)]
    + [dt.datetime(y0, m, 5) for m in range(1, 13)]
    + [dt.datetime(y0 - 1, m, 1) for m in range(1, 13)]
    + [dt.datetime(y0 - 1, m, 5) for m in range(1, 13)]
    + [dt.datetime(y0 + 1, m, 1) for m in range(1, 13)]
    + [dt.datetime(y0 + 1, m, 5) for m in range(1, 13)]
    + [dt.datetime(y0, m, _month_days_29[m]) for m in range(1, 13)]
    + [dt.datetime(y0 - 1, m, (0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)[m]) for m in range(1, 13)]
    + [dt.datetime(y0 + 1, m, (0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)[m]) for m in range(1, 13)]
    + [
        dt.datetime(y0, 2, 28),
        dt.datetime(y0, 2, 29),
        dt.datetime(y0, 3, 1),
        dt.datetime(y0 + 1, 2, 28),
        dt.datetime(y0 + 1, 3, 1),
    ]
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


cycle_list = [
    [
        (1, 1),  # (month, day)
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
    ],
    [
        (1, 1),
        (3, 1),
        (5, 1),
        (7, 1),
        (9, 1),
        (11, 1),
    ],
    [
        (3, 1),
        (6, 1),
        (9, 1),
        (12, 1),
    ],
    [
        (1, 1),
        (1, 15),
        (2, 1),
        (2, 15),
        (3, 1),
        (4, 1),
        (5, 1),
        (6, 1),
        (8, 1),
        (9, 1),
        (9, 5),
        (9, 10),
        (9, 15),
        (9, 20),
        (10, 1),
        (10, 30),
        (11, 1),
    ],
    [
        (4, 20),
    ],
    [
        (3, 1),
        (9, 1),
    ],
    [
        (1, 1),
        (1, 3),
        (1, 5),
        (1, 7),
        (1, 9),
        (1, 11),
        (1, 13),
        (1, 15),
        (1, 17),
        (1, 27),
        (2, 28),
        (3, 10),
        (4, 20),
    ],
]


def test_size_attribute_cycle():
    for cycles in cycle_list:
        for start in start_list:
            for end in end_list:
                cid = DateIntervalCycler(cycles, start, end)
                assert cid.size == len(cid.tolist())
                assert cid.size == len(cid.totuple()) - 1


def test_size_attribute_cycle_with_set():
    NUL = dt.datetime(9999, 1, 1)
    for cycles in cycle_list:
        cid = DateIntervalCycler(cycles, NUL)  # just set up object with cycles
        for start in start_list:
            cid.set_first_interval_start(start)
            for end in end_list:
                cid.set_last_interval_end(end)
                assert len(cid) == len(cid.tolist())
                assert len(cid) == len(cid.totuple()) - 1

# DateIntervalCycler - Numpy Version

<p align="left">
  <img src="https://github.com/ScottBoyce-Python/DateIntervalCycler/actions/workflows/python-pytest-numpy.yml/badge.svg" alt="Build Status" height="20">
</p>
This version of DateIntervalCycler is dependent upon Numpy for storing the cycles. It was the original design of DateIntervalCycler, before pivoting to using a tuple of tuples to store the cycles. The numpy version tends to be significantly slower than the tuple version, but is retained for testing and future comparisons.

&nbsp; 

DateIntervalCycler is a Python object that cycles through datetime intervals based on provided (month, day) tuples. Intervals can be cycled through using a next and back methods or as an iterator within a loop. Specific intervals can be queried with an index or containing date. Lastly, the entire interval series can be converted to a list of tuples or list of the start date for each interval.

The list of (month, day) tuples is called the "cycles". If cycles contains (2, 29), then it will honor leap years by setting the interval date time (2, 28) for non-leap years. However, if the cycles contains both (2, 28) and (2, 29), then it will skip using (2, 29) for non-leap years as the interval from Feb-28 to Feb-29 does not exist. If cycles only contains (2, 28), then the object functions as normal with generating intervals.



## Installation
To install the numpy version of the module
```bash
pip install git+https://github.com/ScottBoyce-Python/DateIntervalCycler@numpy-dep
```

or you can clone the respository with
```bash
git clone https://github.com/ScottBoyce-Python/DateIntervalCycler.git
git switch numpy-dep # move to numpy version
```
and then move the file `DateIntervalCycler/DateIntervalCycler.py` to wherever you want to use it.

However,  it is recommended to instead use the tuple version and install it with:

```bash
pip install --upgrade git+https://github.com/ScottBoyce-Python/DateIntervalCycler.git
```


## Usage
DateIntervalCycler `with_` constructors example:

```python
from DateIntervalCycler import DateIntervalCycler
from datetime import datetime

# Initialize the cycler with a start date, end date
start_date = datetime(2000, 1, 15)
end_date = datetime(2002, 2, 10)

cid_monthly     = DateIntervalCycler.with_monthly(start_date, end_date)     # Cycles first of each month between two dates
cid_monthly_end = DateIntervalCycler.with_monthly_end(start_date, end_date) # Cycles last day of each month between two dates
cid_daily       = DateIntervalCycler.with_daily(start_date, end_date)       # Cycles every day between two dates


# Iterate through the intervals
print("Index,       Start,  End")
for interval_start, interval_end in cid_monthly:
    if 4 < cid_monthly.index < cid_monthly.size - 4:
        continue
    print(f"{cid_monthly.index:>5},  {interval_start.strftime('%Y-%m-%d')},  {interval_end.strftime('%Y-%m-%d')}")

print("\nIndex,       Start,  End")
for interval_start, interval_end in cid_monthly_end:
    if 4 < cid_monthly_end.index < cid_monthly_end.size - 4:
        continue
    print(f"{cid_monthly_end.index:>5},  {interval_start.strftime('%Y-%m-%d')},  {interval_end.strftime('%Y-%m-%d')}")

print("\nIndex,       Start,  End")
for interval_start, interval_end in cid_daily:
     if 4 < cid_daily.index < cid_daily.size - 4:
        continue
     print(f"{cid_daily.index:>5},  {interval_start.strftime('%Y-%m-%d')},  {interval_end.strftime('%Y-%m-%d')}")
```

&nbsp; 

After running the previous code, the terminal output is:

```
Index,       Start,  End
    0,  2000-01-15,  2000-02-01
    1,  2000-02-01,  2000-03-01
    2,  2000-03-01,  2000-04-01
    3,  2000-04-01,  2000-05-01
    4,  2000-05-01,  2000-06-01
   22,  2001-11-01,  2001-12-01
   23,  2001-12-01,  2002-01-01
   24,  2002-01-01,  2002-02-01
   25,  2002-02-01,  2002-02-10

Index,       Start,  End
    0,  2000-01-15,  2000-01-31
    1,  2000-01-31,  2000-02-29
    2,  2000-02-29,  2000-03-31
    3,  2000-03-31,  2000-04-30
    4,  2000-04-30,  2000-05-31
   22,  2001-10-31,  2001-11-30
   23,  2001-11-30,  2001-12-31
   24,  2001-12-31,  2002-01-31
   25,  2002-01-31,  2002-02-10

Index,       Start,  End
    0,  2000-01-15,  2000-01-16
    1,  2000-01-16,  2000-01-17
    2,  2000-01-17,  2000-01-18
    3,  2000-01-18,  2000-01-19
    4,  2000-01-19,  2000-01-20
  753,  2002-02-06,  2002-02-07
  754,  2002-02-07,  2002-02-08
  755,  2002-02-08,  2002-02-09
  756,  2002-02-09,  2002-02-10
```

&nbsp; 

 Here is a full example of the DateIntervalCycler class:

```python
from DateIntervalCycler import DateIntervalCycler
from datetime import datetime

# Initialize the cycler with a start date, end date, and interval pattern
start_date = datetime(2000, 1, 1)
end_date = datetime(2005, 6, 1)

cycles = [
    (1, 1),  # (month, day)
    (4, 1),
    (7, 1),
    (10, 1),
]

cid = DateIntervalCycler(cycles, start_date, end_date)

# Iterate through the intervals
print("Index,       Start,  End")
for interval_start, interval_end in cid:
    print(f"{cid.index:>5},  {interval_start.strftime('%Y-%m-%d')},  {interval_end.strftime('%Y-%m-%d')}")

cid.reset()  # reset to start of series

print("\nIndex,       Start,  End")
for i in range(4):
    interval_start, interval_end = cid.interval  # get current interval
    cid.next()                                   # move to next interval
    print(f"{cid.index:>5},  {interval_start.strftime('%Y-%m-%d')},  {interval_end.strftime('%Y-%m-%d')}")

cid.reset(start_before_first_interval=True)  # first call to next() sets first interval as current 
                                             # rather than second interval

print("\nIndex,       Start,  End")
for i in range(4):
    interval_start, interval_end = cid.next_get()  # equivalent to: cid.next(); cid.interval
    print(f"{cid.index:>5},  {interval_start.strftime('%Y-%m-%d')},  {interval_end.strftime('%Y-%m-%d')}")
    
# Example of index and date lookup
lookup_date = datetime(2003, 4, 15) 
lookup_index = 20

index                          = cid.index_from_date   (lookup_date)   # find index of interval that contains the date
interval_start0, interval_end0 = cid.index_to_interval (lookup_index)  # find interval for given index
interval_start1, interval_end1 = cid.interval_from_date(lookup_date)   # find interval for given date

interval_start2, interval_end2 = cid.index_to_interval(cid.index_from_date(lookup_date))   # find interval for given index


interval0 = f"{interval_start0.strftime('%Y-%m-%d')},  {interval_end0.strftime('%Y-%m-%d')}"
interval1 = f"{interval_start1.strftime('%Y-%m-%d')},  {interval_end1.strftime('%Y-%m-%d')}"
interval2 = f"{interval_start2.strftime('%Y-%m-%d')},  {interval_end2.strftime('%Y-%m-%d')}"


print("\nindex_to_ and  index_from_ results")
print(index)            # from cid.index_from_date(lookup_date)
print(interval0)        # from cid.index_to_interval(lookup_index)
print(interval1)        # from cid.interval_from_date(lookup_date); faster than index_to_interval(index_from_date(date))
print(interval2)        # from index_to_interval(index_from_date(date))
```

&nbsp; 

After running the previous code, the terminal output is:

```
Index,       Start,  End
    0,  2000-01-01,  2000-04-01
    1,  2000-04-01,  2000-07-01
    2,  2000-07-01,  2000-10-01
    3,  2000-10-01,  2001-01-01
    4,  2001-01-01,  2001-04-01
    5,  2001-04-01,  2001-07-01
    6,  2001-07-01,  2001-10-01
    7,  2001-10-01,  2002-01-01
    8,  2002-01-01,  2002-04-01
    9,  2002-04-01,  2002-07-01
   10,  2002-07-01,  2002-10-01
   11,  2002-10-01,  2003-01-01
   12,  2003-01-01,  2003-04-01
   13,  2003-04-01,  2003-07-01
   14,  2003-07-01,  2003-10-01
   15,  2003-10-01,  2004-01-01
   16,  2004-01-01,  2004-04-01
   17,  2004-04-01,  2004-07-01
   18,  2004-07-01,  2004-10-01
   19,  2004-10-01,  2005-01-01
   20,  2005-01-01,  2005-04-01
   21,  2005-04-01,  2005-06-01

Index,       Start,  End
    1,  2000-01-01,  2000-04-01
    2,  2000-04-01,  2000-07-01
    3,  2000-07-01,  2000-10-01
    4,  2000-10-01,  2001-01-01

Index,       Start,  End
    0,  2000-01-01,  2000-04-01
    1,  2000-04-01,  2000-07-01
    2,  2000-07-01,  2000-10-01
    3,  2000-10-01,  2001-01-01

index_to_ and  index_from_ results
13
2005-01-01,  2005-04-01
2003-04-01,  2003-07-01
2003-04-01,  2003-07-01
```



## Testing

This project uses `pytest` and `pytest-xdist` for testing. Tests are located in the `tests` folder. Tests that are very slow are marked as being "slow". The `tests` directory contains multiple subdirectories that contain equivalent slow tests are divided into multiple files to improve parallel execution. The original, slow tests are marked as "slow_skip" and skipped, while the subdirectory tests are marked as "subset".

To run tests, install the required packages and execute the following command:

```bash
pip install pytest pytest-xdist

pytest  # run all tests, note options are set in the pyproject.toml file

pytest -m "not slow"  # skip index tests that are time consuming.

pytest --run-slow-skip # runs oringinal slow tests and skips the subset ones, which are reduntant.
```

&nbsp; 

Note, that the [pyproject.toml](pyproject.toml) file is configured to run `pytest` with the following arguments:

```toml
[tool.pytest.ini_options]
# agressive parallel options
addopts = "-ra --dist worksteal -nauto"
```



## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contributing
Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

## Author
Scott E. Boyce

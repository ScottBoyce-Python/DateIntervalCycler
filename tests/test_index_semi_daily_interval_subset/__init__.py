"""
DateIntervalCycler pytest functions for validation.

Subset test derived from ../test_index_semi_daily_interval.py

The full test_index_daily_interval takes 40 minutes and pytest-xdist does not
distribute the workload well, so it was split into multiple files to improve speed.
"""

# Note: File is necessary for vscode to prevent a "pytest test discovery error for workspace"
#       If not present then the following error is raised:
#
# [error] Subprocess exited unsuccessfully with exit code 2 and signal null on workspace c:\XYZ\XYZ\XYZ\DateIntervalCycler.
# [error] Subprocess exited unsuccessfully with exit code 2 and signal null on workspace c:\XYZ\XYZ\XYZ\DateIntervalCycler. Creating and sending error discovery payload
# [error] pytest test discovery error for workspace:  c:\XYZ\XYZ\XYZ\DateIntervalCycler
#
# The python test process was terminated before it could exit on its own, the process errored with: Code: 2, Signal: null for workspace c:\XYZ\XYZ\XYZ\DateIntervalCycler

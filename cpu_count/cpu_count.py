# Internal
import os
import typing as T
from math import ceil
from posix import cpu_count as os_cpu_count  # type: ignore
from pathlib import Path
from contextlib import suppress


def cpu_count() -> T.Optional[int]:
    """Custom `cpu_count` that takes into account system constraints to calculate the number of CPUs
    available for the current python process.

    > The returned number of CPUs is the minimum (larger than 1) of the following constraints:
     * the number of CPUs in the system, as given by `posix.cpu_count`
     * the CPU affinity settings of the current process
        (available on some Unix systems)
     * CFS scheduler CPU bandwidth limit
        (available on Linux only, typically set by docker and similar container orchestration systems)

    Modified from:
        https://github.com/tomMoral/loky/blob/dc2d941d8285a96f3a5b666a4bd04875b0b25984/loky/backend/context.py#L104

    Originally licensed under:
        BSD 3-Clause "New" or "Revised" License
        https://github.com/tomMoral/loky/blob/dc2d941d8285a96f3a5b666a4bd04875b0b25984/LICENSE.txt

    Returns:
       Return the number of CPUs the current process can use.

    """
    constraints = [None] * 3  # type: T.List[T.Optional[int]]
    constraints[0] = os_cpu_count()

    # Number of available CPUs given affinity settings
    # More info: http://man7.org/linux/man-pages/man2/sched_setaffinity.2.html
    if hasattr(os, "sched_getaffinity"):
        with suppress(NotImplementedError):
            constraints[1] = len(os.sched_getaffinity(0))

    # CFS scheduler CPU bandwidth limit
    # More info: https://www.kernel.org/doc/Documentation/scheduler/sched-bwc.txt
    try:
        # cpu.cfs_quota_us: CPU clock time allocated within a period (in microseconds)
        cfs_quota = int(Path("/sys/fs/cgroup/cpu/cpu.cfs_quota_us").read_text(errors="strict"))
        # cpu.cfs_period_us: Real world time length of a period (in microseconds)
        cfs_period = int(Path("/sys/fs/cgroup/cpu/cpu.cfs_period_us").read_text(errors="strict"))
    except (OSError, ValueError):
        pass
    else:
        if cfs_quota > 0 and cfs_period > 0:
            # We are only interested in how many CPUs can be allocated to this process. However the
            # result of `cfs_quota / cfs_period` is a decimal representing the proportion between
            # CPU clock time allocated and real world time available to run this process. As any
            # time surplus, including fractions, must be allocated in extra cores to archive the
            # desired proportion, rounding up this value to the closest integer represents the
            # maximum number of cores this process can use simultaneously.
            constraints[2] = int(ceil(cfs_quota / cfs_period))

    # TODO: Add Realtime Scheduler constrain
    # More info: https://www.kernel.org/doc/Documentation/scheduler/sched-rt-group.txt

    values = tuple(constrain for constrain in constraints if constrain is not None)
    if not values:
        # We couldn't get any valid constraint value, so return None
        return None

    return max(min(*values), 1)

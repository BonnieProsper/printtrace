"""
Synchronization primitives for printtrace.

This module owns exactly one responsibility:
- providing a single, global mechanism to make output atomic and ordered

Design constraints (do not violate):
- one global lock, no queues, no worker threads
- lock scope must be minimal and explicit
- no dependency on formatting, context, or stdout details
"""

from __future__ import annotations

import threading
from contextlib import contextmanager


# A single global lock guarding *entire* output blocks.
#
# This is intentionally module-level:
# - stdout is a process-wide resource
# - ordering across threads only makes sense globally
# - debugging output favors correctness over throughput
_output_lock = threading.Lock()


@contextmanager
def output_lock():
    """
    Context manager that serializes output.

    Any code that writes a complete trace block to stdout must
    hold this lock for the entire duration of the write.

    The lock must NOT be held while:
    - inspecting the call stack
    - formatting messages
    - constructing strings

    Ordering guarantee:
        The order of output blocks is the order in which threads
        acquire this lock. No stronger guarantee is promised.
    """
    _output_lock.acquire()
    try:
        yield
    finally:
        _output_lock.release()


__all__ = ["output_lock"]

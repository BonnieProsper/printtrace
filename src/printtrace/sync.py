"""
Global output lock for printtrace.

Constraints:
- one lock, no queues, no worker threads
- lock scope covers only the write() call
- no imports from formatting, context, or api
"""

from __future__ import annotations

import threading
from collections.abc import Generator
from contextlib import contextmanager


_output_lock = threading.Lock()


@contextmanager
def output_lock() -> Generator[None, None, None]:
    """
    Serialize output across threads.

    All formatting must be done before acquiring this lock.
    Threads acquire in arrival order; that order is the output order.
    """
    with _output_lock:
        yield


__all__ = ["output_lock"]

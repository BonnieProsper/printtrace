"""
Call-site context capture for printtrace.

This module is intentionally small and opinionated.
It captures *just enough* information to make print-style debugging
useful in concurrent code, without turning into logging.
"""

from __future__ import annotations

import inspect
import threading

from ._types import CallContext

# Internal constant: how many frames to skip to reach the user callsite.
# This is deliberately conservative and tested.
_SKIP_FRAMES = 2


def capture_context(skip: int = _SKIP_FRAMES) -> CallContext:
    """
    Capture call-site context for the *user* invoking printtrace.

    Parameters
    ----------
    skip:
        Number of stack frames to skip. Defaults to internal constant
        suitable for printtrace wrappers.
    """
    frame = inspect.currentframe()
    try:
        # Walk up the stack to the target frame
        for _ in range(skip):
            if frame is None or frame.f_back is None:
                break
            frame = frame.f_back

        if frame is None:
            return _fallback_context()

        code = frame.f_code
        return CallContext(
            filename=code.co_filename,
            lineno=frame.f_lineno,
            function=code.co_name,
            thread_name=threading.current_thread().name,
        )
    finally:
        # Explicitly break reference cycles
        del frame


def _fallback_context() -> CallContext:
    """Used only if frame inspection fails unexpectedly."""
    return CallContext(
        filename="<unknown>",
        lineno=0,
        function="<unknown>",
        thread_name=threading.current_thread().name,
    )

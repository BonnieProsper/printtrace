"""
Call-site context capture for printtrace.

Captures thread name, filename, line number, and function name for the
frame that called printtrace().

Writing a wrapper around printtrace?
-------------------------------------
If you add a function that calls ``printtrace()`` internally, the default
``skip`` value will point at your wrapper rather than your caller.  Pass
an increased ``skip`` value to ``capture_context`` to compensate:

.. code-block:: python

    from printtrace.context import capture_context, _SKIP_FRAMES

    def my_debug(*values, **kwargs):
        ctx = capture_context(skip=_SKIP_FRAMES + 1)
        ...

Each extra call-stack level between the user's code and the
``capture_context`` call requires one additional skip.
"""

from __future__ import annotations

import inspect
import threading

from ._types import CallContext

# Frames to skip from capture_context() to reach the user's call-site:
#   user code → printtrace() → capture_context()
_SKIP_FRAMES = 2

__all__ = ["capture_context", "_SKIP_FRAMES"]


def capture_context(skip: int = _SKIP_FRAMES) -> CallContext:
    """
    Capture call-site context for the *user* invoking printtrace.

    Parameters
    ----------
    skip:
        Stack frames to skip. Must be >= 0. See module docstring for
        wrapper guidance.
    """
    if skip < 0:
        skip = 0

    frame = inspect.currentframe()
    try:
        for _ in range(skip):
            if frame is None or frame.f_back is None:
                return _fallback_context()
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
        # Break reference cycles — CPython keeps frames alive via f_locals.
        del frame


def _fallback_context() -> CallContext:
    return CallContext(
        filename="<unknown>",
        lineno=0,
        function="<unknown>",
        thread_name=threading.current_thread().name,
    )

"""
Shared data types for printtrace.
"""

from __future__ import annotations
from dataclasses import dataclass

__all__ = ["CallContext"]


@dataclass(frozen=True)
class CallContext:
    """
    Immutable snapshot of the call-site that invoked printtrace.

    Attributes
    ----------
    filename:
        Raw ``f_code.co_filename`` - the full path as CPython reports it.
        The displayed output uses only the basename; this field stores the original.
    lineno:
        Line number of the printtrace call within *filename*.
    function:
        Name of the enclosing function, or ``"<module>"`` for module-level code.
    thread_name:
        ``threading.current_thread().name`` at the moment of the call.
    """

    filename: str
    lineno: int
    function: str
    thread_name: str

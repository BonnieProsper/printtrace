"""
Public API for printtrace.

This module exposes the single intended entry point for users.
Everything else in the package exists to support this function.
"""

from __future__ import annotations

import sys
from typing import TextIO

from .context import capture_context
from .formatting import format_value
from .sync import output_lock


def printtrace(
    *values: object,
    sep: str = " ",
    end: str = "\n",
    file: TextIO | None = None,
) -> None:
    """
    Print a trace-safe debugging line with contextual information.

    This is a deliberate middle ground between print() and logging:
    - thread-safe
    - ordered
    - contextual
    - zero configuration

    Parameters mirror print() where it makes sense.
    """
    out = sys.stdout if file is None else file

    # 1. Capture call-site context (before any locking)
    ctx = capture_context()

    # 2. Format values defensively (before any locking)
    message = sep.join(format_value(v) for v in values) if values else ""

    # 3. Assemble final payload (string-only from here on)
    payload = (
        f"[{ctx.thread_name}] "
        f"{ctx.filename}:{ctx.lineno} "
        f"in {ctx.function} | "
        f"{message}{end}"
    )

    # 4. Emit atomically under the global output lock
    with output_lock():
        out.write(payload)
        out.flush()

"""
Public API for printtrace.

This module exposes the single intended entry point for users.
Everything else in the package exists to support this function.
"""

from __future__ import annotations

import json
import os
import sys
from typing import TextIO

from .context import capture_context
from .formatting import format_value
from .sync import output_lock


DEFAULT_MODE = os.getenv("PRINTTRACE_MODE", "verbose")


def _format_message(*, message: str, context: str, mode: str) -> str:
    if mode == "minimal":
        return message

    if mode == "json":
        return json.dumps(
            {
                "message": message,
                "context": context,
            }
        )

    # verbose (default)
    return f"{context} | {message}"


def printtrace(
    *values: object,
    sep: str = " ",
    end: str = "\n",
    file: TextIO | None = None,
    mode: str | None = None,
) -> None:
    """
    Print a trace-safe debugging line with contextual information.

    A deliberate middle ground between print() and logging:
    thread-safe, ordered, contextual, zero configuration.
    """
    out = sys.stdout if file is None else file
    mode = mode or DEFAULT_MODE

    # 1. Capture call-site context early
    ctx = capture_context()

    context_str = (
        f"[{ctx.thread_name}] "
        f"{ctx.filename}:{ctx.lineno} "
        f"in {ctx.function}"
    )

    # 2. Format values
    if values:
        parts = []
        for v in values:
            if isinstance(v, str):
                parts.append(v)
            else:
                parts.append(format_value(v))
        message = sep.join(parts)
    else:
        message = ""

    # 3. Format final output
    formatted = _format_message(
        message=message,
        context=context_str,
        mode=mode,
    )

    # 4. Emit atomically
    with output_lock():
        out.write(formatted + end)
        out.flush()

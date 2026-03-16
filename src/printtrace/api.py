"""
Public API for printtrace.
"""

from __future__ import annotations

import json
import os
import sys
from typing import Literal, TextIO

from .context import capture_context
from .formatting import format_value
from .sync import output_lock

Mode = Literal["verbose", "minimal", "json"]
_VALID_MODES: frozenset[str] = frozenset({"verbose", "minimal", "json"})

_ENV_VAR = "PRINTTRACE_MODE"
_DEFAULT_MODE: str = "verbose"

__all__ = ["printtrace", "Mode"]


def _resolve_mode(mode: str | None) -> str:
    """Return the effective mode, or raise ValueError if unrecognised.

    Resolution order: explicit argument → PRINTTRACE_MODE env var → "verbose".
    """
    if mode is not None:
        resolved = mode
    else:
        env = os.getenv(_ENV_VAR)
        resolved = env if env is not None else _DEFAULT_MODE

    if resolved not in _VALID_MODES:
        raise ValueError(
            f"Invalid printtrace mode {resolved!r}. "
            f"Expected one of: {sorted(_VALID_MODES)}."
        )
    return resolved


def _format_message(*, message: str, context: str, mode: str) -> str:
    if mode == "minimal":
        return message

    if mode == "json":
        return json.dumps({"message": message, "context": context})

    return f"{context} | {message}"


def _safe_str(value: object) -> str:
    """str() with fallback to repr() and then a sentinel - never raises."""
    try:
        return str(value)
    except Exception:
        try:
            return repr(value)
        except Exception:
            return "<unprintable>"


def _shorten_filename(path: str) -> str:
    return os.path.basename(path) or path


def printtrace(
    *values: object,
    sep: str | None = " ",
    end: str | None = "\n",
    file: TextIO | None = None,
    mode: str | None = None,
) -> None:
    """
    Print a trace-safe debugging line with contextual information.

    A deliberate middle ground between print() and logging:
    thread-safe, ordered, contextual, no configuration.

    Parameters
    ----------
    *values:
        Objects to print. In ``"verbose"`` and ``"json"`` modes these are
        rendered with repr-style formatting (via :func:`format_value`).
        In ``"minimal"`` mode they are rendered with :func:`str`, matching
        the behaviour of the built-in :func:`print`. Both paths never raise.
    sep:
        Separator between values. Defaults to a single space.
        ``None`` is treated as ``" "`` to match :func:`print` semantics.
    end:
        String appended after the last value. Defaults to newline.
        ``None`` is treated as ``"\\n"`` to match :func:`print` semantics.
    file:
        Output stream. Defaults to sys.stdout.
    mode:
        Output mode: ``"verbose"`` (default), ``"minimal"``, or ``"json"``.
        Overrides the ``PRINTTRACE_MODE`` environment variable.

    Raises
    ------
    ValueError
        If *mode* (or ``PRINTTRACE_MODE``) is not one of the valid modes.
    """
    if sep is None:
        sep = " "
    if end is None:
        end = "\n"

    out = sys.stdout if file is None else file
    effective_mode = _resolve_mode(mode)

    ctx = capture_context()

    context_str = (
        f"[{ctx.thread_name}] "
        f"{_shorten_filename(ctx.filename)}:{ctx.lineno} "
        f"in {ctx.function}"
    )

    if effective_mode == "minimal":
        message = sep.join(_safe_str(v) for v in values)
    else:
        message = sep.join(format_value(v) for v in values)

    formatted = _format_message(
        message=message,
        context=context_str,
        mode=effective_mode,
    )

    # Build output before the lock so formatting never runs in the critical section.
    output = formatted + end

    with output_lock():
        out.write(output)

    # Flush outside the lock - a slow stream would otherwise stall all threads.
    out.flush()

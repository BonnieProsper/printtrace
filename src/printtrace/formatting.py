"""
Value formatting for printtrace.

Converts arbitrary Python values into compact, repr-style strings that are
safe to embed in debug output. Key guarantees:

- Never raises: all exceptions are caught and replaced with a sentinel.
- Bounded output: depth, item count, and string length are all capped.
- Brackets match Python's repr: list, tuple, set, frozenset, and empty
  set/frozenset are all rendered distinctly.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any

MAX_DEPTH = 3
MAX_ITEMS = 10
MAX_STR_LEN = 120

__all__ = ["format_value", "MAX_DEPTH", "MAX_ITEMS", "MAX_STR_LEN"]


def format_value(value: Any) -> str:
    """
    Format *value* as a compact, human-readable debug string.

    Always returns a string - never raises.
    """
    try:
        return _format(value, depth=0)
    except Exception:
        try:
            return repr(value)
        except Exception:
            return "<unprintable>"


def _format(value: Any, depth: int) -> str:
    if depth >= MAX_DEPTH:
        return "…"

    if value is None or isinstance(value, (bool, int, float)):
        return repr(value)

    if isinstance(value, str):
        return _format_str(value)

    # Check Mapping before the generic iterable types; dicts are also iterable.
    if isinstance(value, Mapping):
        return _format_mapping(value, depth)

    # Use type() not isinstance() for list/tuple so subclasses (e.g. namedtuples)
    # fall through to repr() and keep their class name.
    if type(value) is list or type(value) is tuple:
        return _format_sequence(value, depth)
    if isinstance(value, (set, frozenset)):
        return _format_sequence(value, depth)

    # repr() covers dataclasses, enums, custom classes, etc.
    try:
        return repr(value)
    except Exception:
        return "<unprintable>"


def _format_str(value: str) -> str:
    if len(value) <= MAX_STR_LEN:
        return repr(value)
    truncated = value[:MAX_STR_LEN]
    return repr(truncated + "…")


def _format_mapping(value: Mapping[Any, Any], depth: int) -> str:
    items: list[str] = []
    for i, (k, v) in enumerate(value.items()):
        if i >= MAX_ITEMS:
            items.append("…")
            break
        try:
            items.append(f"{_format(k, depth + 1)}: {_format(v, depth + 1)}")
        except Exception:
            items.append("<unprintable>")
    return "{" + ", ".join(items) + "}"


def _format_sequence(value: Iterable[Any], depth: int) -> str:
    items: list[str] = []
    for i, item in enumerate(value):
        if i >= MAX_ITEMS:
            items.append("…")
            break
        try:
            items.append(_format(item, depth + 1))
        except Exception:
            items.append("<unprintable>")

    # set() and frozenset() must not render as {} (indistinguishable from empty dict).
    if not items:
        if isinstance(value, frozenset):
            return "frozenset()"
        if isinstance(value, set):
            return "set()"

    open_c, close_c = _brackets(value)
    inner = ", ".join(items)

    # Trailing comma distinguishes (x,) from (x).
    if isinstance(value, tuple) and len(items) == 1 and items[0] != "…":
        inner += ","

    return f"{open_c}{inner}{close_c}"


def _brackets(value: Any) -> tuple[str, str]:
    if isinstance(value, list):
        return "[", "]"
    if isinstance(value, tuple):
        return "(", ")"
    if isinstance(value, frozenset):
        return "frozenset({", "})"
    return "{", "}"

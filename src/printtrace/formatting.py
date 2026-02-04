from __future__ import annotations

from collections.abc import Mapping, Sequence, Set
from typing import Any

MAX_DEPTH = 3
MAX_ITEMS = 10
MAX_STR_LEN = 120


def format_value(value: Any) -> str:
    try:
        return _format(value, depth=0)
    except Exception:
        # Absolute last-resort fallback
        try:
            return repr(value)
        except Exception:
            return '<unprintable>'


def _format(value: Any, depth: int) -> str:
    if depth >= MAX_DEPTH:
        return '…'

    # Primitives
    if value is None or isinstance(value, (bool, int, float)):
        return repr(value)

    if isinstance(value, str):
        return _format_str(value)

    # Mappings
    if isinstance(value, Mapping):
        return _format_mapping(value, depth)

    # Sequences / Sets (but not strings)
    if isinstance(value, (list, tuple, set, frozenset)):
        return _format_sequence(value, depth)

    # Fallback
    try:
        return repr(value)
    except Exception:
        return '<unprintable>'


def _format_str(value: str) -> str:
    if len(value) <= MAX_STR_LEN:
        return repr(value)
    truncated = value[:MAX_STR_LEN]
    return repr(truncated + '…')


def _format_mapping(value: Mapping[Any, Any], depth: int) -> str:
    items = []
    for i, (k, v) in enumerate(value.items()):
        if i >= MAX_ITEMS:
            items.append('…')
            break
        try:
            items.append(f"{_format(k, depth + 1)}: {_format(v, depth + 1)}")
        except Exception:
            items.append('<unprintable>')
    return '{' + ', '.join(items) + '}'


def _format_sequence(value: Sequence[Any] | Set[Any], depth: int) -> str:
    items = []
    for i, item in enumerate(value):
        if i >= MAX_ITEMS:
            items.append('…')
            break
        try:
            items.append(_format(item, depth + 1))
        except Exception:
            items.append('<unprintable>')

    open_c, close_c = _brackets(value)
    return f"{open_c}{', '.join(items)}{close_c}"


def _brackets(value: Any) -> tuple[str, str]:
    if isinstance(value, list):
        return '[', ']'
    if isinstance(value, tuple):
        return '(', ')'
    return '{', '}'
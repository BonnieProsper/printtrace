from __future__ import annotations

import io

from collections import namedtuple

from printtrace import printtrace
from printtrace.formatting import (
    MAX_DEPTH,
    MAX_ITEMS,
    MAX_STR_LEN,
    format_value,
    _format,
)


def test_none():
    assert format_value(None) == "None"


def test_bool_true():
    assert format_value(True) == "True"


def test_bool_false():
    assert format_value(False) == "False"


def test_int():
    assert format_value(42) == "42"


def test_float():
    assert format_value(3.14) == "3.14"


def test_short_string_is_repr():
    assert format_value("hello") == "'hello'"


def test_long_string_is_truncated():
    result = format_value("x" * (MAX_STR_LEN + 50))
    assert "…" in result
    assert len(result) < MAX_STR_LEN + 20


def test_string_at_exact_limit_is_not_truncated():
    assert "…" not in format_value("a" * MAX_STR_LEN)


def test_list():
    assert format_value([1, 2, 3]) == "[1, 2, 3]"


def test_empty_list():
    assert format_value([]) == "[]"


def test_list_truncated_at_max_items():
    result = format_value(list(range(MAX_ITEMS + 5)))
    assert "…" in result
    assert result.startswith("[")


def test_tuple():
    assert format_value((1, 2)) == "(1, 2)"


def test_single_element_tuple_has_trailing_comma():
    assert format_value((42,)) == "(42,)"


def test_empty_tuple():
    assert format_value(()) == "()"


def test_set_uses_curly_brackets():
    result = format_value({1})
    assert result.startswith("{")
    assert result.endswith("}")


def test_frozenset_is_distinguishable_from_set():
    assert format_value({1}) != format_value(frozenset({1}))
    assert "frozenset" in format_value(frozenset({1}))


def test_empty_frozenset():
    assert format_value(frozenset()) == "frozenset()"


def test_empty_set_is_not_confused_with_empty_dict():
    assert format_value(set()) != format_value({})
    assert format_value(set()) == "set()"


def test_empty_frozenset_matches_python_repr():
    assert format_value(frozenset()) == "frozenset()"


def test_dict():
    assert "'a': 1" in format_value({"a": 1})


def test_dict_truncated_at_max_items():
    assert "…" in format_value({i: i for i in range(MAX_ITEMS + 5)})


def test_depth_cap_returns_ellipsis():
    assert _format("anything", depth=MAX_DEPTH) == "…"


def test_nested_list_depth_cap():
    assert "…" in format_value([[[[["too deep"]]]]])


class BrokenRepr:
    def __repr__(self):
        raise RuntimeError("repr exploded")

    def __str__(self):
        raise RuntimeError("str exploded")


def test_broken_repr_does_not_raise():
    assert format_value(BrokenRepr()) in ("<unprintable>", "…")


class BrokenLen:
    def __len__(self):
        raise RuntimeError("len exploded")

    def __iter__(self):
        raise RuntimeError("iter exploded")

    def __repr__(self):
        raise RuntimeError("repr exploded")


def test_totally_broken_object_does_not_raise():
    assert isinstance(format_value(BrokenLen()), str)


def test_namedtuple_retains_class_name():
    """Namedtuple subclasses must not lose their class name to the tuple branch."""
    Point = namedtuple("Point", ["x", "y"])
    result = format_value(Point(1, 2))
    assert "Point" in result, f"got {result!r}"


def test_list_subclass_uses_repr():
    class TaggedList(list):
        def __repr__(self) -> str:
            return f"TaggedList({list.__repr__(self)})"

    assert "TaggedList" in format_value(TaggedList([1, 2]))


def test_bytes_uses_repr():
    assert format_value(b"hello") == "b'hello'"


def test_complex_uses_repr():
    assert format_value(1 + 2j) == "(1+2j)"


def test_empty_minimal_output():
    buf = io.StringIO()
    printtrace(file=buf, mode="minimal")
    assert buf.getvalue() == "\n"

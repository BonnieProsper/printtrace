from __future__ import annotations

import io

from printtrace import printtrace


def test_basic_single_value():
    buf = io.StringIO()
    printtrace("hello", file=buf)

    out = buf.getvalue()
    assert "hello" in out
    assert out.endswith("\n")


def test_multiple_values_default_sep():
    buf = io.StringIO()
    printtrace("a", "b", 3, file=buf)

    out = buf.getvalue()
    assert "'a' 'b' 3" in out


def test_custom_separator():
    buf = io.StringIO()
    printtrace("a", "b", sep=", ", file=buf)

    out = buf.getvalue()
    assert "'a', 'b'" in out


def test_custom_end():
    buf = io.StringIO()
    printtrace("x", end="END", file=buf)

    out = buf.getvalue()
    assert out.endswith("END")


def test_empty_call():
    buf = io.StringIO()
    printtrace(file=buf)

    out = buf.getvalue()
    # Still produces a contextual line
    assert out.strip() != ""

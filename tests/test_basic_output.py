from __future__ import annotations

import io
import json

import pytest

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
    assert "'a' 'b' 3" in buf.getvalue()


def test_custom_separator():
    buf = io.StringIO()
    printtrace("a", "b", sep=", ", file=buf)
    assert "'a', 'b'" in buf.getvalue()


def test_custom_end():
    buf = io.StringIO()
    printtrace("x", end="END", file=buf)
    assert buf.getvalue().endswith("END")


def test_empty_call():
    buf = io.StringIO()
    printtrace(file=buf)
    assert buf.getvalue().strip() != ""


def test_verbose_mode_includes_context():
    buf = io.StringIO()
    printtrace("x", file=buf, mode="verbose")
    out = buf.getvalue()
    assert " | " in out
    assert "test_basic_output" in out


def test_minimal_mode_no_context():
    buf = io.StringIO()
    printtrace("hello", file=buf, mode="minimal")
    assert buf.getvalue().strip() == "hello"


def test_minimal_mode_uses_str_not_repr():
    buf = io.StringIO()
    printtrace(42, file=buf, mode="minimal")
    assert buf.getvalue().strip() == "42"


def test_json_mode_is_valid_json():
    buf = io.StringIO()
    printtrace("hello", file=buf, mode="json")
    data = json.loads(buf.getvalue().strip())
    assert "message" in data
    assert "context" in data
    assert "hello" in data["message"]


def test_invalid_mode_raises_with_name():
    with pytest.raises(ValueError, match="vervose"):
        printtrace("x", mode="vervose")


def test_env_var_is_read_at_call_time(monkeypatch):
    """PRINTTRACE_MODE set after import must take effect on the next call."""
    monkeypatch.setenv("PRINTTRACE_MODE", "minimal")
    buf = io.StringIO()
    printtrace("env-test", file=buf)
    assert " | " not in buf.getvalue()


def test_env_var_invalid_raises(monkeypatch):
    monkeypatch.setenv("PRINTTRACE_MODE", "notamode")
    with pytest.raises(ValueError):
        printtrace("x")


def test_explicit_mode_overrides_env_var(monkeypatch):
    monkeypatch.setenv("PRINTTRACE_MODE", "minimal")
    buf = io.StringIO()
    printtrace("x", file=buf, mode="verbose")
    assert " | " in buf.getvalue()


def test_filename_is_basename_only():
    buf = io.StringIO()
    printtrace("x", file=buf)
    out = buf.getvalue()
    assert "test_basic_output.py" in out
    assert "/home/" not in out
    assert "/Users/" not in out


def test_sep_none_treated_as_space():
    buf = io.StringIO()
    printtrace("a", "b", sep=None, file=buf, mode="minimal")
    assert buf.getvalue().strip() == "a b"


def test_end_none_treated_as_newline():
    buf = io.StringIO()
    printtrace("x", end=None, file=buf, mode="minimal")
    assert buf.getvalue() == "x\n"


def test_mode_empty_string_raises():
    with pytest.raises(ValueError, match="Invalid printtrace mode"):
        printtrace("x", mode="")

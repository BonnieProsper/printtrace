from __future__ import annotations

import io
import inspect
import threading

from printtrace import printtrace
from printtrace.context import capture_context


def _emit(buf: io.StringIO) -> str:
    printtrace("value", file=buf)
    return buf.getvalue()


def test_filename_is_basename_only():
    buf = io.StringIO()
    out = _emit(buf)
    assert "test_context_capture.py" in out
    assert "/src/" not in out


def test_function_name_in_output():
    buf = io.StringIO()
    out = _emit(buf)
    assert "_emit" in out


def test_line_number_is_reasonable():
    buf = io.StringIO()

    frame = inspect.currentframe()
    assert frame is not None
    expected_line = frame.f_lineno + 2

    printtrace("x", file=buf)

    out = buf.getvalue()
    before, after = out.rsplit(":", 1)
    lineno = int(after.split()[0])
    assert abs(lineno - expected_line) <= 2


def test_thread_name():
    buf = io.StringIO()
    printtrace("x", file=buf)
    assert threading.current_thread().name in buf.getvalue()


def test_skip_zero_captures_capture_context_itself():
    ctx = capture_context(skip=0)
    assert "capture_context" in ctx.function


def test_huge_skip_returns_fallback():
    ctx = capture_context(skip=9999)
    assert ctx.filename == "<unknown>"
    assert ctx.function == "<unknown>"
    assert ctx.lineno == 0


def test_negative_skip_clamped():
    ctx = capture_context(skip=-1)
    assert ctx.function == "capture_context"

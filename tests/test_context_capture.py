from __future__ import annotations

import io
import inspect
import threading

from printtrace import printtrace


def _emit(buf: io.StringIO) -> str:
    printtrace("value", file=buf)
    return buf.getvalue()


def test_filename_and_function_name():
    buf = io.StringIO()

    out = _emit(buf)

    # Current test file name should appear
    filename = __file__.split("/")[-1]
    assert filename in out

    # Function name where printtrace was called
    assert "_emit" in out


def test_line_number_is_reasonable():
    buf = io.StringIO()

    expected_line = inspect.currentframe().f_lineno + 2
    printtrace("x", file=buf)

    out = buf.getvalue()

    # Extract last :<lineno>
    before, after = out.rsplit(":", 1)
    lineno_str = after.split()[0]

    lineno = int(lineno_str)
    assert abs(lineno - expected_line) <= 2


def test_thread_name():
    buf = io.StringIO()

    printtrace("x", file=buf)
    out = buf.getvalue()

    assert threading.current_thread().name in out

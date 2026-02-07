from __future__ import annotations

import io
import threading
import pytest


@pytest.fixture
def capture_output():
    """
    Thread-safe output capture for printtrace.

    Returns:
        buffer: StringIO buffer
        get_lines: callable returning list[str]
    """
    buffer = io.StringIO()
    lock = threading.Lock()

    def write(data: str) -> None:
        with lock:
            buffer.write(data)

    class Writer:
        def write(self, data: str) -> None:
            write(data)

        def flush(self) -> None:
            pass

    def get_lines():
        with lock:
            return buffer.getvalue().splitlines()

    return Writer(), get_lines

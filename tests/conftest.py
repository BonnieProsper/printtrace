"""
Shared pytest fixtures for the printtrace test suite.
"""

from __future__ import annotations

import io
import threading
from collections.abc import Callable
from typing import Protocol

import pytest


class _WriterProtocol(Protocol):
    """write() and flush() interface required by printtrace's ``file=`` parameter."""

    def write(self, data: str) -> None: ...
    def flush(self) -> None: ...


@pytest.fixture
def capture_output() -> tuple[_WriterProtocol, Callable[[], list[str]]]:
    """Thread-safe (writer, get_lines) pair for capturing printtrace output."""
    buffer = io.StringIO()
    lock = threading.Lock()

    class Writer:
        def write(self, data: str) -> None:
            with lock:
                buffer.write(data)

        def flush(self) -> None:
            pass

    def get_lines() -> list[str]:
        with lock:
            return buffer.getvalue().splitlines()

    return Writer(), get_lines

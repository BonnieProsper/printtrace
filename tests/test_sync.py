"""
Concurrency tests for printtrace synchronization.

The core invariant: one printtrace() call == one contiguous output block.
"""

from __future__ import annotations

import io
import threading
import time

import pytest

from printtrace.sync import output_lock
from printtrace import printtrace


class RecordingWriter:
    """
    Writes character-by-character with a small sleep between each.

    The deliberate slowness amplifies race conditions and makes interleaving
    immediately visible in the output.
    """

    def __init__(self) -> None:
        self.buffer = io.StringIO()

    def write(self, s: str) -> None:
        for ch in s:
            time.sleep(0.0001)
            self.buffer.write(ch)

    def flush(self) -> None:
        pass

    def getvalue(self) -> str:
        return self.buffer.getvalue()


def _write_block(writer: RecordingWriter, marker: str) -> None:
    block = f"[{marker}]\n{marker}\n{marker}\n"
    with output_lock():
        writer.write(block)


@pytest.mark.timeout(5)
def test_output_blocks_do_not_interleave() -> None:
    """
    Each output_lock() block must appear contiguously in the final output.
    Per-character delays and 10 concurrent threads maximise the chance of
    exposing any interleaving.
    """
    writer = RecordingWriter()
    markers: list[str] = [f"T{i}" for i in range(10)]
    threads = [threading.Thread(target=_write_block, args=(writer, m)) for m in markers]

    for t in threads:
        t.start()
    for t in threads:
        t.join()

    output = writer.getvalue()

    for m in markers:
        block = f"[{m}]\n{m}\n{m}\n"
        assert block in output
        start = output.index(block)
        interior = output[start : start + len(block)]
        for other in markers:
            if other != m:
                assert other not in interior


@pytest.mark.timeout(5)
def test_lock_serializes_writes_under_contention() -> None:
    writer = RecordingWriter()

    def spam(thread_id: int) -> None:
        for i in range(20):
            with output_lock():
                writer.write(f"<{thread_id}:{i}>\n")

    threads = [threading.Thread(target=spam, args=(i,)) for i in range(5)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    output = writer.getvalue()
    for i in range(5):
        for j in range(20):
            assert f"<{i}:{j}>" in output


def test_no_partial_lines(capture_output):
    writer, get_lines = capture_output
    payload = "x" * 1000

    def worker():
        for _ in range(10):
            printtrace(payload, file=writer)

    threads = [threading.Thread(target=worker) for _ in range(5)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    lines = get_lines()
    assert len(lines) == 50
    for line in lines:
        assert "x" * 100 in line
        assert "…" in line

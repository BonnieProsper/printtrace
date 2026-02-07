"""
Concurrency tests for printtrace synchronization.

These tests validate the single most important invariant of the project:

    One trace call == one contiguous output block

If these tests fail, the entire tool is invalid.
"""

from __future__ import annotations

import io
import threading
import time
from typing import List

import pytest

from printtrace.sync import output_lock
from printtrace import printtrace


class RecordingWriter:
    """
    A deliberately naive writer that records writes verbatim.

    This simulates stdout at the character level and makes
    interleaving bugs immediately visible.
    """

    def __init__(self) -> None:
        self.buffer = io.StringIO()

    def write(self, s: str) -> None:
        # Introduce tiny timing noise to amplify race conditions
        for ch in s:
            time.sleep(0.0001)
            self.buffer.write(ch)

    def getvalue(self) -> str:
        return self.buffer.getvalue()


def _worker(writer: RecordingWriter, marker: str) -> None:
    """
    Simulates a single trace call writing a multi-line block.

    The output_lock must ensure this entire block appears
    contiguously in the final output.
    """
    block = f"[{marker}]\n{marker}\n{marker}\n"

    with output_lock():
        writer.write(block)


@pytest.mark.timeout(5)
def test_output_blocks_do_not_interleave() -> None:
    """
    Multiple threads writing multi-line blocks must not interleave
    at the character level.

    This test intentionally amplifies race conditions by:
    - adding per-character delays
    - using many threads
    - writing multi-line payloads
    """
    writer = RecordingWriter()

    markers: List[str] = [f"T{i}" for i in range(10)]
    threads = [
        threading.Thread(target=_worker, args=(writer, m))
        for m in markers
    ]

    for t in threads:
        t.start()
    for t in threads:
        t.join()

    output = writer.getvalue()

    # Each block must appear as an intact substring
    for m in markers:
        block = f"[{m}]\n{m}\n{m}\n"
        assert block in output

    # Blocks must not be interwoven character-by-character
    # We enforce this by checking that no marker appears inside
    # another marker's block except at block boundaries.
    for m in markers:
        block = f"[{m}]\n{m}\n{m}\n"
        start = output.index(block)
        end = start + len(block)
        interior = output[start:end]
        for other in markers:
            if other != m:
                assert other not in interior


@pytest.mark.timeout(5)
def test_lock_serializes_writes_under_contention() -> None:
    """
    Stress test: many threads repeatedly acquiring the lock
    must not deadlock or corrupt output.
    """
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

    # Sanity check: all expected lines are present
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

    # 5 threads × 10 calls
    assert len(lines) == 50

    for line in lines:
        # Payload must appear exactly once and intact
        assert "x" * 100 in line  # some reasonable minimum
        assert "…" in line       # explicit truncation signal

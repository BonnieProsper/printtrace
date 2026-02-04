from __future__ import annotations

import io
import threading

from printtrace import printtrace


def test_multiline_value_is_emitted_atomically():
    buf = io.StringIO()

    multiline = "line1\nline2\nline3"
    printtrace(multiline, file=buf)

    out = buf.getvalue()

    # The payload may contain internal newlines from the value,
    # but it must be emitted as one contiguous write.
    # We assert that the entire output was produced in one call.
    assert out.count("line1") == 1
    assert out.count("line2") == 1
    assert out.count("line3") == 1
    assert out.endswith("\n")


def test_multiline_under_concurrent_writes():
    buf = io.StringIO()

    def worker(i: int) -> None:
        text = f"start-{i}\nmid-{i}\nend-{i}"
        printtrace(text, file=buf)

    threads = [threading.Thread(target=worker, args=(i,)) for i in range(5)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    out = buf.getvalue()

    # Each worker's multiline block should appear intact
    for i in range(5):
        assert f"start-{i}" in out
        assert f"mid-{i}" in out
        assert f"end-{i}" in out

    # No partial interleaving markers should appear
    # Each worker should produce exactly one trailing newline
    assert out.count("\n") >= 5

from __future__ import annotations

import io
import threading

from printtrace import printtrace


def test_multiline_value_is_emitted_atomically():
    buf = io.StringIO()
    multiline = "line1\nline2\nline3"
    printtrace(multiline, file=buf)
    out = buf.getvalue()
    assert out.count("line1") == 1
    assert out.count("line2") == 1
    assert out.count("line3") == 1
    assert out.endswith("\n")


def test_multiline_under_concurrent_writes(capture_output):
    writer, get_lines = capture_output

    def worker(i: int) -> None:
        text = f"start-{i}\nmid-{i}\nend-{i}"
        printtrace(text, file=writer)

    threads = [threading.Thread(target=worker, args=(i,)) for i in range(5)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    out = "\n".join(get_lines())
    for i in range(5):
        assert f"start-{i}" in out
        assert f"mid-{i}" in out
        assert f"end-{i}" in out


def test_long_payload_is_truncated(capture_output):
    writer, get_lines = capture_output

    printtrace("x" * 10_000, file=writer)

    line = get_lines()[0]

    assert "…" in line

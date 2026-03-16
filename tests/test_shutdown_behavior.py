from __future__ import annotations

from printtrace import printtrace


def test_output_not_truncated_at_exit(capture_output):
    writer, get_lines = capture_output

    for i in range(100):
        printtrace("line", i, file=writer, mode="minimal")

    output = get_lines()

    assert len(output) == 100
    assert output[0].startswith("line 0")
    assert output[-1].startswith("line 99")


def test_immediate_exit_pattern(capture_output):
    writer, get_lines = capture_output

    printtrace("last line", file=writer)

    output = get_lines()

    assert len(output) == 1
    assert "last line" in output[0]


def test_minimal_mode_safe_str_exception(capture_output):
    class Evil:
        def __str__(self):
            raise RuntimeError("str exploded")

        def __repr__(self):
            return "<Evil>"

    writer, get_lines = capture_output
    printtrace(Evil(), file=writer, mode="minimal")
    lines = get_lines()
    assert len(lines) == 1
    assert "<Evil>" in lines[0]


def test_minimal_mode_totally_broken_object(capture_output):
    class Broken:
        def __str__(self):
            raise RuntimeError("str")

        def __repr__(self):
            raise RuntimeError("repr")

    writer, get_lines = capture_output
    printtrace(Broken(), file=writer, mode="minimal")
    lines = get_lines()
    assert len(lines) == 1
    assert "<unprintable>" in lines[0]


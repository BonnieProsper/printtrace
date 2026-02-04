import threading

from printtrace.api import printtrace


def test_no_deadlock_on_thread_exit(capture_output):
    writer, get_lines = capture_output

    def worker():
        for _ in range(10):
            printtrace("x", file=writer)

    t = threading.Thread(target=worker)
    t.start()
    t.join(timeout=2)

    assert not t.is_alive()
    assert len(get_lines()) == 10


def test_output_not_truncated_at_exit(capture_output):
    for i in range(100):
        printtrace("line", i)

    output = capture_output()
    assert len(output) == 100


def test_immediate_exit_pattern(capture_output):
    printtrace("last line")

    output = capture_output()
    assert output[-1].endswith("last line\n")

import threading

from printtrace.api import printtrace


def test_no_deadlock_on_thread_exit(capture_output):
    def worker():
        for i in range(10):
            printtrace("worker", i)

    threads = [threading.Thread(target=worker) for _ in range(5)]

    for t in threads:
        t.start()
    for t in threads:
        t.join()

    output = capture_output()
    assert len(output) == 50

def test_output_not_truncated_at_exit(capture_output):
    for i in range(100):
        printtrace("line", i)

    output = capture_output()
    assert len(output) == 100


def test_immediate_exit_pattern(capture_output):
    printtrace("last line")

    output = capture_output()
    assert output[-1].endswith("last line\n")

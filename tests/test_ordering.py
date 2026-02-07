import threading
import time

from printtrace.api import printtrace


def test_ordering_interleaved_calls(capture_output):
    writer, get_lines = capture_output

    def worker(prefix, delay):
        time.sleep(delay)
        printtrace(prefix, file=writer, mode="minimal")

    threads = [
        threading.Thread(target=worker, args=("A", 0.02)),
        threading.Thread(target=worker, args=("B", 0.01)),
        threading.Thread(target=worker, args=("C", 0.00)),
    ]

    for t in threads:
        t.start()
    for t in threads:
        t.join()

    output = get_lines()

    assert len(output) == 3
    assert {line.strip() for line in output} == {"A", "B", "C"}


def test_ordering_multi_thread(capture_output):
    writer, get_lines = capture_output

    def worker(value):
        printtrace(value, file=writer, mode="minimal")

    threads = [
        threading.Thread(target=worker, args=(f"msg-{i}",))
        for i in range(10)
    ]

    for t in threads:
        t.start()
    for t in threads:
        t.join()

    output = get_lines()

    assert len(output) == 10
    assert {line.strip() for line in output} == {
        f"msg-{i}" for i in range(10)
    }


def test_ordering_single_thread(capture_output):
    writer, get_lines = capture_output

    printtrace("first", file=writer, mode="minimal")
    printtrace("second", file=writer, mode="minimal")
    printtrace("third", file=writer, mode="minimal")

    output = get_lines()

    assert output == [
        "first",
        "second",
        "third",
    ]

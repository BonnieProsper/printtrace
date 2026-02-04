import threading
import time

def test_ordering_interleaved_calls(capture_output):
    from printtrace.api import printtrace

    def worker(prefix, delay):
        time.sleep(delay)
        printtrace(prefix)

    threads = [
        threading.Thread(target=worker, args=("A", 0.02)),
        threading.Thread(target=worker, args=("B", 0.01)),
        threading.Thread(target=worker, args=("C", 0.00)),
    ]

    for t in threads:
        t.start()

    for t in threads:
        t.join()

    output = capture_output()

    # Order is determined by call order, not sleep timing
    assert output == ["A", "B", "C"]

def test_ordering_multi_thread(capture_output):
    from printtrace.api import printtrace

    def worker(value):
        printtrace(value)

    threads = [
        threading.Thread(target=worker, args=(f"msg-{i}",))
        for i in range(10)
    ]

    for t in threads:
        t.start()

    for t in threads:
        t.join()

    output = capture_output()

    # Must preserve submission order, not execution order
    assert output == [f"msg-{i}" for i in range(10)]


def test_ordering_single_thread(capture_output):
    from printtrace.api import printtrace

    printtrace("first")
    printtrace("second")
    printtrace("third")

    output = capture_output()

    assert output == [
        "first",
        "second",
        "third",
    ]

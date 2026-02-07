from printtrace import printtrace

printtrace("hello world")
printtrace("hello\nworld")
import threading
from printtrace import printtrace

def worker(i):
    printtrace("worker", i)

threads = [threading.Thread(target=worker, args=(i,)) for i in range(10)]
for t in threads:
    t.start()
for t in threads:
    t.join()

try:
    val = 1 / 0
except Exception as e:
    printtrace("error:", e)

def validate(x):
    if x < 0:
        printtrace("invalid value:", x)

def foo():
    printtrace("inside foo")

printtrace("start")
foo()
printtrace("end")

import threading
import time
from printtrace import printtrace

def worker_2(i):
    for j in range(5):
        printtrace(f"worker {i}", j)
        time.sleep(0.01)

threads = [threading.Thread(target=worker_2, args=(i,)) for i in range(5)]

for t in threads:
    t.start()
for t in threads:
    t.join()

from printtrace import printtrace

def crash():
    printtrace("about to crash")
    raise RuntimeError("boom")

crash()

from printtrace import printtrace

printtrace("about to exit")
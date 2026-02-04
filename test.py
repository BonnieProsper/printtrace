import threading
from printtrace import printtrace

def worker(n):
    for i in range(3):
        printtrace(f"worker {n}", i)

threads = [threading.Thread(target=worker, args=(i,)) for i in range(5)]
for t in threads:
    t.start()
for t in threads:
    t.join()

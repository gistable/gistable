import array
import tracemalloc
from contextlib import contextmanager

@contextmanager
def tracemem(msg):
    tracemalloc.start()
    snapshot1 = tracemalloc.take_snapshot()
    yield
    snapshot2 = tracemalloc.take_snapshot()
    print(snapshot2.compare_to(snapshot1, 'lineno')[0])


def main():
    with tracemem('array'):
        a = array.array('Q', range(10000000))
    del a

    with tracemem('list'):
        l = list(range(10000000))
    del l


if __name__ == "__main__":
    '''
    Om my machine:
    python3 -X tracemalloc test_allocations.py
    test_allocations.py:16: size=78.1 MiB (+78.1 MiB), count=3 (+3), average=26.0 MiB
    test_allocations.py:20: size=353 MiB (+353 MiB), count=9999745 (+9999745), average=37 B
    '''
    main()
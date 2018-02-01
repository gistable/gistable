import time


n = range(50000)


def test_tuple():
    data = ()
    for i in n:
        data += (1, 2) + (3, 4)


def test_tuple2():
    data = []
    for i in n:
        data += list((1, 2)) + list((3, 4))


def test_list():
    data = []
    for i in n:
        data += [1, 2] + [3, 4]


def run(fn):
    start = time.time()
    fn()
    print(time.time() - start)


def bench():
    run(test_tuple)
    run(test_tuple2)
    run(test_list)
    print('-' * 30)


bench()
bench()
bench()
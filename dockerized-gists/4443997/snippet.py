def maybe(gen):
    it = gen()
    v = next(it)

    try:
        while v is not None:
            v = it.send(v)

    except StopIteration:
        return v


def test():
    @maybe
    def result():
        x = yield 1
        y = yield x * 2

        yield y * 3

    assert result == 6

    @maybe
    def result():
        x = yield None
        y = yield x * 2

        yield y * 3

    assert result is None


if __name__ == '__main__':
    test()

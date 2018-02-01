import time

j = range(100000)


def test_plus():
    out = ''
    for i in j:
        out += 'a'
    return out


def test_format():
    out = ''
    for i in j:
        out = '{0}{1}'.format(out, 'a')
    return out


def test_modulo():
    out = ''
    for i in j:
        out = '%s%s' % (out, 'a')
    return out


def bench(fn):
    start = time.time()
    fn()
    print(time.time() - start)


bench(test_plus)
bench(test_format)
bench(test_modulo)

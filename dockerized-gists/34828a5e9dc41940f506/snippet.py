
def test_z_interval(full=False):
    send, more, money = '0send', '0more', 'money'
    tuples = tuple(zip(send, more, money))
    all_chars = ('m', ) + tuple(sorted(set((send + more + money).replace('m', ''))))
    firsts = ('m', 's',)

    def v2int(t, val):
        r = 0
        for v in val:
            r = r * 10 + t[v]
        return r

    def rule1(t, a, b, c):
        s = t[a] + t[b]
        return t[c] in (s, s + 1, s - 10, s - 9)

    def rule2(t):
        return v2int(t, send) + v2int(t, more) == v2int(t, money)


    def walk(depth, t, r):
        if depth == 5:
            if rule2(t):
                yield t
        else:
            _all = True
            for sym in tuples[depth]:
                if not sym in t:
                    _all = False
                    t_ = t.copy()
                    for i in sorted(r):
                        if i == 0 and sym in ('m', 's'):
                            continue
                        t_[sym] = i
                        for res in walk(depth, t_, r - {i}):
                            yield res
            if _all and rule1(t, *tuples[depth]):
                for res in walk(depth + 1, t, r):
                    yield res

    if full:
        rs = []
        for t in walk(0, {'0': 0}, set(range(10))):
            rs.append((v2int(t, send), v2int(t, more), v2int(t, money)))
        return rs[0]
    else:
        for t in walk(0, {'0': 0}, set(range(10))):
            return v2int(t, send), v2int(t, more), v2int(t, money)


def test_freuser_ft_alex_2(full=False):
    def rang(c={1, 2, 3, 4, 5, 6, 7, 8, 9, 0}, sendmory=''):
        if len(sendmory)<8:
            for i in (c):
                if i==0 and (len(sendmory)==4 or len(sendmory)==0):
                    continue
                for res in rang(c-{i}, sendmory+str(i)):
                    yield res
        else:
            if int(sendmory[0:4])+int(sendmory[4:7]+sendmory[1])==int(sendmory[4:6]+sendmory[2]+sendmory[1]+sendmory[7]):
                yield (int(sendmory[0:4]), int(sendmory[4:7]+sendmory[1]), int(sendmory[4:6]+sendmory[2]+sendmory[1]+sendmory[7]))
    if full:
        rs = []
        for res in rang():
            rs.append((res))
        return rs[0]
    else:
        for res in rang():
            return res


def test_freuser_ft_alex_2_back(full=False):
    def rang(c={0, 9, 8, 7, 6, 5, 4, 3, 2, 1}, sendmory=''):
        if len(sendmory)<8:
            for i in (c):
                if i==0 and (len(sendmory)==4 or len(sendmory)==0):
                    continue
                for res in rang(c-{i}, sendmory+str(i)):
                    yield res
        else:
            if int(sendmory[0:4])+int(sendmory[4:7]+sendmory[1])==int(sendmory[4:6]+sendmory[2]+sendmory[1]+sendmory[7]):
                yield (int(sendmory[0:4]), int(sendmory[4:7]+sendmory[1]), int(sendmory[4:6]+sendmory[2]+sendmory[1]+sendmory[7]))
    if full:
        rs = []
        for res in rang():
            rs.append((res))
        return rs[0]
    else:
        for res in rang():
            return res


def test_freuser_ft_alex_3(full=False):
    def rang(c={1, 2, 3, 4, 5, 6, 7, 8, 9, 0}, msendory=''):
        depth = len(msendory)
        if depth == 0:
            for res in rang(c-{1}, msendory+str(1)):
                yield res
        if depth < 8:
            for i in (c):
                if i==0 and depth < 2:
                    continue
                for res in rang(c-{i}, msendory+str(i)):
                    yield res
        else:
            if int(msendory[1:5])+int(msendory[0]+msendory[5:7]+msendory[2])==int(msendory[0]+msendory[5]+msendory[3]+msendory[2]+msendory[7]):
                yield (int(msendory[1:5]), int(msendory[0]+msendory[5:7]+msendory[2]), int(msendory[0]+msendory[5]+msendory[3]+msendory[2]+msendory[7]))
    if full:
        rs = []
        for res in rang():
            rs.append((res))
        return rs[0]
    else:
        for res in rang():
            return res


def test_freuser_ft_alex_3_back(full=False):
    def rang(c={0, 9, 8, 7, 6, 5, 4, 3, 2, 1}, msendory=''):
        depth = len(msendory)
        if depth == 0:
            for res in rang(c-{1}, msendory+str(1)):
                yield res
        if depth < 8:
            for i in (c):
                if i==0 and depth < 2:
                    continue
                for res in rang(c-{i}, msendory+str(i)):
                    yield res
        else:
            if int(msendory[1:5])+int(msendory[0]+msendory[5:7]+msendory[2])==int(msendory[0]+msendory[5]+msendory[3]+msendory[2]+msendory[7]):
                yield (int(msendory[1:5]), int(msendory[0]+msendory[5:7]+msendory[2]), int(msendory[0]+msendory[5]+msendory[3]+msendory[2]+msendory[7]))
    if full:
        rs = []
        for res in rang():
            rs.append((res))
        return rs[0]
    else:
        for res in rang():
            return res


def test_dict(full=False):
    send, more, money = 'send', 'more', 'money'
    all_chars = ('m', ) + tuple(sorted(set((send + more + money).replace('m', ''))))
    firsts = ('m', 's',)

    def v2int(t, val):
        r = 0
        for v in val:
            r = r * 10 + t[v]
        return r

    def walk(chars, t):
        if not chars:
            if v2int(t, money) == v2int(t, send) + v2int(t, more):
                yield t
        else:
            sym, chars = chars[0], chars[1:]
            t_ = t.copy()
            nums = tuple(t.values())
            for i in range(10):
                if i in nums or i == 0 and sym in firsts:
                    continue
                t_[sym] = i
                for res in walk(chars=chars, t=t_):
                    yield res

    if full:
        rs = []
        for t in walk(all_chars, dict()):
            rs.append((v2int(t, send), v2int(t, more), v2int(t, money)))
        return rs[0]
    else:
        for t in walk(all_chars, dict()):
            return v2int(t, send), v2int(t, more), v2int(t, money)


def test_dict_str2int(full=False):
    send, more, money = 'send', 'more', 'money'
    all_chars = ('m', ) + tuple(sorted(set((send + more + money).replace('m', ''))))
    firsts = ('m', 's',)

    def v2int(t, val):
        return int(''.join(t[v] for v in val))

    all_nums = '1234568790'

    def walk(chars, t):
        if not chars:
            if v2int(t, money) == v2int(t, send) + v2int(t, more):
                yield t
        else:
            sym, chars = chars[0], chars[1:]
            t_ = t.copy()
            nums = tuple(t.values())
            for i in all_nums:
                if i in nums or i == '0' and sym in firsts:
                    continue
                t_[sym] = i
                for res in walk(chars=chars, t=t_):
                    yield res

    if full:
        rs = []
        for t in walk(all_chars, dict()):
            rs.append((v2int(t, send), v2int(t, more), v2int(t, money)))
        return rs[0]
    else:
        for t in walk(all_chars, dict()):
            return v2int(t, send), v2int(t, more), v2int(t, money)


class V():
    def __init__(self):
        self.v = -1


def test_obj(full=False):
    s, e, n, d, m, o, r, y = tuple(V() for _ in range(8))
    chars = m, s, e, n, d, o, r, y
    send, more, money = (s, e, n, d), (m, o, r, e), (m, o, n, e, y)

    def obj2int(val):
        res = 0
        for v in val:
            res = res * 10 + v.v
        return res

    def walk(depth = 0):
        # print('{} :: {}'.format(depth, [v() for v in chars]))
        if depth == len(chars):
            if obj2int(money) == obj2int(send) + obj2int(more):
                yield tuple(obj2int(x) for x in (send, more, money))
        else:
            char, left_chars = chars[depth], chars[:depth]
            for i in range(10):
                if i == 0 and depth < 2 or any(i == v.v for v in left_chars):
                    continue
                char.v = i
                for res in walk(depth=depth + 1):
                    yield res

    if full:
        rs = []
        for res in walk():
            rs.append((res))
        return rs[0]
    else:
        for res in walk():
            return res


def test_list(full=False):
    s, e, n, d, m, o, r, y = tuple([-1] for _ in range(8))

    chars   = m, s, e, n, d, o, r, y
    send    = s, e, n, d
    more    = m, o, r, e
    money   = m, o, n, e, y
    firsts  = m, s

    def idx2int(val):
        res = 0
        for v in val:
            res = res * 10 + v[0]
        return res

    def walk(depth = 0):
        # print('{} :: {}'.format(depth, [v[0] for v in chars]))
        if depth == len(chars):
            if idx2int(money) == idx2int(send) + idx2int(more):
                yield tuple(idx2int(x) for x in (send, more, money))
        else:
            char, left_chars = chars[depth], chars[:depth]
            for i in range(10):
                if i == 0 and depth < 2  or  any(i == v[0] for v in left_chars):
                    continue
                char[0] = i
                for res in walk(depth=depth + 1):
                    yield res

    if full:
        rs = []
        for res in walk():
            rs.append((res))
        return rs[0]
    else:
        for res in walk():
            return res


def test_list2(full=False):
    s, e, n, d, m, o, r, y = tuple([-1] for _ in range(8))
    all_chars   = m, s, e, n, d, o, r, y

    def calc_old():
        send = ((s[0] * 10 + e[0]) * 10 + n[0]) * 10 + d[0]
        more = ((m[0] * 10 + o[0]) * 10 + r[0]) * 10 + e[0]
        money = (((m[0] * 10 + o[0]) * 10 + n[0]) * 10 + e[0]) * 10 + y[0]
        return send, more, money

    def calc():
        send = ((s[0] * 10 + e[0]) * 10 + n[0]) * 10 + d[0]
        mo_e = (m[0] * 10 + o[0]) * 100 + e[0]
        more = mo_e + r[0] * 10
        money = (mo_e + n[0] * 10) * 10 + y[0]
        return send, more, money

    def walk(chars):
        # print('{} :: {}'.format(8 - len(chars), [v[0] for v in all_chars]))
        if not chars:
            send, more, money = calc()
            # print('{}'.format((send, more, money)))
            if send + more == money:
                yield send, more, money
        else:
            depth = 8 - len(chars)
            char, chars, left_chars = chars[0], chars[1:], all_chars[:depth]
            for i in range(10):
                if i == 0 and depth < 2  or  any(i == v[0] for v in left_chars):
                    continue
                char[0] = i
                for res in walk(chars=chars):
                    yield res

    if full:
        rs = []
        for res in walk(all_chars):
            rs.append((res))
        return rs[0]
    else:
        for res in walk(all_chars):
            return res


def do_tests():
    import sys
    import time
    self = sys.modules[__name__]
    tests = ((name, getattr(self, name))
             for name in sorted(dir(self)) if name.startswith('test_'))

    global mn, mx

    mn = 999999999., ''
    mx = 0., ''
    results = []

    class Profiler(object):

        def __init__(self, name):
            self._name = name

        def __enter__(self):
            self._startTime = time.time()

        def __exit__(self, type, value, traceback):
            global mn, mx
            if type is not None:
                return
            delta = time.time() - self._startTime
            results.append((delta, self._name))
            if mn[0] > delta:
                mn = delta, self._name
            if mx[0] < delta:
                mx = delta, self._name
            print("Elapsed time: {:.3f} sec\n".format(delta))

    test_times = 1
    args = tuple()

    print()
    print('{:>64}: {}'.format('Task', '{} + {} = {}'.format('send', 'more', 'money')))
    print('{:>64}: {}'.format(
        'Expected result', '{} + {} = {}'.format(9567, 1085, 10652)))
    print()

    for name, function in tests:
        try:
            with Profiler(name):
                print('{:<64}: {} + {} = {}'.format(name, *function(full=False)))
        except:
            print('{:<64}: {}'.format(name, 'FAILED'))
            raise

    print()
    for result in sorted(results, key=lambda x: x[0]):
        print('{:>8.3f} sec;   {}'.format(*result))

    print()
    print('{:<16}: {:>8.3f} sec;   {}'.format('Fastest', *mn))
    print('{:<16}: {:>8.3f} sec;   {}'.format('Slowest', *mx))


if __name__ == '__main__':
    do_tests()


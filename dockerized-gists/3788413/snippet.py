import io

class StringIteratorIO(io.TextIOBase):

    def __init__(self, iter):
        self._iter = iter
        self._left = ''

    def readable(self):
        return True
    
    def _read1(self, n=None):
        while not self._left:
            try:
                self._left = next(self._iter)
            except StopIteration:
                break
        ret = self._left[:n]
        self._left = self._left[len(ret):]
        return ret

    def read(self, n=None):
        l = []
        if n is None or n < 0:
            while True:
                m = self._read1()
                if not m:
                    break
                l.append(m)
        else:
            while n > 0:
                m = self._read1(n)
                if not m:
                    break
                n -= len(m)
                l.append(m)
        return ''.join(l)

    def readline(self):
        l = []
        while True:
            i = self._left.find('\n')
            if i == -1:
                l.append(self._left)
                try:
                    self._left = next(self._iter)
                except StopIteration:
                    self._left = ''
                    break
            else:
                l.append(self._left[:i+1])
                self._left = self._left[i+1:]
                break
        return ''.join(l)


def _str_iter():
    for a in range(100):
        yield str(a)*a

assert StringIteratorIO(_str_iter()).read() == ''.join(_str_iter())

for line in StringIteratorIO(_str_iter()):
    print(line)

f = StringIteratorIO(_str_iter())
print(f.read(5))
print(f.read(5))
print(f.read(5))
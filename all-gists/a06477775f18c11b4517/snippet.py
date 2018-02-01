import re

from ctypes import *
from nose.tools import *
from six import *
from unittest.mock import *

def ref_to_pointer(ref, ctype):
    '''convert byref() object to real pointer'''
    addr = int(re.search(r'(0x[\dabcdefABCDEF]+)',repr(ref)).group(1), 0)
    return cast(addr, POINTER(ctype))

class Libc:
    def __init__(self):
        self.libc = cdll.LoadLibrary(None)

    def puts(self, s):
        try:
            return self.libc.puts(s.encode())
        except AttributeError as e:
            if not isinstance(s, string_types):
                raise TypeError('a string is required')
            else:
                raise e

    def puti(self, i):
        return self.libc.printf(b'%i\n', c_int(i))

    def putf(self, f):
        return self.libc.printf(b'%f\n', c_float(f))

    def remquo(self, x, y):
        quo = c_double()
        rem = self.libc.remquo(x, y, byref(quo))
        return rem, quo.value

def test():

    libc = Libc()

    class MockReturn: pass

    with patch.object(libc.libc, 'puts', Mock(return_value=MockReturn)):
        assert_equal(libc.puts('testing'), MockReturn)
        assert_raises(TypeError, libc.puts, b'testing')
        assert_raises(TypeError, libc.puts, 1)
        assert_raises(TypeError, libc.puts, 3.1415)

    with patch.object(libc.libc, 'printf', Mock(return_value=MockReturn)):
        assert_equal(libc.puti(1), MockReturn)
        assert_raises(TypeError, libc.puti, 'testing')
        assert_raises(TypeError, libc.puti, b'testing')
        assert_raises(TypeError, libc.puti, 3.1415)

        assert_equal(libc.putf(3.1415), MockReturn)
        assert_equal(libc.putf(1), MockReturn)
        assert_raises(TypeError, libc.putf, 'testing')
        assert_raises(TypeError, libc.putf, b'testing')

    def mock_libc_remquo(x, y, quo):
        quo = ref_to_pointer(quo, c_double)
        quo[0] = 2
        return 1

    with patch.object(libc.libc, 'remquo', Mock(side_effect=mock_libc_remquo)):
        rem,quo = libc.remquo(1,2)
        assert_equal(rem,1)
        assert_equal(quo,2.0)

if __name__ == '__main__':
    test()

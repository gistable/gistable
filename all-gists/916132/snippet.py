"""Monads in Python, as close as I can get them to
Haskell
"""

class Monad(object):
    def return_(self, value):
        raise NotImplementedError()

    def __ge__(self, mf):
        raise NotImplementedError()

class Maybe(Monad):
    def __init__(self):
        super(Monad, self).__init__()
        
    @classmethod
    def return_(cls, value):
        return Just(value)


class Just(Maybe):
    def __init__(self, value):
        super(Maybe, self).__init__()
        self._value = value

    def __ge__(self, mf):
        return mf(self._value)

    def __repr__(self):
        return 'Just(%s)' % (repr(self._value))
    __str__ = __repr__


class _Nothing(Maybe):
    def __ge__(self, mf):
        return self

    def __repr__(self):
        return 'Nothing'
    __str__ = __repr__

Nothing = _Nothing()

if __name__ == '__main__':
    # 1. 
    # print Just(5) >= lambda x: Just(x + 5)) >= lambda x: Maybe.return_(x)
    #  File "monad.py", line 49
    #  print Just(5) >= lambda x: Just(x + 5)) >= lambda x: Maybe.return_(x)
    #                        ^
    # SyntaxError: invalid syntax

    # 2. 
    print Just(5) >= (lambda x: Just(x + 5)) >= (lambda x: Maybe.return_(x))
    # False --- ????
    
    # 3.
    print (Just(5) >= (lambda x: Just(x + 5))) >= (lambda x: Maybe.return_(x))
    # Just(10) --- Now we're on to something, but WTF?
    
    # 4.
    print (Nothing >= (lambda x: Just(x + 5))) >= (lambda x: Maybe.return_(x))
    # Nothing -- again, as expected, but with crazy loads of parens...

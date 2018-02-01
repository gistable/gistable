from functools import reduce, partial
from ast import literal_eval
from math import *

# make a function an infix operator
class infix:
    def __init__(self, f):
        self.f = f

    def __or__(self, other):
        return self.f(other)

    def __ror__(self, other):
        return infix(partial(self.f, other))

    def __call__(self, x, y):
        return self.f(x, y)


# make function composable
class compose:
    def __init__(self, f):
        self.f = f

    def __call__(self, *args, **kwargs):
        return self.f(*args, **kwargs)

    def __mul__(self, other):
        return compose(self._compose(other))

    def __lshift__(self, x):
    	return self.f(x)

    def _compose(self, g):
        return lambda *args, **kwargs: self.f(g(*args, **kwargs))


# curry and compose a function
def curry(x, argc=None):
    if argc is None:
        try:
            argc = x.__code__.co_argcount
        except AttributeError:
            # if x is a composable
            argc = x.f.__code__.co_argcount
    def p(*a):
        if len(a) == argc:
            return x(*a)
        def q(*b):
            return x(*(a + b))
        return curry(q, argc - len(a))
    return compose(p)


# functions to be redefined
_print, _range      = print, range
_filter, _map, _zip = filter, map, zip
_list, _str, _chr   = list, str, chr
_all,  _any         = all, any


# python
list   = compose (_list)
chr    = compose (_chr)
range  = compose (lambda a, b, s=1:
             list << _range(a, b+1, s) if isinstance (a, int)
                                       else map (chr) << _range (ord(a), ord(b)+1, s))

# Operators
add     = curry (lambda y, x: x + y)
sub     = curry (lambda y, x: x - y)
mult    = curry (lambda y, x: x * y)
quot    = infix (lambda x, y: x // y)
rem     = infix (lambda x, y: x % y)

# Tuples
fst = compose (lambda t: t[0])
snd = compose (lambda t: t[1])

# Higher order functions
map    = curry (lambda f, xs: list << _map (f, xs))
filter = curry (lambda f, xs: list << _filter (f, xs))
foldl  = curry (lambda f, xs: reduce (f, xs))
foldr  = curry (lambda f, xs: reduce (f, xs[::-1]))

# Miscellaneous
flip  = curry (lambda f, a, b: f (b, a))
id    = compose (lambda x: x)
const = compose (lambda x, _: x)
do    = lambda *x: any([x])

# Boolean
no  = compose (lambda x: not x)
ee  = curry (lambda x, y : x and y)
oo  = curry (lambda x, y : x or y)
all = curry (lambda xs: _all(xs))
any = curry (lambda xs: _any(xs))

# Numerical
even = compose (lambda x: x % 2 == 0)
odd  = no * even
gcd  = compose (lambda x, y,
           gcd_=lambda x, y: x if y == 0
                               else gcd (y, x |rem| y):
           gcd_ (abs(x), abs(y)))
lcm  = compose (lambda x, y: 0 if no (x or y)
                              else (x |quot| gcd (x, y))*2)

# List
head    = compose (lambda xs: xs[0])
last    = compose (lambda xs: xs[-1])
tail    = compose (lambda xs: xs[1:])
init    = compose (lambda xs: xs[0:-1])
null    = compose (lambda xs: len (xs) == 0)
length  = compose (len)
reverse = compose (lambda xs: xs[::-1])

# Special folds
sum     = compose (lambda xs: foldl (add, xs))
product = compose (lambda xs: foldl (mult, xs))
concat  = compose (lambda xs:
             (lambda r=[x for x in (x for x in xs)]:
                 ''.join(r) if isinstance(xs[0], str)
                            else r)())
concatMap = curry (lambda f, xs: concat << map (f) (xs))
maximum   = compose (lambda xs: max (xs))
minimum   = compose (lambda xs: min (xs))

# Building lists
scanl = curry (lambda f, z: add ([z]) * map (f (z)))
scanr = curry (lambda f, z: scanl (f, z) * reverse)

# Sublist
take      = curry (lambda n, xs: xs[:n])
drop      = curry (lambda n, xs: xs[n:])
splitAt   = curry (lambda n, xs: (xs[:n], xs[n:]))
takeWhile = curry (lambda p, xs:
                [] if no * p << head (xs)
                   else [head (xs)] + takeWhile (p) (tail (xs)))
dropWhile = curry (lambda p, xs:
                [] if null (xs)
                   else dropWhile (p) << tail (xs) if p << head (xs)
                        else xs)
span = curry (lambda p, xs:
            (xs, xs) if null (xs)
                     else ([], xs) if no * p << head (xs)
                                   else (lambda k = span (p, tail (xs)):
                                            ([head (xs)] ++ fst (k), snd (k))
                                        )())
break_ = curry (lambda p, xs: span (no * pi) (xs))

# Searching lists
elem    = curry (lambda x, xs: x in xs)
notElem = curry (no * elem)
lookup  = curry (lambda x, ks: ks.get(x))

# Zipping and unzipping lists
zip      = curry (lambda xs, ys: list << _zip (xs, ys))
zip3     = curry (lambda xs, ys, zs: list << _zip (xs, ys, zs))
zipWith  = curry (lambda f, xs, ys: list << _map (f, xs, ys))
zipWith3 = curry (lambda f, xs, ys, zs: list << _map (f, xs, ys, zs))
unzip    = compose (lambda xs: list << _zip(*xs))
unzip3   = unzip

# Functions on strings
lines   = compose (lambda x: x.split('\n'))
words   = compose (lambda x: x.split())
unlines = compose (lambda x: '\n'.join(x))
unwords = compose (lambda x: ' '.join(x))

# Converting to String
show = str

# Converting from String
read = compose (literal_eval)

# Output functions
putStr   = compose (lambda x: _print (x, end=""))
putStrLn = compose (lambda x: _print (x))
print    = putStrLn * show

# Input functions
getLine = compose (input)

main = do (
    print ("Is this Haskell?"),
    # Is this a let?
    (lambda n = mult (3) * product * filter (odd) * init << range (1, 10),
            k = 14 |quot| 3, # infix?
            e = lcm (620, 12):
        print << (n, k, e)
    )(),
    print * concat << range ('a', 'f'),
    print * scanl (mult, 2) * snd * splitAt (3) << range (10, 20),
    print * concatMap (add ("! ")) << ["hey", "hi", "what"],
    print << dropWhile (odd) ([1,3,5,8,11,12]),
    print << zip3 ([1,2,3], [4,5,6], [3,4,5]),

)

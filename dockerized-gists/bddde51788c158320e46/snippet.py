"""A sketch of parser combinators for Python.

I wanted to parse a recursive list of words with Python-like syntax, for
example:

    [foo, [bar, baz], quux]

Using an external library would have been too hard and complicated.
Unfortunately this didn't end up being very beautiful, either. Check out the
definition of wordlist(). Ugh.
"""

from collections import namedtuple

Success = namedtuple('Success', ['result', 'rest'])
Failure = namedtuple('Failure', ['message'])


# Character parsers

def satisfy(pred):
    def parse(s):
        if len(s) == 0:
            return Failure('Expecting character, got empty string')

        if pred(s[0]):
            return Success(s[0], s[1:])
        else:
            return Failure('Character "{}" failed predicate.'.format(s[0]))

    return parse


def char(c):
    return satisfy(lambda x: x == c)


def alpha():
    return satisfy(lambda s: s.isalpha())


# Parser combinators

def sep_by(p, sep):
    def parse(s):
        acc = []
        while True:
            r1 = p(s)
            r2 = then(r1, sep)

            if isinstance(r1, Success):
                acc.append(r1.result)
            elif len(acc) > 0:
                return r1
            else:
                return Success(acc, s)

            if isinstance(r2, Failure):
                return Success(acc, r1.rest)

            s = r2.rest

    return parse


def many(p):
    def parse(s):
        acc = []
        while True:
            r = p(s)
            if isinstance(r, Failure):
                return Success(acc, s)
            acc.append(r.result)
            s = r.rest
    return parse


def many1(p):
    def parse(s):
        r1 = p(s)
        r2 = then(r1, many(p))
        return fmap(r2, lambda x: [r1.result] + x)

    return parse


def alt(p, q):
    def parse(s):
        r = p(s)

        if isinstance(r, Failure):
            return q(s)
        else:
            return r

    return parse


# Monadic(?) combinators

def fmap(r, f):
    if isinstance(r, Success):
        return Success(f(r.result), r.rest)
    else:
        return r


def then(r, p):
    if isinstance(r, Success):
        return p(r.rest)
    else:
        return r


def sequence(*ps):
    def parse(s):
        r = Success(None, s)
        for p in ps:
            r = then(r, p)
        return r
    return parse


# Parsing word lists

def word():
    def parse(s):
        r = many1(alpha())(s)
        return fmap(r, lambda x: ''.join(x))
    return parse


def skip_space():
    return many(char(' '))


def space_comma():
    return sequence(skip_space(), char(','), skip_space())


def wordlist():
    def parse(s):
        r = char('[')(s)
        r_w = then(r, sep_by(alt(wordlist(), word()), space_comma()))
        r = then(r_w, char(']'))
        return then(r, lambda x: Success(r_w.result, x))
    return parse


# Using the parser

if __name__ == '__main__':
    parser = wordlist()
    print(parser('[foo, [bar, baz], quux]'))
    print(parser('[[[]]]'))
from itertools import ifilter


class Step(object):
    """Sequential step in nfa. for branch to continue, the match
    defined here must be successul at this point in the string."""

    __slots__ = 'match', 'nfa'

    def __init__(self, match, nfa=None):
        self.match = match
        self.nfa = nfa


class Split(object):
    """Fork in nfa, allowing for several possible outcomes."""

    __slots__ = 'left', 'right'

    def __init__(self, left=None, right=None):
        self.left = left
        self.right = right


class MatchEnd(object):
    """Element signifying end of nfa."""


def matches(string, nfa):
    states = [nfa]

    for x in string:
        states = ifilter(lambda s: s != MatchEnd, states)
        states = open_splits(states)
        states = advance_states(x, states)

    return any(state == MatchEnd for state in states)


def open_splits(states):
    for state in states:
        if type(state) == Split:
            yield state.left
            yield state.right
        else:
            yield state


def advance_states(char, states):
    for state in states:
        if type(state) == Step:
            if state.match == char:
                yield state.nfa
        else:
            yield state


# First let's define some simple patterns
p1 = Step('a', MatchEnd)                                        # a
p2 = Step('a', Step('b', MatchEnd))                             # ab
p3 = Step('a', Split(Step('b', MatchEnd), Step('c', MatchEnd))) # a(b|c)


# let's do some comparisons!
assert matches('a', p1)
assert not matches('aa', p1)
assert matches('ab', p2)
assert not matches('abc', p2)
assert not matches('aa', p2)


# Now for something more interesting.  As a regex, this would be: (abc)+
step1 = Step('a', Step('b'))
step2 = Split(Step('c', Split(Step('d', step1), step1)), MatchEnd)
step1.nfa.nfa = step2

p4 = step1

# Let's try it out!
assert matches('abc', p4)
assert matches('abcdabc', p4)

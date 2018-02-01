#!/usr/bin/env python3
"""Generate 1-dimensional automata based on various rules"""

def ngrams(iterable, n=1):
    """Generate ngrams from an iterable"""
    return zip(*(iterable[i:] for i in range(n)))

def states(state, rule, left_pad='0', right_pad='0'):
    """Generate a stream of states from an initial state and a rule"""
    next_state = ''.join(rule[''.join(window)] for window in ngrams(state, 3))
    padding = '{}{}{}'
    yield state, states(padding.format(left_pad, next_state, right_pad), rule)

def automata(state, rule, n):
    """Generate n generations given an initial state and a rule"""
    tail = states(state, rule)
    for _ in range(n):
        head, tail = next(tail)
        yield head

if __name__ == '__main__':
    SYMBOLS = '01'
    WIDTH = 80
    LEFT, RIGHT = (SYMBOLS[0] * (WIDTH // 2),) * 2
    GENERATIONS = 30
    # generate all possible 3 bit windows/keys
    keys = ['{:0>3b}'.format(i) for i in range(8)]
    # generate all possible bytes
    bytes_ = ['{:0>8b}'.format(i) for i in range(256)]
    # construct all 256 possible rule mappings of 3-bit keys to 1-bit values
    rules = [dict(zip(keys, byte)) for byte in bytes_]
    # define the seed state with a single bit activated in the middle
    initial_state = LEFT + SYMBOLS[1] + RIGHT
    # show the first 30 generations for each of the 256 rules
    label = 'rule #{}: {}'
    for i, rule in enumerate(rules, 1):
        print(label.format(i, rule))
        for state in automata(initial_state, rule, GENERATIONS):
            print(state)

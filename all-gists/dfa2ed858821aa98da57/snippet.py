#!/usr/bin/env python

"""calc.py: A concise prefix notation calculator."""

import regex  # pip install regex


def calc_eval(exp):
    """Evaluates the given prefix notation expression.
    Raises a SyntaxError if the input is not valid.
    """
    m = regex.match(r'\(([-+\/\*]) ((?R)) ((?R))\)|(\d+)|[-+\/\*]', exp)
    if not m:
        raise SyntaxError('Not well formed')
    if all(map(m.group, [1, 2, 3])):  # exp is a procedure call
        return eval(' '.join([str(calc_eval(m.group(i))) for i in [2, 1, 3]]))
    return eval(exp) if m.group(4) else exp  # exp is a number / an operator


""" Run from command line for REPL mode. """
if __name__ == '__main__':
    while True:
        print calc_eval(raw_input('> '))

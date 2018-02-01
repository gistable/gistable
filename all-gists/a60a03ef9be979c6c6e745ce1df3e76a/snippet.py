#!/usr/bin/env python3
"""
This module will build truth tables from logic expressions. It is intended to
be used with the Python REPL.
"""
import abc
import itertools
import random
import sys

class BaseProposition:
    def __and__(self, other):
        return AndProposition(self, other)

    def __or__(self, other):
        return OrProposition(self, other)

    def __invert__(self):
        return NotProposition(self) 

    def __gt__(self, other):
        return ImplProposition(self, other)

    def __lt__(self, other):
        return ImplProposition(other, self)

    def __eq__(self, other):
        return EquivProposition(self, other)

    def truth_table(self, out=True):
        propositions = sorted(self.propositions(), key=lambda p: str(p))
        components = self.components()
        permutations = itertools.product([False, True], repeat=len(propositions))
        table = {}
        for permutation in permutations:
            proposition_values = {
                p: v
                for p, v in zip(propositions, permutation)
            }
            result = self.compute(proposition_values)
            for p, v in result.items():
                if p in table:
                    table[p].append(v)
                else:
                    table[p] = [v]
        return table

class Proposition(BaseProposition):
    priority = 0

    def __init__(self, name):
        self._str = name
        self._hash = random.randint(-sys.maxsize - 1, sys.maxsize)
        self.order = 0

    def propositions(self):
        return set([self])

    def compute(self, propositions):
        return {
            self: propositions[self]
        }

    def components(self):
        return set([self])

    def __str__(self):
        return self._str

    def __hash__(self):
        return self._hash

def make_proposition_connector2(compute, priority_, pretty):
    class GenProposition2(BaseProposition):
        priority = priority_

        def __init__(self, left, right):
            self._str = pretty(left, right)
            self._hash = random.randint(-sys.maxsize - 1, sys.maxsize)
            self.left = left
            self.right = right
            self.order = max(left.order, right.order) + 1

        def propositions(self):
            return self.left.propositions() | self.right.propositions()

        def compute(self, propositions):
                res = {}
                res.update(self.left.compute(propositions))
                assert self.left in res
                res.update(self.right.compute(propositions))
                assert self.right in res
                res.update({
                    self: compute(res[self.left], res[self.right])
                })
                return res

        def components(self):
            return set([self]) | self.left.components() | self.right.components()

        def __str__(self):
            return self._str

        def __hash__(self):
            return self._hash
    return GenProposition2

class NotProposition(BaseProposition):
    priority = 1

    def __init__(self, operand):
        self._str = '¬{}'.format(str(operand))
        self._hash = random.randint(-sys.maxsize - 1, sys.maxsize)
        self.operand = operand
        self.order = operand.order + 1

    def propositions(self):
        return self.operand.propositions()

    def compute(self, propositions):
        res = self.operand.compute(propositions)
        assert self.operand in res
        res.update({
            self: not res[self.operand]
        })
        return res

    def components(self):
        return set([self]) | self.operand.components()

    def __str__(self):
        return self._str

    def __hash__(self):
        return self._hash

AndProposition = make_proposition_connector2(
    (lambda a, b: a and b),
    2,
    '({} ∧ {})'.format,
)

OrProposition = make_proposition_connector2(
    (lambda a, b: a or b),
    3,
    '({} ∨ {})'.format,
)

ImplProposition = make_proposition_connector2(
    (lambda a, b: b or not a),
    4,
    '({} => {})'.format,
)

EquivProposition = make_proposition_connector2(
    (lambda a, b: a == b),
    4,
    '({} <=> {})'.format,
)

def pretty_truth_table(table, box=True):
    dummy = table[list(table.keys())[0]]
    l = len(dummy)
    primaries = sorted(
        (p for p in table if isinstance(p, Proposition)),
        key=lambda p: str(p),
    )
    secondaries = sorted(
        (p for p in table if not isinstance(p, Proposition)),
        key=lambda p: p.order,
    )
    print('┌─' + '──' * l + '┬───╴' if box else
          '+-' + '--' * l + '+----')
    for p in primaries:
        print(('│ {} │ {}' if box else '| {} | {}').format(
            ' '.join(str(int(v)) for v in table[p]),
            str(p),
        ))
    print('├┄' + '┄┄' * l + '┼┄┄┄╴' if box else
          '+-' + '--' * l + '+----')
    for p in secondaries:
        print(('│ {} │ {}' if box else '| {} | {}').format(
            ' '.join(str(int(v)) for v in table[p]),
            str(p),
        ))
    print('└─' + '──' * l + '┴───╴')

def T(proposition):
    pretty_truth_table(proposition.truth_table())

p = Proposition('p')
q = Proposition('q')
r = Proposition('r')
s = Proposition('s')
t = Proposition('t')

print("""Truth Table Generator by Victor Schubert

Run interactively with `python3 -i ttg.py`.

Use T(statement) to generate a truth table. For example:
>>> T(p & q | r)

Supported operators:
  &  AND
  |  OR
  >  IMPLICATION
  <  IMPLICATION
 ==  EQUIVALENCE
  ~  NEGATION

Known issues:
 - Some associativity issues with implication and equivalence. Use parentheses
   with these.
""")

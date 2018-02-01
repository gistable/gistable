# Simple implementation of proving/disproving implicational statements

# https://github.com/louisswarren/pyutil
# from util import *
accumulate = lambda t: lambda f: lambda *a, **k: t(iter(f(*a, **k)))

# String constants

lBOT = '⊥'
lNEG = '¬'
lIMP = ' → '
lMMP = ' ⇒ '
lNVD = ' ⊬ '



# Helper functions

def paren(obj):
    if is_atom(obj) or obj.conclusion is bot:
        return str(obj)
    return '({})'.format(obj)

def is_atom(prop):
    return isinstance(prop, Atom)

def is_impl(prop):
    return isinstance(prop, Impl)

def is_simp(prop):
    return is_impl(prop) and is_atom(prop.premise)

def is_left(prop):
    return is_impl(prop) and is_impl(prop.premise)

def strset(iterable):
    return '{' + ', '.join(map(str, sorted(iterable))) + '}'



# Formula types

class Prop:
    # Warning: not right-associative
    def __rshift__(self, shift):
        return Impl(self, shift)

    def __invert__(self):
        return Impl(self, bot)

    def __lt__(self, other):
        return str(self) < str(other)


class Atom(Prop):
    @constructor
    def __init__(self, name):
        pass

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name

    @accumulate(all)
    def __eq__(self, other):
        yield is_atom(other)
        yield self.name == other.name

    def __hash__(self):
        return hash(self.name)

bot = Atom(lBOT)
A = Atom('A')
B = Atom('B')
C = Atom('C')
D = Atom('D')
P = Atom('P')
Q = Atom('Q')
R = Atom('R')


class Impl(Prop):
    @constructor
    def __init__(self, premise, conclusion):
        pass

    def __repr__(self):
        if self.conclusion is bot:
            return lNEG + paren(self.premise)
        return paren(self.premise) + lIMP + paren(self.conclusion)

    @accumulate(all)
    def __eq__(self, other):
        yield is_impl(other)
        yield self.premise == other.premise
        yield self.conclusion == other.conclusion

    def __hash__(self):
        return hash((self.premise, self.conclusion))



# Trees

class Tree:
    @constructor
    def __init__(self, labels, successors={}, utility=''):
        self.depth = -1
        self.inc_depth()


    def inc_depth(self):
        self.depth += 1
        for s in self.successors:
            s.inc_depth()

    def __lt__(self, other):
        order = lambda x: str(min(x.labels, default=''))
        return order(self) < order(other)

    @accumulate(all)
    def __eq__(self, other):
        yield isinstance(other, Tree)
        yield self.labels == other.labels
        yield self.successors == other.successors

    def __hash__(self):
        return hash((tuple(sorted(self.labels)), tuple(sorted(self.successors))))


    @accumulate(''.join)
    def __str__(self):
        r = ''
        if self.depth > 0:
            r += '    ' * (self.depth - 1)
            r += '  \- '
        else:
            yield 'Tree:\n'
            r += ' '
        r += strset(self.labels)
        if self.utility:
            r += ' '*(72 - len(r) - len(self.utility)) + self.utility
        yield r + '\n'
        yield from map(str, sorted(self.successors))



# Proof search

@accumulate(set)
def reduction_step(propset):
    for x in propset:
        if is_impl(x) and x.premise in propset:
            yield x.conclusion
        else:
            yield x

# Returns a tuple (deduction_list, kripke_model). The latter may be None.
def prove(premises, conclusion, level=0):
    deductions = []
    log = lambda msg: deductions.append((level, msg))
    log('Proving {} {} {}'.format(strset(premises), lMMP, conclusion))

    # Restate so that the conclusion is a single atom
    if is_impl(conclusion):
        while is_impl(conclusion):
            premises = premises.union({conclusion.premise})
            conclusion = conclusion.conclusion
        log('Restate as {} {} {}'.format(strset(premises), lMMP, conclusion))

    # Reduce premises using modus ponens
    prev_gamma = premises
    gamma = reduction_step(prev_gamma.copy())
    while gamma != prev_gamma:
        log('Reduced {} to {}'.format(strset(prev_gamma), strset(gamma)))
        prev_gamma = gamma
        gamma = reduction_step(prev_gamma.copy())
    if gamma != premises:
        log('Reduct: {} {} {}'.format(strset(gamma), lMMP, conclusion))

    # Check if goal has been reached
    if conclusion in gamma:
        log('Found {} in assumptions'.format(conclusion))
        return deductions, None

    # Try proving premises of nested implications in the premise set
    nested = set(filter(is_left, gamma))
    atoms = set(filter(is_atom, gamma))
    if not nested:
        log('Halting: no more deductions possible')
        utility = strset(atoms) + lNVD + str(conclusion)
        return deductions, Tree(atoms, utility=utility)
    counter_models = set()
    all_nested_had_countermodels = True
    for formula in sorted(nested):
        fp_de, fp_cm = prove(gamma - {formula}, formula.premise, level + 1)
        deductions += fp_de
        if fp_cm is not None:
            counter_models.add(fp_cm)
        else:
            gamma.remove(formula)
            gamma.add(formula.conclusion)
            all_nested_had_countermodels = False

    # If all premises of nested implications are unprovable, we are stuck
    if all_nested_had_countermodels:
        utility = strset(atoms) + lNVD + strset(f.premise for f in nested)
        return deductions, Tree(set(), counter_models, utility=utility)

    # At least one nested premise has been reduced
    subproof = prove(gamma, conclusion, level)
    return deductions + subproof[0], subproof[1]


def proof_wrapper(premise, conclusion):
    print('\n' * 4)
    print('='*72)
    print("Proving", strset(premise), lMMP, conclusion)
    print('-'*72)
    proof_deductions, proof_model = prove(premise, conclusion)
    level_counter = {}
    for level, line in proof_deductions:
        level_counter[level] = level_counter.get(level, 0) + 1
        print('    '*level + '{:>4} {} '.format(level_counter[level], line))
        for lv in level_counter:
            if lv > level:
                level_counter[lv] = 0
    print()
    if proof_model:
        print("Not derivable, by countermodel:")
        print(proof_model, end='')
    else:
        print("Proved")
    print('-'*72)
    return proof_deductions, proof_model

def prover(statement):
    return proof_wrapper(set(), statement)



# Testing

if __name__ == '__main__':
    prover((A >> (B >> C)) >> ~~(~(A >> C) >> ~~~~(B >> C)))
    prover((~~A >> B) >> ~~(A >> B))


# ========================================================================
# Proving {}  ⇒  (A → (B → C)) → ¬¬(¬(A → C) → ¬¬¬¬(B → C))
# ------------------------------------------------------------------------
#    1 Proving {}  ⇒  (A → (B → C)) → ¬¬(¬(A → C) → ¬¬¬¬(B → C))
#    2 Restate as {A → (B → C), ¬(¬(A → C) → ¬¬¬¬(B → C))}  ⇒  ⊥
#        1 Proving {A → (B → C)}  ⇒  ¬(A → C) → ¬¬¬¬(B → C)
#        2 Restate as {A → (B → C), ¬(A → C), ¬¬¬(B → C)}  ⇒  ⊥
#            1 Proving {A → (B → C), ¬¬¬(B → C)}  ⇒  A → C
#            2 Restate as {A, A → (B → C), ¬¬¬(B → C)}  ⇒  C
#            3 Reduced {A, A → (B → C), ¬¬¬(B → C)} to {A, B → C, ¬¬¬(B → C)}
#            4 Reduct: {A, B → C, ¬¬¬(B → C)}  ⇒  C
#                1 Proving {A, B → C}  ⇒  ¬¬(B → C)
#                2 Restate as {A, B → C, ¬(B → C)}  ⇒  ⊥
#                3 Reduced {A, B → C, ¬(B → C)} to {A, B → C, ⊥}
#                4 Reduct: {A, B → C, ⊥}  ⇒  ⊥
#                5 Found ⊥ in assumptions
#            5 Proving {A, B → C, ⊥}  ⇒  C
#            6 Halting: no more deductions possible
#            7 Proving {A → (B → C), ¬(A → C)}  ⇒  ¬¬(B → C)
#            8 Restate as {A → (B → C), ¬(A → C), ¬(B → C)}  ⇒  ⊥
#                1 Proving {A → (B → C), ¬(B → C)}  ⇒  A → C
#                2 Restate as {A, A → (B → C), ¬(B → C)}  ⇒  C
#                3 Reduced {A, A → (B → C), ¬(B → C)} to {A, B → C, ¬(B → C)}
#                4 Reduced {A, B → C, ¬(B → C)} to {A, B → C, ⊥}
#                5 Reduct: {A, B → C, ⊥}  ⇒  C
#                6 Halting: no more deductions possible
#                7 Proving {A → (B → C), ¬(A → C)}  ⇒  B → C
#                8 Restate as {A → (B → C), B, ¬(A → C)}  ⇒  C
#                    1 Proving {A → (B → C), B}  ⇒  A → C
#                    2 Restate as {A, A → (B → C), B}  ⇒  C
#                    3 Reduced {A, A → (B → C), B} to {A, B, B → C}
#                    4 Reduced {A, B, B → C} to {A, B, C}
#                    5 Reduct: {A, B, C}  ⇒  C
#                    6 Found C in assumptions
#                9 Proving {A → (B → C), B, ⊥}  ⇒  C
#               10 Halting: no more deductions possible
#
# Not derivable, by countermodel:
# Tree:
#  {}                                        {} ⊬ {¬(A → C) → ¬¬¬¬(B → C)}
#   \- {}                                          {} ⊬ {A → C, ¬¬(B → C)}
#       \- {}                                          {} ⊬ {A → C, B → C}
#           \- {A, ⊥}                                           {A, ⊥} ⊬ C
#           \- {B, ⊥}                                           {B, ⊥} ⊬ C
#       \- {A, ⊥}                                               {A, ⊥} ⊬ C
# ------------------------------------------------------------------------
#
#
#
#
#
# ========================================================================
# Proving {}  ⇒  (¬¬A → B) → ¬¬(A → B)
# ------------------------------------------------------------------------
#    1 Proving {}  ⇒  (¬¬A → B) → ¬¬(A → B)
#    2 Restate as {¬(A → B), ¬¬A → B}  ⇒  ⊥
#        1 Proving {¬¬A → B}  ⇒  A → B
#        2 Restate as {A, ¬¬A → B}  ⇒  B
#            1 Proving {A}  ⇒  ¬¬A
#            2 Restate as {A, ¬A}  ⇒  ⊥
#            3 Reduced {A, ¬A} to {A, ⊥}
#            4 Reduct: {A, ⊥}  ⇒  ⊥
#            5 Found ⊥ in assumptions
#        3 Proving {A, B}  ⇒  B
#        4 Found B in assumptions
#        5 Proving {⊥}  ⇒  ¬¬A
#        6 Restate as {¬A, ⊥}  ⇒  ⊥
#        7 Found ⊥ in assumptions
#    3 Proving {B, ⊥}  ⇒  ⊥
#    4 Found ⊥ in assumptions
#
# Proved
# ------------------------------------------------------------------------
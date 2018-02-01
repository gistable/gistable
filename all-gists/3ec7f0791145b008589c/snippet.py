# Examples:
#
# from qcombinator import q
# q.add(3) # is equivalent to: (lambda doc: doc.add(3))
# q.add(3).eq(4) -> (lambda doc: doc + 3 == 4)
# q.add(3).eq(4).or_('Dang!') -> (lambda doc: r.or_(doc + 3 == 4, 'Dang!'))
# q(3) -> r.expr(3)
# r.table('A').map(q.obj('ok')) -> r.table('A').map(lambda doc: {'ok': doc})

import sys
import types
import rethinkdb as r


class QCombinator(object):

    def __init__(self, lambd=(lambda x: r.expr(x))):
        self.lambd = lambd
        # This is to trick ReQL function inspection when it creates
        # the AST. You can't subclass types.FunctionType
        # unfortunately, so emulating them is the best we can do
        self.func_code = lambd.func_code
        self.__doc__ = lambd.__doc__

    def __call__(self, *args):
        return self.lambd(*args)
        
    def __getitem__(self, key):
        return QC(lambda x: self.lambd(x)[key])

    def const(self, a):
        '''Function which ignores its second argument and returns the first'''
        return QC(lambda b: a)

    def add(self, a):
        '''curried version of r.add'''
        return QC(lambda b: self.lambd(b).add(a))

    def sub(self, a):
        '''Curried version of r.sub'''
        return QC(lambda b: self.lambd(b).sub(a))

    def div(self, a):
        '''Curried version of r.div'''
        return QC(lambda b: self.lambd(b).div(a))

    def mul(self, a):
        '''Curried version of r.mul'''
        return QC(lambda b: self.lambd(b).mul(a))

    def branch(self, test, true_branch, false_branch):
        '''composed version of r.branch. Test, and both branches are required
        to be functions of one argument (the current stream)'''
        def _branch(doc):
            value = self.lambd(doc)
            return r.branch(test(value), true_branch(value), false_branch(value))
        return QC(_branch)

    def obj(self, key):
        '''Promotes the composed value into an object with the given key'''
        return QC(lambda val: {key: self.lambd(val)})

    def merge(self, mergefun):
        '''Composed version of merge'''
        return QC(lambda doc: r.expr(self.lambd(doc)).merge(mergefun))

    def and_(self, a):
        '''curried version of r.and_ (accepts only 2 arguments)'''
        return QC(lambda b: r.and_(b, a))

    def or_(self, a):
        '''curried version of r.or_ (accepts only 2 arguments)'''
        return QC(lambda b: r.or_(b, a))

    def contains(self, a):
        '''curried version of contains (accepts only 1 argument)'''
        return QC(lambda doc: self.lambd(doc).contains(a))

    def match(self, regex):
        '''curried version of match'''
        return QC(lambda doc: self.lambd(doc).match(a))

    def split(self, spliton):
        return QC(lambda doc: r.expr(self.lambd(doc)).split(spliton))

    def eq(self, other):
        '''curries version of eq'''
        return QC(lambda doc: self.lambd(doc).eq(other))

    def lt(self, other):
        '''curried version of lt'''
        return QC(lambda doc: self.lambd(doc).lt(other))

    def le(self, other):
        '''curried version of le'''
        return QC(lambda doc: self.lambd(doc).le(other))

    def gt(self, other):
        '''curried version of gt'''
        return QC(lambda doc: self.lambd(doc).gt(other))

    def ge(self, other):
        '''curried version of ge'''
        return QC(lambda doc: self.lambd(doc).ge(other))


QC = QCombinator
q = QCombinator()

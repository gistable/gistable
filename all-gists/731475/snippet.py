#!/usr/bin/env python

import sys
import types
import operator

class Runtime:
    def __init__(self, env={}, stack=[]):
        self.env = {
            # Primitive words, not an impressive base but it works
            '.':     lambda s,r: sys.stdout.write(repr(s.pop()) + "\n"),
            '+':     lambda s,r: self._math(s, operator.add),
            '-':     lambda s,r: self._math(s, operator.sub),
            '*':     lambda s,r: self._math(s, operator.mul),
            '/':     lambda s,r: self._math(s, operator.div),
            'mod':   lambda s,r: self._math(s, operator.mod),
            '>':     lambda s,r: self._math(s, operator.gt),
            '<':     lambda s,r: self._math(s, operator.lt),
            '=':     lambda s,r: self._math(s, operator.eq),
            'f':     lambda s,r: s.append(False),
            'not':   lambda s,r: s.append(not s.pop()),
            'drop':  lambda s,r: s.pop(),
            'dup':   lambda s,r: s.append(s[-1]),
            'swap':  self._swap,
            'over':  lambda s,r: s.append(s[-2]),
            'clear': self._clear,
            'quote': lambda s,r: s.append(list(s.pop())),
            'call':  self._call,            
            'r>':    lambda s,r: r.append(s.pop()),
            '>r':    lambda s,r: s.append(r.pop()),
            '?':     self._which,
            'curry': self._curry,
            # Non-primitive words -- in essence, the prelude
            'dip':   ['swap', 'r>', 'call', '>r'],
            'if':    ['?', 'call'],
            'when':  ['swap', ['call'], ['drop'], 'if'],
            'keep':  ['over', ['call'], 'dip'],
            'loop':  [['call'], 'keep', ['loop'], 'curry', 'when']
        }
        self.env.update(env)
        self.stack = stack
        self.frames = [] # Fudge of Factor's callstack
        self.retain = [] # The retain stack, for >r and r>

    def _swap(self, stack, retain):
        stack[-1], stack[-2] = stack[-2], stack[-1]

    def _clear(self, stack, retain):
        del stack[:]

    def _which(self, stack, retain):
        falseq = stack.pop()
        trueq = stack.pop()
        stack.append(trueq if stack.pop() else falseq)

    def _curry(self, stack, retain):
        quot = stack.pop()[:]
        quot.insert(0, stack.pop())
        stack.append(quot)

    def _call(self, stack, retain):
        if self.ptr < len(self.nodes) - 1:
            self.frames.append((self.nodes, self.ptr + 1))
        self.ptr, self.nodes = -1, self.stack.pop()

    def _math(self, stack, func):
        rhs = stack.pop()
        lhs = stack.pop()
        stack.append(func(lhs, rhs))

    def evaluate(self, nodes):
        self.nodes = nodes
        self.retain, self.frames, self.ptr = [], [], 0
        while True:
            try:
                node = self.nodes[self.ptr]
                # Strings are words, so a lookup is attempted.
                if isinstance(node, str):
                    # Check if the word is defined in the environment.
                    if self.env.has_key(node):
                        defn = self.env[node]
                        # Python lists in the environment are quotations.
                        # They are from the prelude, or they are user-defined words.
                        if isinstance(defn, list):
                            # A call frame is only saved if the word being called
                            # is not the last word in the quotation.
                            # Tail-call optimization achieved. :)
                            if self.ptr < len(self.nodes) - 1:
                                self.frames.append((self.nodes, self.ptr + 1))
                            self.ptr, self.nodes = -1, defn
                        else:
                            defn(self.stack, self.retain)
                    # To keep with Factor syntax, the : word-name definition... ;
                    # design choice was made. It would be entirely possible to
                    # have definitions be postfix as well, and probably more
                    # consistent with the implementation.
                    elif ':' == node:
                        name = self.nodes[self.ptr + 1]
                        body = []
                        self.ptr += 2
                        # Build a quotation until ; word is found, and add it to
                        # the environment.
                        while self.nodes[self.ptr] != ';':
                            body.append(self.nodes[self.ptr])
                            self.ptr += 1
                        self.env[name] = body
                    else:
                        raise NameError, "word %s not defined" % node
                else:
                    self.stack.append(node)
                self.ptr += 1
            # End of quotation reached, so pop off the call frame and
            # start from there.
            except IndexError:
                try:
                    (self.nodes, self.ptr) = self.frames.pop()
                # No more call frames. Program is terminated.
                except IndexError:
                    return self.stack
        return self.stack

def read(s):
    return parse(tokenize(s))

def tokenize(s):
    return s.split()
    
def parse(tokens, depth=0):
    program = []
    if len(tokens) == 0:
        return program
    while len(tokens) > 0:
        token = tokens.pop(0)
        if '[' == token:
            program.append(parse(tokens))
        elif ']' == token:
            return program
        else:
            program.append(atom(token))
    return program

def atom(token):
    "Numbers become numbers; every other token is a symbol."
    try: return int(token)
    except ValueError:
        try: return float(token)
        except ValueError:
            return str(token)

def repl():
    runtime = Runtime()
    while True:
        result = runtime.evaluate(read(raw_input("> ")))
        print "-- data stack --"
        print "\n".join(map(lambda el: repr(el), result))

if __name__ == '__main__':
    repl()

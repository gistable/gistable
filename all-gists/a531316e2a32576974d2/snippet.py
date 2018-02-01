import operator
import re

def pairs(l):
    return zip(l[::2], l[1::2])

def vm(ops, env={}):
    class closure:
        def __init__(self, pc, env): self.pc, self.env = pc, env
    def popn(n):
        if len(stack) < n: print 'not enough elements for pop: %d needed, %d left' % (n, len(stack))
        top = stack[-n:]
        stack[-n:] = []
        return top
    pc, stack, fstack = 0, [], []
    labels = {op[1]: index for index, op in enumerate(ops) if op[0] == 'label'}
    while pc < len(ops):
        op, args, pc = ops[pc][0], ops[pc][1:], pc + 1
        arg = args[0] if args else None
        if op == 'label':
            pass
        elif op == 'val':
            stack.append(arg)
        elif op == 'fn':
            stack.append(closure(labels[arg], env))
        elif op == 'set' or op == 'get':
            e = env
            while e is not None and arg not in e:
                e = e[''] if '' in e else None
            if op == 'set': (env if e is None else e)[arg] = stack.pop()
            elif op == 'get':
                if e: stack.append(e[arg])
                else: print('undefined variable %s' % arg)
        elif op == 'arr':
            stack.append(popn(arg))
        elif op == 'map':
            stack.append(dict(pairs(popn(arg * 2))))
        elif op == 'call' or op == 'tcall':
            fn = stack.pop()
            if args and arg:
                stack.append(popn(arg))
            if isinstance(fn, closure):
                if op == 'call':
                    fstack.append((pc, env))
                pc, env = fn.pc, {'': fn.env}
            elif hasattr(fn, '__call__'):
                stack.append(fn(stack.pop()))
        elif op == 'args':
            vals = stack.pop()
            if len(args) != len(vals): print 'warning: wrong arguments count: %d expected, %d given' % (len(args), len(vals))
            env.update(dict(zip(args, vals)))
        elif op == 'ret':
            if not fstack: break
            pc, env = fstack.pop()
        elif op == 'jmp':
            pc = labels[arg]
        elif op == 'jmpf':
            if not stack.pop(): pc = labels[arg]

def puts(args): print ' '.join(map(str, args))
def mul(args): return reduce(operator.mul, args, 1)
def unary(fn): return lambda args: fn(args[0])
def binary(fn): return lambda args: fn(args[0], args[1])
def proxy(fn): return lambda args: fn(*args)
genv = {
    'puts': puts,
    '+': sum,
    '-': lambda a: -a[0] if len(a) == 1 else a[0] - sum(a[1:]),
    '*': mul,
    '/': lambda a: 1 / a[0] if len(a) == 1 else a[0] / mul(a[1:]),
    'int': unary(int),
    'real': unary(float),
    'str': unary(str),
    'zip': proxy(zip),
    '<': binary(operator.lt),
}

def lex(text):
    sym = r'[\w+\-*/=<>]+'
    toks = (
        r';.*?\n\s*',
        lambda m: None,
        r'-?(\d+)?\.\d+(e-?\d+)?\s*',
        lambda m: ['val', float(m.group(0))],
        r'-?\d+\s*',
        lambda m: ['val', int(m.group(0))],
        r"'((?:[^'\\]|\\.)*)'\s*",
        lambda m: ['val', m.group(1)],
        r'([@#])(\d+)\s*',
        lambda m: [{'@': 'arr', '#': 'map'}[m.group(1)], int(m.group(2))],
        r'~(~?)(\d*)\s*',
        lambda m: ['tcall' if m.group(1) else 'call'] + ([int(m.group(2))] if m.group(2) else []),
        r'\.(%s)?\s*' % sym,
        lambda m: ['label', m.group(1)] if m.group(1) else ['ret'],
        r'([%%$=!?])(%s)\s*' % sym,
        lambda m: [{'=': 'set', '$': 'get', '%': 'fn', '!': 'jmp', '?': 'jmpf'}[m.group(1)], m.group(2)],
        r':(%s(:?,%s)*)\s*' % (sym, sym),
        lambda m: ['args'] + m.group(1).split(',')
    )
    compiled = [(re.compile(regex), action) for regex, action in pairs(toks)]
    pos = 0
    text = text.strip()
    while pos < len(text):
        for regex, action in compiled:
            m = regex.match(text, pos)
            if m:
                pos += len(m.group(0))
                tok = action(m)
                if tok: yield tok; break
        else:
            print('illegal character %s' % repr(text[pos]))
            pos += 1

code = '''
!main

.make-person :name,age
    %person
.

.person
    'Hello! My name is' $name 'and Im' $age 'years old!' $puts ~5
    $age 1 $+ ~2 =age
.

.main
    'Butjok' 24 %make-person ~2 =butjok
    'Joe' 32 %make-person ~2 =joe
    $butjok ~
    $butjok ~
    $butjok ~
    $joe ~
    $joe ~
'''
# print(list(lex(code)))
vm(list(lex(code)), genv)
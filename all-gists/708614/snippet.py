#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, traceback, re
from fractions import Fraction


nil = type('Nil', (), {'__str__': lambda self: '()'})()
undef = type('Undef', (), {'__str__': lambda self: '#<undef>'})()
f = type('F', (), {'__str__': lambda self: '#f'})()
t = type('T', (), {'__str__': lambda self: '#t'})()
eof = type('Eof', (), {})

class Cell:

    def __init__(self, car=nil, cdr=nil):
        self.car = car
        self.cdr = cdr

    def __str__(self):
        s = '(' + str(self.car)
        cell = self.cdr
        while not cell == nil:
            if isinstance(cell, Cell):
                s += ' ' + str(cell.car)
                cell = cell.cdr
            else:
                s += ' . {0}'.format(cell)
                break
        return s+')'

    def __eq__(self, x):
        if x is nil:
            return self.car is nil and self.cdr is nil
        elif isinstance(x, Cell):
            return self.car == x.car and self.cdr == x.cdr
        else:
            return False
    
class Symbol:

    def __init__(self, exp):
        self.exp = exp

    def __str__(self):
        return self.exp

    def __eq__(self, x):
        return self.exp == x

    def __hash__(self):
        return hash(self.exp)

class Syntax:

    def __init__(self, proc):
        self.proc = proc

    def __str__(self):
        return '#<syntax>'

class Primitive:

    def __init__(self, proc):
        self.proc = proc

    def __str__(self):
        return '#<primitive>'

class Closure:

    def __init__(self, exp, pars, env):
        self.exp = exp
        self.pars = pars
        self.env = env

    def __str__(self):
        return '#<closure {0}>'.format(self.exp)

class Macro:

    def __init__(self, closure):
        self.closure = closure

    def __str__(self):
        return '#<macro {0}>'.format(self.closure.exp)

def intconverter(f):
    def conv(*args):
        t = getattr(Fraction, f.__name__)(*args)
        if t.denominator == 1:
            return Integer(t.numerator)
        else:
            return t
    return conv

def compconverter(f):
    def conv(*args):
        t = getattr(complex, f.__name__)(*args)
        if t.imag == 0:
            return Real(t.real)
        else:
            return t
    return conv

class Integer(int):

    def __div__(self, x):
        return Rational(self, x)

    def __str__(self):
        #return '#<integer {0}>'.format(int.__str__(self))
        return int.__str__(self)

class Real(float):

    def __str__(self):
        #return '#<real {0}>'.format(float.__str__(self))
        return float.__str__(self)


class Rational(Fraction):

    @intconverter
    def __new__(cls, x): pass
    @intconverter
    def __add__(self, x): pass
    @intconverter
    def __div__(self, x): pass
    @intconverter
    def __divmod__(self, x): pass
    @intconverter
    def __floordiv__(self, x): pass
    @intconverter
    def __mod__(self, x): pass
    @intconverter
    def __mul__(self, x): pass
    @intconverter
    def __pow__(self, x): pass
    @intconverter
    def __sub__(self, x): pass
    @intconverter
    def __radd__(self, x): pass
    @intconverter
    def __rdiv__(self, x): pass
    @intconverter
    def __rdivmod__(self, x): pass
    @intconverter
    def __rfloordiv__(self, x): pass
    @intconverter
    def __rmod__(self, x): pass
    @intconverter
    def __rmul__(self, x): pass
    @intconverter
    def __rpow__(self, x): pass
    @intconverter
    def __rsub__(self, x): pass

    def __str__(self):
        return '#<rational {0}/{1}>'.format(self.numerator, self.denominator)

class Complex(complex):

    def __new__(cls, x):
        n = r'[0-9]*(\.[0-9]*)?'
        m = re.compile('(([\-\+]?{0}))?((\-|\+){0})i'.format(n)).match(x)
        if m is not None:
            g = m.groups()
            c = complex.__new__(cls, float(g[1] or 0), float(g[3]))
            return c if c.imag != 0 else Real(c.real)
        else:
            raise ValueError

    @compconverter
    def __add__(self, x): pass
    @compconverter
    def __div__(self, x): pass
    @compconverter
    def __divmod__(self, x): pass
    @compconverter
    def __floordiv__(self, x): pass
    @compconverter
    def __mod__(self, x): pass
    @compconverter
    def __mul__(self, x): pass
    @compconverter
    def __pow__(self, x): pass
    @compconverter
    def __sub__(self, x): pass
    @compconverter
    def __radd__(self, x): pass
    @compconverter
    def __rdiv__(self, x): pass
    @compconverter
    def __rdivmod__(self, x): pass
    @compconverter
    def __rfloordiv__(self, x): pass
    @compconverter
    def __rmod__(self, x): pass
    @compconverter
    def __rmul__(self, x): pass
    @compconverter
    def __rpow__(self, x): pass
    @compconverter
    def __rsub__(self, x): pass

    def __str__(self):
        im = str(self.imag) if self.imag < 0 else '+'+str(self.imag)
        return '#<complex {0}{1}i>'.format(self.real, im)


class Lexer:

    def __init__(self, data):
        self.data = list(data+'\0')
        self.move()

    @classmethod
    def get_sexps(self, exp):
        ast = Lexer(exp)

        v = ast.get_sexp()
        while not v == eof:
            yield v
            v = ast.get_sexp()

    def move(self):
        if not self.data:
            raise SyntaxError()
        self.token = self.data.pop(0)
    
    def get_sexp(self):

        if self.token == '\0':
            return eof
        if self.token.isspace():
            self.move()
            return self.get_sexp()
        elif self.token == '(':
            self.move()
            return self.get_list()
        elif self.token == '\'':
            self.move()
            return self.get_quote()
        elif self.token == '`':
            self.move()
            return self.get_quasiquote()
        elif self.token == ',':
            self.move()
            return self.get_unquote()
        elif self.token == '"':
            self.move()
            return self.get_string()
        elif self.token == '#':
            self.move()
            if self.token == '\\':
                self.move()
                return self.get_char()
            elif self.token == 't':
                self.move()
                return t
            elif self.token == 'f':
                self.move()
                return f
        else:
            return self.get_atom()

    def get_list(self):
        
        def skip():
            while self.token.isspace(): self.move()

        skip()

        if self.token == ')':
            self.move()
            return nil

        cell = Cell()
        cell.car = self.get_sexp()

        skip()

        if self.token == '.':
            v = self.get_atom()
            if v == '.':
                cell.cdr = self.get_sexp()
                skip()
                if self.token == ')':
                    self.move()
                else:
                    raise SyntaxError()
            else:
                cell.cdr = Cell(v, self.get_list())
            return cell
        else:
            cell.cdr = self.get_list()
            return cell

    def get_quote(self):

        cell = Cell()
        cell.car = Symbol('quote')
        cell.cdr = Cell(self.get_sexp(), nil)
        return cell

    def get_quasiquote(self):

        cell = Cell()
        cell.car = Symbol('quasiquote')
        cell.cdr = Cell(self.get_sexp(), nil)
        return cell

    def get_unquote(self):

        if self.token == '@':
            self.move()
            cell = Cell()
            cell.car = Symbol('unquote-splicing')
            cell.cdr = Cell(self.get_sexp(), nil)
        else:
            cell = Cell()
            cell.car = Symbol('unquote')
            cell.cdr = Cell(self.get_sexp(), nil)
        return cell

    def get_char(self):

        ch = self.token
        self.move()
        while self.token not in (' ', '\t', '\n', '(', ')', '\0'):
            ch += self.token
            self.move()

        if len(ch) == 1:
            return ch
        elif ch in ('space'):
            return ' '
        elif ch in ('newline'):
            return '\n'

    def get_string(self):
        
        if self.token == '"':
            self.move()
            return ''
        else:
            if self.token == '\\':
                self.move()
                if self.token == '\\':
                    self.move()
                    head = '\\'
                elif self.token == '"':
                    self.move()
                    head = '"'
            else:
                head = self.token
                self.move()

            tail = self.get_string()
            return head+tail

    def get_atom(self):

        atom = ''
        while self.token not in ('(', ')', ' ', '\n', '\t', '\0'):
            atom += self.token
            self.move()

        try:
            return Integer(atom)
        except ValueError:
            try:
                return Real(atom)
            except ValueError:
                try:
                    return Rational(atom)
                except ValueError:
                    try:
                        return Complex(atom)
                    except:
                        return Symbol(atom)

class Env(dict):

    def __init__(self, outer=None):
        self.outer = outer

        if outer is None:
            self.add_syntaxes()
            self.add_native_funcs()
            self.preload()

    def find(self, var):
        try:
            return self[var] if var in self else self.outer.find(var)
        except:
            raise Exception("Not found the symbol: "+str(var))
    
    def add_syntaxes(self):

        def quote_syntax(arg, env):
            return arg.car

        def if_syntax(arg, env):
            if evals(arg.car, env) == t:
                return evals(arg.cdr.car, env)
            elif not arg.cdr.cdr == nil:
                return evals(arg.cdr.cdr.car, env)

        def setq_syntax(arg, env):
            var = arg.car
            exp = arg.cdr.car
            if var in env:
                env[var] = evals(exp, env)
                return env[var]
            else:
                raise Exception('Symbol:{0} is not binded before'.format(var))

        def define_syntax(arg, env):
            var = arg.car
            exp = arg.cdr.car

            if isinstance(var, Cell):
                name = var.car
                pars = var.cdr
                env[name] = Closure(exp, pars, env)
            else:
                name = var
                env[name] = evals(exp, env)
            return name

        def lambda_syntax(arg, env):
            pars = arg.car
            exp = arg.cdr.car
            return Closure(exp, pars, env)

        def begin_syntax(arg, env):
            inner = Env(env)
            exp = arg
            val = undef
            while not exp == nil:
                val = evals(exp.car, inner)
                exp = exp.cdr
            return val

        def define_macro_syntax(arg, env):
            var = arg.car
            exp = arg.cdr.car

            if isinstance(var, Cell):
                name = var.car
                pars = var.cdr
                proc = Closure(exp, pars, env)
                env[name] = Macro(proc)
            else:
                name = var
                env[name] = Macro(evals(exp, env))
            return undef

        def quasiquote_syntax(arg, env):

            def connect_list(a, b):
                if isinstance(a, Cell):
                    return Cell(a.car, connect_list(a.cdr, b))
                elif a == nil:
                    return b
                else:
                    raise Exception('Cannot connect an atom to an improper list')

            def expand(x):
                if isinstance(x, Cell):
                    if x.car == 'unquote':
                        return evals(x.cdr.car, env)
                    elif isinstance(x.car, Cell) and x.car.car == 'unquote-splicing':
                        return connect_list(evals(x.car.cdr.car, env), expand(x.cdr))
                    else:
                        return Cell(expand(x.car), expand(x.cdr))
                else:
                    return x

            return expand(arg.car)

        syntaxes = {
            'quote': quote_syntax,
            'if': if_syntax,
            'set!': setq_syntax,
            'lambda': lambda_syntax,
            'define': define_syntax,
            'begin': begin_syntax,
            'define-macro': define_macro_syntax,
            'quasiquote': quasiquote_syntax,
            }

        for name, cont in syntaxes.items():
            self[Symbol(name)] = Syntax(cont)

    def add_native_funcs(self):
        import operator as op
        funcs = {
            'cons': lambda x,y=nil: Cell(x,y),
            'car': lambda x: x.car,
            'cdr': lambda x: x.cdr,
            '+': lambda *args: reduce(op.add, args),
            '-': lambda *args: reduce(op.sub, args),
            '*': lambda *args: reduce(op.mul, args),
            '/': lambda *args: reduce(op.div, args),
            'mod': lambda x,y: t if x % y == 0 else f,
            'not': lambda x: f if x == t else t,
            '>': lambda x,y: t if x > y else f,
            '<': lambda x,y: t if x < y else f,
            '>=': lambda x,y: t if x >= y else f,
            '<=': lambda x,y: t if x <= y else f,
            '=': lambda x,y: t if x == y else f,
            'equal?': lambda x,y: t if x == y else f,
            'eq?': lambda x,y: t if x is y else f,
            'pair?': lambda x: t if isinstance(x, Cell) else f,
            'null?': lambda x: t if x == nil else f,
            'symbol?': lambda x: t if isinstance(x, Symbol) else f,
            'atom?': lambda x: t if not isinstance(x, Cell) else f,
            'display': lambda x: sys.stdout.write(str(x)) or undef,
            'newline': lambda: sys.stdout.write('\n') or undef,
            }

        for name, cont in funcs.items():
            self[Symbol(name)] = Primitive(cont)

    def preload(self):
        pre = '''
(define (1+ x) (+ x 1))
(define (1- x) (- x 1))
(define (list . x) x)
(define (cadr x) (car (cdr x)))
(define (cdar x) (cdr (car x)))
(define (caar x) (car (car x)))
(define (cddr x) (cdr (cdr x)))

(define (map f args)
  (if (null? args)
      '()
      (cons (f (car args)) (map f (cdr args)))))

(define (filter f args)
  (if (null? args)
      '()
      (if (f (car args))
          (cons (car args) (filter f (cdr args)))
          (filter f (cdr args)))))

(define-macro (let2 let-args . let-body)
  `((lambda ,(map car let-args) ,@let-body) ,@(map cadr let-args)))
        '''

        for exp in Lexer.get_sexps(pre):
            evals(exp, self)


def evals(x, env):

    def issymbol(x): return isinstance(x, Symbol)
    def islist(x): return isinstance(x, Cell)
    def isconstant(x): return isinstance(x, Integer) or isinstance(x, Real) or isinstance(x, Rational) or isinstance(x, str) or x in (t, f, nil)

    def bind_params(pars, args, closure_scope, ev=True):

        newenv = Env(closure_scope)

        def eval_rec(exps):
            return nil if exps == nil else Cell(evals(exps.car, env), eval_rec(exps.cdr, env))

        def binder(pars, args):
            if isinstance(pars, Cell):
                newenv[pars.car] = evals(args.car, env) if ev else args.car
                binder(pars.cdr, args.cdr)
            elif not pars == nil:
                newenv[pars] = eval_rec(args) if ev else args

        binder(pars, args)

        return newenv


    if x is eof:
        return

    elif issymbol(x):
        return env.find(x)

    elif islist(x):

        proc = evals(x.car, env)

        if isconstant(proc):
            return proc

        elif isinstance(proc, Syntax):
            return proc.proc(x.cdr, env)

        elif isinstance(proc, Macro):
            clos = proc.closure
            return evals(evals(clos.exp, bind_params(clos.pars, x.cdr, clos.env, False)), env)

        elif isinstance(proc, Closure):
            return evals(proc.exp, bind_params(proc.pars, x.cdr, proc.env))

        elif isinstance(proc, Primitive):
            args, elem = [], x.cdr
            while not elem == nil:
                args.append(evals(elem.car, env))
                elem = elem.cdr
            return proc.proc(*args)

        else:
            raise Exception('{0}:{1} is not callable'.format(type(x.car), x.car))

    else:
        return x


def run_repl():
    print '////////////////////////////////////////////////////////////'
    print '// アメージング☆エターナルフォースブリザード☆わざびずLisp //'
    print '//////////////////// Powered by wasabi /////////////////////'
    print '////////////////////////////////////////////////////////////'
    print 'Type "quit" to exit interactive mode'
    print 

    global_env = Env()

    while True:
        print 'そんなS式で大丈夫か? >>', 
        s = raw_input()
        if s == 'quit':
            break
        else:
            try:
                for exp in Lexer.get_sexps(s):
                    result = evals(exp, global_env)
                    if result: print result
            except SyntaxError:
                print 'Syntax Error!'
            except:
                print 'Rumtime Error!'
                print '-'*30
                traceback.print_exc(file=sys.stdout)
                print '-'*30

    print 'Bye-Bye!'


def run_non_interactive():

    global_env = Env()

    with open(sys.argv[1]) as f:
        try:
            for exp in Lexer.get_sexps(f.read()):
                result = evals(exp, global_env)
                if result is None:
                    break
        except SyntaxError:
            print 'Syntax Error!'
        except:
            print 'Runtime Error!'
            print '-'*30
            traceback.print_exc(file=sys.stdout)
            print '-'*30


if __name__ == '__main__':
    if len(sys.argv) >= 2:
        run_non_interactive()
    else:
        run_repl()

#!/usr/bin/env python3

# Reader -- parses text to something, some structure.

# Python lists for lists.
# Instances of Symbol for symbols.
# Numbers for numbers.
# Strings for strings.
# ??? for functions

# ???
class Symbol(name):
    def __init__(self, name):
        self.name = name

    # todo: implement magic methods for equality so we can use these
    # as keys in dicts

def read(text): # Return (object, rest of text)
    # ignoring whitespace --
    # If you see '(', read a list.
    # Otherwise, read an atom.
    # ...
    if (text[0] == '('):
        return read_a_list(text)
    else:
        return read_atom(text)

def read_a_list(text):
    assert text[0] == '('
    lst = []
    rest = text[1:]
    while text[0] != ')':
        obj, rest = read(rest)
        lst.append(obj)
    return lst

def read_atom(text):
    if text[0] == "\"":
        return read_string(text)
    else:
        return read_non_whitespace(text)

# Evaluator -- rules for evaluating that structure.

def eval(sexp, env):
    if is_list(sexp):
        return eval_list(sexp, env)
    else:
        return eval_atom(sexp, env)

def eval_atom(sexp, env):
    if is_self_evaluating(sexp):
        return sexp
    elif is_symbol(sexp):
        return env[sexp]
    else:
        raise Exception("Busted program: can't get here")

def eval_list(sexp, env):
    head, *rest = sexp

    # Special operators:
    # (if a b c)
    # (quote a) a.k.a. 'a
    # (lambda (a b) (+ a b))
    # (define foo 10)
    # (define foo (a b) (+ a b))
    # (define foo (lambda (a b) (+ a b)))

    # (let ((x 10)) (+ x 20))

    # Not special operators:
    # (+ 1 2), etc.

    if is_special(head):
        return eval_special(sexp, env)
    elif is_macro(head):
        return eval(macro_expand(sexp, env))
    else:
        lm, params, body = eval(head, env)
        #fn.apply()
        args = [ eval(arg, env) for arg in rest ]
        new_env = copy_env(env)
        for (name, value) in zip(params, args):
            new_env[name] = value
        eval(body, new_env)

# (foo 10 20)
# ((lambda (a b) (+ a b)) 10 20)

def eval_special(sexp, env):
    head, *rest = sexp

    if head == "if":
        condition, then, else = rest
        if lisp_bool_to_python(eval(condition, env))):
            return eval(then, env)
        else:
            return eval(else, env)
    elif head == "quote":
        if len(rest) != 1: fail("bogus quote")
        return rest[0]

        ...


def lisp_bool_to_python(sexp):
    return not (sexp == [])







#

# Atoms vs. Composite

# Composite:
#  1. Basic evaluation rule
#  2. Special operators
#  3. Macros -- extend the syntax

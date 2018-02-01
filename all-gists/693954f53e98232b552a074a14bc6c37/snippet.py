import re
import sys

def parse_any(symbols):
    while len(symbols):
        if symbols[0] == '(':
            return parse_list(symbols[1:])
        if symbols[0] == "'":
            symbols, inner = parse_any(symbols[1:])
            return symbols, ['quote', inner]
        if symbols[0].isspace():
            symbols = symbols[1:]
            continue
        if symbols[0].isalnum():
            return symbols[1:], symbols[0]
        raise RuntimeError("Cannot parse" + str(symbols))

def parse_list(symbols):
    result = []
    while len(symbols):
        if symbols[0] == ')':
            symbols = symbols[1:]
            break
        symbols, atom = parse_any(symbols)
        result.append(atom)
    return symbols, result

def parse(txt): 
    return parse_any(re.findall(r'([\(\)\']|[a-z0-9A-Z]+|\s+)', txt))[1]

def lookup(atom, env):
    for x, value in env:
        if x == atom:
            return value
    raise LookupError("%s is unbound" % atom)

def eval(exp, env):
    if isinstance(exp, str): return lookup(exp, env)
    elif isinstance(exp[0], str): return dict(
            quote=lambda exp, env: exp[1],
            atom=lambda exp, env: 't' if isinstance(eval(exp[1], env), str) else 'f',
            eq=lambda exp, env: 't' if len(set([eval(X, env) for X in exp[1:]])) == 1 else 'f',
            car=lambda exp, env: eval(exp[1], env)[0],
            cdr=lambda exp, env: (lambda x: 'nil' if len(x) == 1 else x[1:])(eval(exp[1], env)),
            cons=lambda exp, env: [eval(exp[1], env)] + ([] if rest == 'nil' else eval(exp[2], env)),
            defun=lambda exp, env: env.insert(0, (exp[1], ["label", exp[1], ["lambda", exp[2], exp[3]]])) or exp[1],
            cond=cond,
        ).get(exp[0], lambda exp, env: eval([lookup(exp[0], env)] + exp[1:], env))(exp, env)
    elif exp[0][0] == "lambda":
        (_, params, body), args = exp[0], exp[1:]
        return eval(body, zip(params, map(lambda e: eval(e, env), args)) + env)
    elif exp[0][0] == "label":
        return eval([exp[0][2]] + exp[1:], [(exp[0][1], exp[0])] + env)

def cond(exp, env):
    for p, e in exp[1:]:
        if eval(p, env) == 't':
            return eval(e, env)

def repl(env):
    while True:
        try:
            print eval(parse(raw_input("> ")), env)
        except (EOFError, KeyboardInterrupt):
            return
        except Exception, e:
            print "! %s" % e

if __name__ == "__main__":
    env = []
    for arg in sys.argv[1:]:
        with open(arg, 'r') as handle:          
            expr = parse(handle.read())
            print eval(expr, env)
    if sys.stdout.isatty():
        repl(env)
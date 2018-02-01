"""
a = 1
b = 1
i = 2
n = 10
while i < n
    c = a + b
    a = b
    b = c
    i = i + 1
"""

"""
program := statements
statements := statement*
statement := while | assign
while := "while" expr INDENT statements DEDENT
assign := VAR "=" expr NL
expr := term | term "+" term | term "<" term
term := VAR | NUM
"""

tokens = [
    ("VAR", "a"), ("=",), ("NUM", "1"), ("NL",),
    ("VAR", "b"), ("=",), ("NUM", "1"), ("NL",),
    ("VAR", "i"), ("=",), ("NUM", "2"), ("NL",),
    ("VAR", "n"), ("=",), ("NUM", "10"), ("NL",),
    ("while",), ("VAR", "i"), ("<",), ("VAR", "n"), ("INDENT",),
    ("VAR", "c"), ("=",), ("VAR", "a"), ("+",), ("VAR", "b"), ("NL",),
    ("VAR", "a"), ("=",), ("VAR", "b"), ("NL",),
    ("VAR", "b"), ("=",), ("VAR", "c"), ("NL",),
    ("VAR", "i"), ("=",), ("VAR", "i"), ("+",), ("NUM", "1"), ("NL",),
    ("DEDENT",),
]

i = 0

class Error(Exception):
    pass

def match(kind):
    if i >= len(tokens):
        return
    token = tokens[i]
    return token[0] == kind

def match_one(kinds):
    token = tokens[i]
    return token[0] in kinds

def eat(kind):
    global i
    if match(kind):
        i = i + 1
        return
    raise Error

def get(kind):
    global i
    if match(kind):
        token = tokens[i]
        i = i + 1
        return token
    raise Error

def get_one(kinds):
    global i
    if match_one(kinds):
        token = tokens[i]
        i = i + 1
        return token
    raise Error

def program():
    l = statements()
    return "program", l

def statements():
    l = []
    while True:
        s = statement()
        if not s: break
        l.append(s)
    return l

def statement():
    if match("while"): return while_()
    if match("VAR"): return assign()

def while_():
    eat("while")
    e = expr()
    eat("INDENT")
    l = statements()
    eat("DEDENT")
    return "while", e, l

def assign():
    v = get("VAR")
    eat("=")
    e = expr()
    eat("NL")
    return "assign", v, e

def expr():
    t1 = term()
    ops = ["+", "<"]
    if match_one(ops):
        op = get_one(ops)[0]
        t2 = term()
        return op, t1, t2
    return t1

def term():
    if match("VAR"): return get("VAR")
    if match("NUM"): return get("NUM")
    raise Error

def interpret(p):
    kind = p[0]
    if kind == 'program':
        statements = p[1]
        for statement in statements:
            interpret(statement)
    elif kind == 'while':
        expr = p[1]
        statements = p[2]
        while True:
            e = evaluate(expr)
            if not e: break
            for statement in statements:
                interpret(statement)
    elif kind == 'assign':
        name = p[1][1]
        expr = p[2]
        state[name] = evaluate(expr)
        
def evaluate(e):
    kind = e[0]
    if kind == 'VAR':
        name = e[1]
        return state[name]
    elif kind == 'NUM':
        number = e[1]
        return int(number)
    elif kind == '+':
        e1 = evaluate(e[1])
        e2 = evaluate(e[2])
        return e1 + e2
    elif kind == '<':
        e1 = evaluate(e[1])
        e2 = evaluate(e[2])
        return e1 < e2

state = {}
p = program()
interpret(p)
print state['b']

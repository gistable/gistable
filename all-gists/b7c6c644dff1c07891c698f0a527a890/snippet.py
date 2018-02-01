import re, sys # this file requires python 3
def parse(tokens):
    stack = ([], None)
    for t in tokens:
        if t == '(':
            stack = ([], stack)
        elif t == ')':
            (finished_list, stack) = stack
            stack[0].append(finished_list)
        elif not t.startswith(';;'):
            stack[0].append(t)
    return stack[0]
def reduce(f, init, items):
    for i in items[::-1]:
        init = f(i, init)
    return init
def run(stmt, names):
    if isinstance(stmt, int) or isinstance(stmt, float): return stmt
    if isinstance(stmt, str):
        return int(stmt) if stmt.isdigit() else names[stmt]
    if stmt == []: return None
    op, *args = stmt
    if op == 'def':
        names[args[0]] = run(args[1], names)
        return None
    elif op == 'fn': return stmt
    elif op == 'if': return run(args[1], names) if run(args[0], names) else run(args[2], names)
    elif op == 'set':
        val = run(args[1], names)
        names[args[0]] = val
        return val
    elif op == 'quote': return args[0]
    arg_vals = [run(a, names) for a in args]
    if op == 'print':
        print(*arg_vals)
        return None
    elif op == 'read':
        x = input()
        return int(x) if x.isdigit() else x
    elif op == '+': return sum(arg_vals)
    elif op == '-': return arg_vals[0] - sum(arg_vals[1:])
    elif op == '*': return reduce(lambda a,b: a*b, 1, arg_vals)
    elif op == '/': return arg_vals[0] / reduce(lambda a,b: a*b, 1, arg_vals[1:])
    elif op == '>': return int(arg_vals[0] > arg_vals[1])
    elif op == '<': return int(arg_vals[0] < arg_vals[1])
    elif op == 'and': return int(reduce(lambda a,b: a and b, True, [a != 0 for a in arg_vals]))
    elif op == 'or': return int(reduce(lambda a,b: a or b, False, [a != 0 for a in arg_vals]))
    elif op == 'not': return int(arg_vals[0] == 0)
    elif op == 'head': return arg_vals[0][0]
    elif op == 'tail': return arg_vals[0][1]
    elif op == 'cons': return (arg_vals[0], arg_vals[1])
    elif op == 'eq': return arg_vals[0] == arg_vals[1]
    elif op == 'list': return reduce(lambda a,b: (a,b), None, arg_vals)
    elif op in names:
        _, arg_names, body = names[op]
        frame = names.copy()
        for (name, val) in zip(arg_names, arg_vals):
            frame[name] = val
        return run(body, frame)
    else:
        print('error, uknown function name', op)
token_re = re.compile(r'([(]|[)]|;;[^\n]*\n|"(?:[^"\\]|\\.)*"|[^\s()]+|\s+|\n)')
lisp = parse([t for t in token_re.findall(sys.stdin.read()) if not t.isspace()])
names = {}
[run(stmt, names) for stmt in lisp]
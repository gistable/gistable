import re, sys, operator

#read and tokenize the program
tokens = [x for x in re.split(r'\s+', re.sub('([()])', r' \1 ', ''.join((sys.stdin.readlines())))) if x]

#populate the global scope
global_scope = None, {'+': lambda nums: sum(map(apply, nums)), '-': lambda nums: -nums[0]() if len(nums)==1 else nums[0]() - sum(map(apply, nums)[1:]),
                     '/': lambda nums: nums[0]() / nums[1](), '*': lambda nums: reduce(operator.mul, map(apply, nums)),
                     'equal?': lambda exprs: 'true' if exprs[0]() == exprs[1]() else 'false',
                     'if': lambda exprs: exprs[1]() if exprs[0]()=='true' else exprs[2]()}

#evaluate an expression
def evaluate(expr,scope=global_scope):
    parent,symbols = scope
    if type(expr) is list:
        evals = map(lambda statement: lambda use_scope=None:
            evaluate(statement,use_scope) if use_scope else evaluate(statement,scope), expr[1:])
        if expr[0]=='lambda':
            return lambda new_expr: map(lambda e: e((scope, dict(zip(expr[1], map(apply,new_expr))))), evals[1:])[-1]
        else:
            return evaluate(expr[0],scope)(evals)
    elif expr in symbols:
        return symbols[expr]
    elif parent:
        return evaluate(expr,parent)
    return float(expr)

#parse the program into a datastructure
def parse(tokens):
    if tokens[0]!='(': return tokens.pop(0)
    tokens.pop(0)
    ret=[]
    while (tokens[0] != ')'):
        ret.append(parse(tokens)) if tokens[0] == '(' else ret.append(tokens.pop(0))
    tokens.pop(0)
    return ret

#repl
while len(tokens)>0: print evaluate(parse(tokens))
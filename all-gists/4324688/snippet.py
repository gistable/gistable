import re
import json

OP_STACK = list()
ELEM_STACK = list()
COMP_STACK = list()

OP_MONGO_MAP = dict({
    'AND': '$and',
    'OR': '$or',
    'NOT': '$not',
    'LESS': '$lt',
    'GREATER': '$gt',
    'LESS_OR_EQUAL': '$lte',
    'GREATER_OR_EQUAL': '$gte'
})

class Token(object):
    TOKEN_DICT = [
        ('AND', r'^(and)'),
        ('OR', r'^(or)'),
        ('NOT', r'^(not)'),
        ('LEFT_PAREN', r'^(\()'),
        ('RIGHT_PAREN', r'^(\))'),
        ('LESS', r'^(<)[^>=]'),
        ('GREATER', r'^(>[^=])'),
        ('EQUAL', r'^(==)'),
        ('LESS_OR_EQUAL', r'^(<=)'),
        ('GREATER_OR_EQUAL', r'^(>=)'),
        ('INTEGER', r'^(\d+)'),
        ('STRING', r"^'([_\w]+)'"),
        ('FIELD', r'^([_\w]+)')
    ]
    
    def __init__(self, tokenType, tokenValue):
        self.tokenType = tokenType
        self.tokenValue = tokenValue
    
    def getType(self):
        if self.tokenType in ['AND', 'OR', 'NOT', 'LEFT_PAREN', 'RIGHT_PAREN']:
            return 'OP'
        elif self.tokenType in ['LESS', 'GREATER', 'EQUAL', 'LESS_OR_EQUAL', 'GREATER_OR_EQUAL']:
            return 'COMP'
        else:
            return 'ELEM'
    pass

def get_token(string):
    string = string.strip()
    while string != '':
        illegal = True
        for tokenTypeTuple in Token.TOKEN_DICT:
            regex = re.compile(tokenTypeTuple[1], re.I)
            m = regex.match(string)
            if m:
                illegal = False
                token_str = m.group(1)
                token = Token(tokenTypeTuple[0], token_str)
                if token.tokenType == 'STRING':
                    offset = len(token_str) + 2
                else:
                    offset = len(token_str)
                string = string[offset:].strip()
                break
        if not illegal:
            yield token
        if illegal:
            break

def make_tree(token):
    return token.tokenValue
    return dict({'root': token.tokenValue})

def compare_op(op1, op2):
    ops = ['OR', 'AND', 'NOT',  'RIGHT_PAREN', 'LEFT_PAREN', 'EQUAL', 'LESS', 'GREATER', 'LESS_OR_EQUAL', 'GREATER_OR_EQUAL']
    pos1 = ops.index(op1.tokenType)
    pos2 = ops.index(op2.tokenType)
    if pos1 <= pos2:
        return -1
    else:
        return 1
    pass

def build_not(op, expression):
    # return dict({'root': op.tokenType, 'children': [expression]})
    return dict({OP_MONGO_MAP[op.tokenType]: expression})

def build_binary(op, left, right):
    # return dict({'root': op.tokenType, 'children': [left, right]})
    return dict({OP_MONGO_MAP[op.tokenType]: [left, right]})

def build_comparator(op, left, right):
    return dict({left: {OP_MONGO_MAP[op.tokenType]: right}})

def parse_for_mongo(ast):
    pass

def build_cond(comp, l, r):
    if comp == 'EQUAL':
        return dict({l: r})
    else:
        return dict({l: {OP_MONGO_MAP[comp]: r}})

def parse(topOp):
    if topOp.tokenType == 'NOT':
        element = ELEM_STACK.pop()
        ELEM_STACK.append(build_not(topOp, element))
    elif topOp.tokenType == 'LEFT_PAREN':
        return
    elif topOp.tokenType == 'RIGHT_PAREN':
        while OP_STACK[-1].tokenType != 'LEFT_PAREN':
            parse(OP_STACK.pop())
        OP_STACK.pop()
    else:
        right_element = ELEM_STACK.pop()
        left_element = ELEM_STACK.pop()
        if topOp.tokenType in ['AND', 'OR']:
            ELEM_STACK.append(build_binary(topOp, left_element, right_element))
        else:
            ELEM_STACK.append(build_comparator(topOp, left_element, right_element))
        
        while len(OP_STACK) > 0 and compare_op(OP_STACK[-1], topOp) > 0 and OP_STACK[-1].tokenType != 'LEFT_PAREN':
            parse(OP_STACK.pop())

def push_simple_expression():
    if len(COMP_STACK) == 1:
        r = ELEM_STACK.pop()
        l = ELEM_STACK.pop()
        comp = COMP_STACK.pop()
        ELEM_STACK.append(build_cond(comp, l, r))
        
if __name__ == '__main__':
    for token in get_token("(type < 300) AND (camp == 1314 OR camp == 1415) AND (NOT spotid == 'xxx' AND NOT spotid == 'yyy')"):
        # print token.tokenType
        if token.getType() == 'ELEM':
            ELEM_STACK.append(token.tokenValue)
            if token.tokenType in ['STRING', 'INTEGER']:
                push_simple_expression()
        elif token.getType() == 'COMP':
            COMP_STACK.append(token.tokenType)
        else:
            if token.tokenType == 'LEFT_PAREN':
                # print token.tokenType
                OP_STACK.append(token)
            elif len(OP_STACK) == 0 or OP_STACK[-1].tokenType == 'LEFT_PAREN' or compare_op(OP_STACK[-1], token) < 0:
                OP_STACK.append(token)
            else:
                # print map(lambda x: x.tokenType, OP_STACK)
                topOp = OP_STACK.pop()
                parse(topOp)
                OP_STACK.append(token)
    while not len(OP_STACK) == 0:
        topOp = OP_STACK.pop()
        parse(topOp)
    print json.dumps(ELEM_STACK[0], indent=4)
    pass
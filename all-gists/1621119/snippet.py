class Token:
    ASSIGN = 'assign'
    NAME = 'name'
    NUMBER = 'number'
    
    PLUS = 'plus'
    MINUS = 'minus'
    LPARENS = 'lparens'
    RPARENS = 'rparens'
    DOUBLEDOT = 'doubledot'
    EQUAL = 'equal'
    IF = 'if'

    NEWLINE = 'newline'
    EMPTY = 'empty'

    def __init__(self, tokenizer, type, start, end):
        self.tokenizer = tokenizer
        self.type = type
        self.start = start
        self.end = end

    def __str__(self):
        return '<token ' + self.type + '>'

class Number(Token):
    def __init__(self, tokenizer, start, end):
        Token.__init__(self, tokenizer, Token.NUMBER, start, end)
        self.value = int(self.tokenizer.source[start:end])

    def __str__(self):
        return '<token Number : %d>' % self.value

class Name(Token):
    def __init__(self, tokenizer, start, end):
        Token.__init__(self, tokenizer, Token.NAME, start, end)
        self.name = self.tokenizer.source[start:end]

    def __str__(self):
        return '<token Name : %s>' % self.name

class Empty(Token):
    def __init__(self, tokenizer, start):
        Token.__init__(self, tokenizer, Token.EMPTY, start, start)

class SingleCharToken(Token):
    def __init__(self, tokenizer, type, start):
        Token.__init__(self, tokenizer, type, start, start + 1)

class CompareEqual(Token):
    def __init__(self, tokenizer, start):
        Token.__init__(self, tokenizer, Token.EQUAL, start, start + 2)

class IfStatement(Token):
    def __init__(self, tokenizer, start):
        Token.__init__(self, tokenizer, Token.IF, start, start + 2)

import unicodedata

class Tokenizer:
    def __init__(self, source):
        self.source = source
        self.position = 0
        self.line = 1

    def get(self):
        try:
            char = self.source[self.position]
            self.position += 1
            return char
        except IndexError:
            return None

    def unget(self, char):
        self.position -= 1
        assert self.source[self.position] == char

    def token(self):
        char = self.get()

        if not char:
            return Empty(self, self.position)

        while char.isspace():
            if char == '\n':
                return SingleCharToken(self, Token.NEWLINE, self.position)
            
            char = self.get()
            if not char:
                return Empty(self, self.position)

        self.unget(char) # push back first non-space

        if char == '=':
            self.get()
            char = self.get()
            
            if char == '=':
                return CompareEqual(self, self.position)

            self.unget(char)    
            return SingleCharToken(self, Token.ASSIGN, self.position)

        single =  {
            '+': Token.PLUS,
            '-': Token.MINUS,
            '(': Token.LPARENS,
            ')': Token.RPARENS,
            ':': Token.DOUBLEDOT
        }

        if single.has_key(char):
            self.get()
            return SingleCharToken(self, single[char], self.position)

        if char == 'i':
            char = self.get()
            char2 = self.get()
            if char2 == 'f':
                return IfStatement(self, self.position)

            self.unget(char2)
            self.unget(char)

        if char.isdigit():
            start = self.position
            while char.isdigit():
                char = self.get()
                if not char:
                    break
            if char:
                self.unget(char)

            return Number(self, start, self.position)

        if char.isalpha():
            start = self.position
            while char.isalpha() or char.isdigit():
                char = self.get()
                if not char:
                    break
            if char:
                self.unget(char)

            return Name(self, start, self.position)

        raise Exception('Unknonw Token type')

    def peek(self):
        saved = self.position
        token = self.token()
        self.position = saved
        return token


class Parser:
    def __init__(self, tokenizer):
        self.tokenizer = tokenizer
        self.ast = []

    def primary(self):
        token = self.tokenizer.token()

        if token.type == Token.NAME:
            return ['name', token.name]
        if token.type == Token.NUMBER:
            return ['number', token.value]

        raise Exception('unexcpected ' + token.type + ' token')

    def parens(self):
        type = self.tokenizer.peek().type

        if type == Token.LPARENS:
            self.tokenizer.token()

            expression = self.assignment()

            if self.tokenizer.token().type != Token.RPARENS:
                raise Exception('missing ) after parenthese expression')

            return expression

        return self.primary()

    def unary(self):
        lhs = self.parens()

        type = self.tokenizer.peek().type
        if type == Token.LPARENS:
            self.tokenizer.token()
            if self.tokenizer.token().type != Token.RPARENS:
                raise Exception('missing ) after (')
            return ['call', lhs]

        return lhs

    def expression(self):
        lhs = self.unary()

        type = self.tokenizer.peek().type
        if type == Token.PLUS:
            self.tokenizer.token()
            rhs = self.expression()
            return ['add', lhs, rhs]

        if type == Token.EQUAL:
            self.tokenizer.token()
            rhs = self.expression()
            return ['equal', lhs, rhs]

        return lhs

    def assignment(self):
        lhs = self.expression()

        token = self.tokenizer.peek()
        if token.type == Token.ASSIGN:
            self.tokenizer.token()
            if lhs[0] != 'name':
                raise Exception('bad lhs of assign')

            rhs = self.assignment()
            return ['assign', lhs, rhs]
        return lhs

    def statement(self):
        type = self.tokenizer.peek().type

        if type == Token.IF:
            self.tokenizer.token()
            condition = self.expression()
            
            if self.tokenizer.token().type != Token.DOUBLEDOT:
                raise Exception('missing : after condition in if statement')

            type = self.tokenizer.peek().type
            if type != Token.NEWLINE:
                body = ['block', [self.statement()]]
            else:
                body = self.statements()

            return ['if', condition, body]

        assignment = self.assignment()

        type = self.tokenizer.peek().type
        if not type in [Token.NEWLINE, Token.EMPTY]:
            raise  Exception('unexcpected ' + type + ' token')

        return assignment

    def statements(self):
        body = []
        while True:
            type = self.tokenizer.peek().type
            if type == Token.NEWLINE:
                self.tokenizer.token()
            elif type == Token.EMPTY:
                return ['block', body]
            else:
                body.append(self.statement())

def execute(ast, vars):
    if ast[0] == 'block':
        value = None
        for statement in ast[1]:
            value = execute(statement, vars)
        return value
    if ast[0] == 'if':
        value = execute(ast[1], vars)
        if value:
            value = execute(ast[2], vars)
        return value
    if ast[0] == 'assign':
        name = ast[1]
        assert name[0] == 'name'
        value = execute(ast[2], vars)
        vars[name[1]] = value
        return value
    if ast[0] == 'add':
        lhs = execute(ast[1], vars)
        rhs = execute(ast[1], vars)
        return lhs + rhs
    if ast[0] == 'number':
        return ast[1]
    if ast[0] == 'name':
        return vars[ast[1]]

test = 'a = 1 \n if a: a = 5'

t = Tokenizer(test)
p = Parser(t)

ast = p.statements()
print ast

vars = {}
print execute(ast, vars)
print vars
        

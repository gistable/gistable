#this program uses the Shunting Yard algorithm to transform infix expressions
# into postfix, and then an AST, which can then be easily evaluated.
#just run `python calc.py` and enjoy. enjoyment is optional and not included
# with the standard calc.py package, but for an extra $99.99 we can have a
# calc.py Premium Deluxe sent to you over the next 6-8 weeks, which may or may
# not increase your enjoyment of our calc.py product.
#for a list of operators supported and not supported (for isntance, the unary -
# is a ~) look below.
#TODO: handle parentheses.

from __future__ import print_function

#operator table: operator => { precedence, associativity=left, arity=2, calc }

#but first, a note from our sponsor, the infamous factorial (yes, I know it can
# be optimised to great extents)
def factorial (n):
    if n < 2:
        return 1
    return n * factorial(n-1)

operators = {
    # addition
    '+' : {
        'prec' : 1,
        'calc' : lambda a,b: a + b },
    # subtraction
    '-' : {
        'prec' : 1,
        'calc' : lambda a,b: a - b },
    # multiplication
    '*' : {
        'prec' : 2,
        'calc' : lambda a,b: a * b },
    # division
    '/' : {
        'prec' : 2,
        'calc' : lambda a,b: a / b },
    # exponentiation
    '^' : {
        'prec' : 3,
        'assoc' : 'right',
        'calc' : lambda a,b: a ** b },
    # negation
    '~' : {
        'prec' : 6,
        'assoc' : 'right',
        'arity' : 1,
        'calc' : lambda a: -a },
    # modulus
    '%' : {
        'prec' : 4,
        'calc' : lambda a,b: a % b },
    # factorial
    '!' : {
        'prec' : 4,
        'assoc' : 'right',
        'arity' : 1,
        'calc' : lambda a: factorial(a) },
    # average
    '@' : {
        'prec' : 5,
        'calc' : lambda a,b: (a + b) / 2 },
    # max
    '$' : {
        'prec' : 5,
        'calc' : lambda a,b: max(a,b) },
    # min
    '&' : {
        'prec' : 5,
        'calc' : lambda a,b: min(a,b) } }

for key in operators:
    operators[key]['symbol'] = key

class Calculator:
    def __init__ (self):
        self.operators = operators

    def calc (self, inp):
        self.parse(inp)
        self.ast = self.to_ast()
        return self.ast.calc() if self.ast is not None else None

    def parse (self, inp):
        tokens = list(inp.replace(' ', ''))
        self.opstack = []
        self.out = []

        while tokens:
            self.parse_token(tokens.pop(0))

        while self.opstack:
            self.out.append(self.opstack.pop())
            #check for mismatched parens

        #awesome, we jut finished converting into postfix

    def to_ast (self):
        if not self.out:
            return None

        #we go from the right. on each operator, we grab `arity` tokens ahead
        # and add them as the op's children
        stack = self.out[::]
        root = self.build_ast(stack.pop(), stack)
        return root

    def build_ast (self, tok, stack):
        if not stack:
            return tok

        for i in xrange(0, tok.arity):
            if not stack:
                msg = 'Improper expression: {0} expected {1} operands, but only got {2}'.format(tok.symbol, tok.arity, i)
                raise SyntaxError(msg)


            child = stack.pop()
            print('popped token %s' % (child))

            #recurse if we're on an operator
            if isinstance(child, OperatorToken):
                self.build_ast(child, stack)
            tok.add_child(child)

        return tok


    def parse_token (self, tok):
        if is_number(tok):
            self.out.append(NumberToken(tok))
        elif self.operators.has_key(tok):
            actual_tok = OperatorToken(self.operators[tok])
            self.parse_op(actual_tok)
        #add parentheses handling
        else:
            raise SyntaxError('Unrecognized token ' + str(tok));

    def parse_op (self, tok):
        #an operator `left` is weaker than (should be placed after) `right` if
        # it's left-associative and they have equal precedence, or if `left`
        # just has lower precedence than `right`
        def weaker (left, right):
            if left.assoc == 'left' and left.prec == right.prec:
                return True
            return left.prec < right.prec

        while self.opstack and weaker(tok, self.opstack[-1]):
            self.out.append(self.opstack.pop())

        self.opstack.append(tok)


class Token:
    pass

class OperatorToken(Token):
    prec = 1
    assoc = 'left'
    arity = 2
    cb = lambda a,b: None

    def __init__ (self, op):
        self.children = []

        self.symbol = op['symbol']
        self.prec   = op['prec']
        self.assoc  = op['assoc'] if op.has_key('assoc') else 'left'
        self.arity  = op['arity'] if op.has_key('arity') else 2
        self.cb     = op['calc']

    def calc (self):
        args = [child.calc() for child in self.children]
        print('args to ', self.symbol, ' '.join([str(x) for x in args]))
        return self.cb(*args)


    def add_child (self, child):
        print('Adding child %s to %s' % (child, self))
        self.children.insert(0, child)

    def add_children (self, *children):
        for child in children:
            self.add_child(child)

    def humane_str (self):
        if self.arity == 1 and self.assoc == 'right':
            return self.symbol + str(self.children[0])
        elif self.arity == 2:
            return ' '.join(
                [self.children[0].humane_str(),
                 self.symbol,
                 self.children[1].humane_str()])

        strung_children = [str(x) for x in self.children]
        return '{0} => [{1}]'.format(self.symbol, ', '.join(strung_children))

    def __str__ (self):
        return self.symbol


class NumberToken(Token):
    def __init__ (self, val):
        self.value = float(val) if '.' in str(val) else int(val)

    def calc (self):
        return self.value

    def humane_str (self):
        return str(self)

    def __str__ (self):
        return str(self.value)

def is_number (string):
    try:
        float(string)
        return True
    except ValueError:
        return False

if __name__ == '__main__':
    calc = Calculator()

    while True:
        try:
            inp = raw_input('> ')
        except EOFError:
            inp = ''
        if not inp:
            print('Goodbye!')
            break

        res = None
        try:
            res = calc.calc(inp)
        except SyntaxError as ex:
            print('Syntax error: {0}'.format(str(ex)))
        else:
            if res is not None:
                print(calc.ast.humane_str(), end=' = ')
            print(res)

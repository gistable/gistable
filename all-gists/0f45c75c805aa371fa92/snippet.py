"""
This implements a fairly simple expression language via a Pratt-style parser.

The language supports fairly standard floating point literals, such as:

    5
    1.09
    .16

    12e7
    12.34e-45
    .34e-2

It also supports basic arithmetic operators (which obey arithmetic precedence):

    + (addition)
    - (subtraction)
    * (multiplication)
    / (division)
    ^ (exponentiation)
    % (modulus)

Parentheses are also supported.

    1 + 2 * 3   -- evaluates to 7
    (1 + 2) * 3 -- evaluates to 9

Support for simple functions is also included, which take single and multiple
arguments:

    sin 3.1415926   -- Functions can be called like in ML...
    sin(3.1415926)  -- ... or with parenthesis delimiting the argument.
    logN(64, 8)     -- Multiple arguments are handled via tuples.

Finally, the language also supports tuples (which are typically used for function
arguments, as in the logN example above):

    1,2         -- Denotes a tuple with two elements, 1 and 2
    1+2, 3+4    -- Tuples bind looser than arithmetic operators, so this...
    (1+2),(3+4) -- ... and this are equivalent

    (1,)        -- Singleton tuples are also allowed, as in Python
"""
from collections import deque, namedtuple
from enum import Enum
from functools import singledispatch
import math
import operator
import random
import string

class Operators(Enum):
    """
    Different types of operators which can be applied to expressions.
    """
    ADD = 1
    SUB = 2
    MUL = 3
    DIV = 4
    MOD = 5
    POW = 6

# The glyph used to represent each particular operator in expressions
SYMBOL_TO_OPERATOR = {
    '+': Operators.ADD,
    '-': Operators.SUB,
    '*': Operators.MUL,
    '/': Operators.DIV,
    '%': Operators.MOD,
    '^': Operators.POW,
}

# The functions used to evaluate each type of arithmetic expression
OPERATOR_EVAL = {
    Operators.ADD: operator.add,
    Operators.SUB: operator.sub,
    Operators.MUL: operator.mul,
    Operators.DIV: operator.truediv,
    Operators.MOD: operator.mod,
    Operators.POW: operator.pow,
}

# Maps functions in the evaluator to Python built-in functions. Note that
# functions with >1 argument must be unpacked explicitly, since the evaluator
# uses tuples for providing multiple arguments.
FUNC_TABLE = {
    'sin': math.sin,
    'cos': math.cos,
    'tan': math.tan,
    'acos': math.acos,
    'asin': math.asin,
    'atan': math.atan,

    'radians': math.radians,
    'degrees': math.degrees,

    'ceil': math.ceil,
    'floor': math.floor,
    'trunc': math.trunc,

    'factorial': math.factorial,

    'exp': math.exp,
    'gamma': math.gamma,
    'log': math.log,
    'log10': math.log10,
    'log2': math.log2,
    # logN(value, base)
    'logN': lambda x: math.log(x[0], x[1]),
    'sqrt': math.sqrt,

    # random(min, max)
    'random': lambda x: random.uniform(x[0], x[1]),
    # normal(mean, sigma)
    'normal': lambda x: random.normalvariate(x[0], x[1]),

    'print': lambda x: (print(x), x)[1]
}

# The precedence table for binary operators.
PRECEDENCE_TABLE = {
    Operators.ADD: 3,
    Operators.SUB: 3,

    Operators.MUL: 4,
    Operators.DIV: 4,

    Operators.MOD: 5,
    Operators.POW: 6,
}

# The prefix table for unary operators.
PREFIX_PRECEDENCE_TABLE = {
    Operators.ADD: 11,
    Operators.SUB: 11,
}

# All the different tokens, which are produced by the lexer and consumed by the
# parser.
#
# In general, each of these have three primary pieces of functionality, implemented
# by the singledispatch generic functions that follow:
#
# - a particular precedence (higher means tighter binding)
# - a prefix mode, which is called when the token appears at the beginning
#   of an expression.
# - an infix mode, which is called when the token appears in the middle of an
#   expression
NameToken = namedtuple('NameToken', ['name'])
NumberToken = namedtuple('NumberToken', ['value'])
BeginGroup = namedtuple('BeginGroup', [])
EndGroup = namedtuple('EndGroup', [])
CommaToken = namedtuple('CommaToken', [])
OperatorToken = namedtuple('OperatorToken', ['operator'])

# All the types of expressions which the parser can generate. The only useful
# things you can do with these is evaluate them.
NumberExpression = namedtuple('NumberExpression', ['value'])
CallExpression = namedtuple('CallExpression', ['func', 'arg'])
BinaryExpression = namedtuple('BinaryExpression', ['left', 'right', 'func'])
Tuple = namedtuple('Tuple', ['elems'])

# Precedences for all other kinds of tokens, which are not operators
TOKEN_PRECEDENCE_TABLE = {
    NameToken: 9,
    BeginGroup: 10,
    EndGroup: 1,
    CommaToken: 2,
}

##### Indenting Pretty Printer #####
def pretty(expr, indent=0):
    """
    Pretty formats an expression, indenting all the sub-expressions relative to
    their parents. Useful for debugging, or for visualizing the parser's results.
    """
    if not isinstance(expr, tuple):
        return (indent * '  ') + str(expr) + '\n'

    buffer = (indent * '  ') + str(type(expr).__name__) + '\n'
    if isinstance(expr, Tuple):
        # Tuples contain sequences, and must be handled specially, by extracting
        # the internal expression (so the loop iterates it correctly)
        expr = expr.elems

    if tuple(expr):
        for child in tuple(expr):
            buffer +=  pretty(child, indent+1)
        return buffer
    else:
        return buffer

##### Token Precedence #####
# These are responsible for figuring out the precedence of each type of token.
#
# Note that each token can discriminate based upon whether it is being used
# in the prefix position or the infix position, although most of them don't
# care. Only the + and - operators change their precedence depending upon
# their position.

@singledispatch
def token_precedence(tok, prefix):
    """
    Gets the precedence of a token.

    Note that prefix is True when the operator is in the prefix position,
    otherwise it is False when the operator is in the infix position.
    """
    return TOKEN_PRECEDENCE_TABLE[type(tok)]

@token_precedence.register(OperatorToken)
def _(tok, prefix):
    if prefix:
        precedence = PREFIX_PRECEDENCE_TABLE.get(tok.operator, None)
        if tok is None:
            raise SyntaxError('{} is not a valid prefix operator'.format(tok))
        return precedence
    else:
        return PRECEDENCE_TABLE[tok.operator]

##### Prefix Operations #####
# These take each different type of token, and generate expressions which result
# from the token being used as a prefix operator. For example, +1 would call the
# prefix operation of +.
#
# Note that the number tokens, although they are not operators, need this since
# they *do* appear in the prefix position.
#
# In summary:
# - NameToken in the prefix position indicates a call to a function, and consumes
#   its one argument (>1 arguments are represented by tuples).
# - BeginGroup searches for the matching EndGroup, and returns the expression
#   between them. Groups are not actually a type of expression, but a way of
#   delimiting precedence.
# - OperatorToken can be either a + or a -, both of which act as signs to the
#   expressions following them. Other operators are syntax errors.

@singledispatch
def parse_prefix(tok, parser):
    """
    Returns the expression which results when using the given token as a prefix
    operator.
    """
    # By default, a token cannot serve as a prefix operator.
    raise SyntaxError('Expecting prefix operator, but {} was found'.format(tok))

@parse_prefix.register(NameToken)
def _(tok, parser):
    # Names indicate function calls, which must be postfixed by a single value
    # (multiple arguments are passed in via tuples).
    arg = parser.parse(TOKEN_PRECEDENCE_TABLE[NameToken])
    if arg is None:
        raise SyntaxError('Hit end of expression while reading arguments to {}'.format(tok))

    return CallExpression(tok.name, arg)

@parse_prefix.register(NumberToken)
def _(tok, parser):
    return NumberExpression(tok.value)

@parse_prefix.register(BeginGroup)
def _(tok, parser):
    # (by a 'group', I mean a pair of parenthesis. The group (1+2) is a group
    # which contains the expression 1+2).
    expr = parser.parse(TOKEN_PRECEDENCE_TABLE[EndGroup])
    if expr is None:
        raise SyntaxError('Hit end of expression while reading sub-expression inside (')

    end_paren = parser.next_token()
    if end_paren is None:
        raise SyntaxError('Hit end of expression while waiting for )')
    elif not isinstance(end_paren, EndGroup):
        raise SyntaxError('Got a {} when a ) was expected'.format(end_paren))
    return expr

@parse_prefix.register(OperatorToken)
def _(tok, parser):
    if tok.operator is Operators.ADD:
        # Unary positive, such as +3
        operand = parser.parse(token_precedence(tok, prefix=True))
        if operand is None:
            raise SyntaxError('Expected value after +')

        return operand
    elif tok.operator is Operators.SUB:
        # Unary negative, such as -5
        operand = parser.parse(token_precedence(tok, prefix=True))
        if operand is None:
            raise SyntaxError('Expected value after -')

        return MulExpression(NumberExpression(-1), operand)
    else:
        raise SyntaxError('{} is not a prefix operator'.format(tok))

##### Infix Operations #####
# The following functions take the token given, as well as the expression to the
# left of the token, and return a new expression which results from using the
# token as an infix operator.
#
# There are only two types of infix operators:
# - CommaToken is used to construct tuples, in basically the same way as Python.
#   It reads further CommaTokens, until it hits either and ending parenthesis or
#   a non-comma (caring about the ending parenthesis allows singleton tuples to
#   be represented by (1,) as they are in Python).
# - OperatorToken is used to construct binary expressions.

@singledispatch
def parse_infix(tok, left, parser):
    """
    Returns the expression which results when using the given token as an infix
    operator.
    """
    # By default, a token cannot serve as an infix operator.
    raise SyntaxError('Expecting infix operator, but {} was found'.format(tok))

@parse_infix.register(CommaToken)
def _(tok, left, parser):
    # Tuples are chained operators, so we have to go until we find no more commas.
    items = [left]
    while True:
        next_token = parser.peek_token()
        if isinstance(next_token, EndGroup):
            # Like Python, if we hit a ), then stop constructing a tuple - this
            # lets us get one-element tuples by using (1,).
            return Tuple(items)

        element = parser.parse(token_precedence(tok, prefix=False))
        if element is None:
            return Tuple(items)
        items.append(element)

        trailing = parser.peek_token()
        if trailing is None or not isinstance(trailing, CommaToken):
            # We've hit the end of the tuple, so wrap it up and continue.
            return Tuple(items)
        else:
            # Another comma means another element, so consume the comma before
            # continuing.
            parser.next_token()

@parse_infix.register(OperatorToken)
def _(tok, left, parser):
    precedence = token_precedence(tok, prefix=False)
    right = parser.parse(precedence)
    if right is None:
        raise SyntaxError('Expected expression after binary operator')

    expr_func = OPERATOR_EVAL[tok.operator]
    result = BinaryExpression(left, right, expr_func)
    return result

##### Expression Evaluation #####
# This converts an expression type into a numeric value by interpreting the
# expression. This is basically what you'd expect from these functions.

@singledispatch
def evaluate_expr(expr):
    return float('NaN')

@evaluate_expr.register(NumberExpression)
def _(expr):
    return expr.value

@evaluate_expr.register(CallExpression)
def _(expr):
    try:
        func = FUNC_TABLE[expr.func]
        return func(evaluate_expr(expr.arg))
    except KeyError:
        raise SyntaxError('Unknown function {}'.format(expr.func))

@evaluate_expr.register(BinaryExpression)
def _(expr):
    return expr.func(evaluate_expr(expr.left), evaluate_expr(expr.right))

@evaluate_expr.register(Tuple)
def _(expr):
    return tuple(evaluate_expr(elem) for elem in expr.elems)

##### Lexer #####
# This turns a character stream into a stream of tokens. The only interesting
# functions (besides lex()) are lex_number() and lex_name() - these more-or-less
# reimplement the state machines which would underly the regular expressions
# representing names and numbers. Their state machines are clearly laid-out,
# so don't expect any trouble understanding them.

DIGITS = [str(x) for x in range(0, 9+1)]
LETTERS = string.ascii_letters
OPERATORS = list(SYMBOL_TO_OPERATOR)
SPACES = ' \r\t\n\v'

# This is explained below, but basically, it is faster to use this than call
# int() for single digits.
NUM_TO_INT = {str(x): x for x in range(0, 9+1)}

def lex_number(stream):
    """
    Lexes a floating point number, which consists of four parts:

    - An integer part, which are digits before the .
    - A decimal part, which are digits after the .
    - An exponential sign, which is the sign after the E or e
    - An exponent, which is the number after the exponential sign
    """
    # State Machine
    # =============
    #
    # BEGIN
    #   |--> 0 1 2 3 4 5 6 7 8 9 --> READ_INTEGER
    #   |--> .                   --> READ_DECIMAL
    #
    # READ_INTEGER
    #   |--> 0 1 2 3 4 5 6 7 8 9 --> READ_INTEGER
    #   |--> .                   --> READ_DECIMAL
    #   |--> E e                 --> READ_EXPONENTIAL_SIGN
    #
    # READ_DECIMAL
    #   |--> 0 1 2 3 4 5 6 7 8 9 --> READ_DECIMAL
    #   |--> E e                 --> READ_EXPONENTIAL_SIGN
    #
    # READ_EXPONENTIAL_SIGN
    #   |--> + -                 --> READ_EXPONENT
    #   |--> 0 1 2 3 4 5 6 7 8 9 --> READ_EXPONENT
    #
    # READ_EXPONENT
    #   |--> 0 1 2 3 4 5 6 7 8 9 --> READ_EXPONENT

    # Conventions of these state functions:
    # - Returning non-None 'accepts' the given character, and uses the returned
    #   function as the new state.
    # - Returning None terminates the number, not accepting the given input
    #
    # Note that 'None' is given to the function if the input stream is exhausted,
    # so that the state can check whether or not it is allowed to be the end state.
    #
    # In order to explicitly 'reject' a character, raising a SyntaxError is 
    # necessary.

    def begin(char):
        "Picks out the starting state from the first character"
        if char in DIGITS:
            return read_integer
        elif char == '.':
            return read_decimal
        else:
            raise SyntaxError('Invalid start to numeric literal: {}'.format(char))

    def read_integer(char):
        if char in DIGITS:
            return read_integer
        elif char == '.':
            return read_decimal
        elif char is not None and char in 'Ee':
            return read_exponential_sign

    def read_decimal(char):
        if char is not None and char in DIGITS:
            return read_decimal
        elif char is not None and char in 'Ee':
            return read_exponential_sign
        elif char == '.':
            raise SyntaxError('More than one decimal point in number literal')

    def read_exponential_sign(char):
        if char is not None and char in DIGITS:
            return read_exponent
        elif char is not None and char in '+-':
            # There isn't a 'READ_EXPONENT_TENTATIVE' state in the state diagram
            # given above, so what gives? Well, if the state machine above
            # were implemented directly, it would allow monstrosities like the
            # following to rear their ugly heads:
            #
            #   2.2e-
            #
            # That is, when we read the sign, the next state is 'READ_EXPONENT'
            # according to the diagram, which allows its input to be None. But,
            # if the sign is there, then we can't be sure the number is really
            # valid! So, this artificial 'READ_EXPONENT_TENTATIVE' state is mean
            # to patch up that hole - if it is given None, then it will die, unlike
            # 'READ_EXPONENT'.
            return read_exponent_tentative
        else:
            raise SyntaxError('Expected sign or digit after E')

    def read_exponent_tentative(char):
        if char is None or char not in DIGITS:
            raise SyntaxError('Expected exponent after exponential sign')
        return read_exponent(char)

    def read_exponent(char):
        if char is not None and char in DIGITS:
            return read_exponent

    # Note that I *could* just call float() on the parsed output, but it would
    # just be duplicating our work here, and it isn't difficult once the number
    # has been parsed.
    integer_part = 0

    decimal_part = 0
    # The 'scale' of the next number, which decreases as more digits are added.
    decimal_multiplier = 0.1

    exponent_sign = +1
    exponent_part = 0

    char = stream.popleft()
    state = begin(char)
    if state is read_integer:
        integer_part *= 10
        integer_part += NUM_TO_INT[char]
    elif state is read_decimal:
        # Ignore this, since the only way this can happen is if the first
        # character is the '.', and we don't consume that.
        pass

    while stream and (state is not None):
        char = stream[0]
        old_state = state
        state = state(char)

        # Only consume the character if the state explicitly handles it,
        # because we don't want to accidentally consume things like ')'
        # which are significant to the syntax.
        if state is not None:
            stream.popleft()

            # Why use NUM_TO_INT vs int()? Because int() is approximately twice
            # as slow as using a dict, for translating single digits into integers
            # (according to a quick timeit benchmark). No point slowing things down
            # unnecessarily, since the slower alternative really isn't any simpler.
            if old_state is read_integer and char in DIGITS:
                integer_part *= 10
                integer_part += NUM_TO_INT[char]
            elif old_state is read_decimal and char in DIGITS:
                decimal_part += NUM_TO_INT[char] * decimal_multiplier
                decimal_multiplier /= 10
            elif old_state is read_exponential_sign and char in '+-':
                exponent_sign = -1 if char == '-' else +1
            elif old_state is read_exponential_sign and char in DIGITS:
                exponent_part *= 10
                exponent_part += NUM_TO_INT[char]
            elif old_state in (read_exponent_tentative, read_exponent):
                exponent_part *= 10
                exponent_part += NUM_TO_INT[char]

    if state is not None:
        # In this case, we hit the end of the expression, rather than the
        # number running out 'naturally'. Ensure that the final state will
        # allow this. We don't care about its return state - just that it doesn't
        # throw a SyntaxError.
        state(None)

    value = (integer_part + decimal_part) * (10 ** (exponent_sign * exponent_part))
    return NumberToken(value)

def lex_name(stream):
    """
    Lexes a name, which can consist of a letter, followed by any number
    of letters or numbers.
    """
    # READ_FIRST
    # |--> A B C ... X Y Z a b c ... x y z                 --> READ_REST
    #
    # READ_REST
    # |--> A B C ... X Y Z a b c ... x y z 0 1 2 ... 7 8 9 --> READ_REST

    # For the ideas behind this, see lex_number for an idea of how
    # these functions work together to make the state machine.
    def read_first(char):
        if char in LETTERS:
            return read_rest
        elif char is None:
            raise SyntaxError('Expected name, but hit end of expression')
        else:
            raise SyntaxError('{} is an invalid first character to a name'.format(char))

    def read_rest(char):
        if char in LETTERS or char in DIGITS:
            return read_rest
        elif char in SPACES:
            return None

    state = read_first
    buffer = ''
    while stream and (state is not None):
        char = stream[0]
        state = state(char)
        
        if state is not None:
            buffer += char
            stream.popleft()

    if state is not None:
        state(None)

    return NameToken(buffer)

def lex(expr):
    """
    Converts the expression into a list of tokens.
    """
    char_stream = deque(expr)
    while char_stream:
        char = char_stream[0]
        if char in DIGITS or char == '.':
            yield lex_number(char_stream)
        elif char in LETTERS:
            yield lex_name(char_stream)
        elif char in OPERATORS:
            char_stream.popleft()
            operator = SYMBOL_TO_OPERATOR[char]
            yield OperatorToken(operator)
        elif char == ',':
            char_stream.popleft()
            yield CommaToken()
        elif char == '(':
            char_stream.popleft()
            yield BeginGroup()
        elif char == ')':
            char_stream.popleft()
            yield EndGroup()
        elif char in SPACES:
            char_stream.popleft()
        else:
            raise SyntaxError('Unexpected character: "{}"'.format(char))

##### Parser #####
class LookaheadIterator:
    """
    An iterator which allows for a single token of lookahead.
    """
    def __init__(self, iterable):
        self.iterator = iter(iterable)
        self.has_lookahead = False
        self.lookahead = None
        self.finished = False
    
    def __iter__(self):
        return self

    def __next__(self):
        if self.finished:
            raise StopIteration
        elif self.has_lookahead:
            self.has_lookahead = False
            return self.lookahead
        else:
            try:
                return next(self.iterator)
            except StopIteration:
                self.finished = True
                raise

    def peek(self):
        """
        Gets the next element without consuming it.

        Note that if no element is available, then a StopIteration exception is thrown.
        """
        if self.finished:
            raise StopIteration

        if self.has_lookahead:
            return self.lookahead
        else:
            try:
                self.lookahead = next(self.iterator)
            except StopIteration:
                self.finished = True
                raise
            self.has_lookahead = True
            return self.lookahead

class Parser:
    """
    The core of the Pratt parser, which reads in tokens and builds expressions
    using those tokens.
    """
    def __init__(self, stream):
        self.stream = LookaheadIterator(stream)
        self.stream_iter = iter(self.stream)

    def next_token(self):
        """
        Gets the next token, or None if no more tokens follow.
        """
        try:
            return next(self.stream_iter)
        except StopIteration:
            return None

    def peek_token(self):
        """
        Gets the next token, without consuming it, or None if not tokens follow.
        """
        try:
            return self.stream.peek()
        except StopIteration:
            return None

    def peek_precedence(self, limit):
        """
        Gets either:

        - The next token which has a precedence above the limit.
        - None, if the next token's precedence is too high, or there are no
          tokens left.

        Why above the limit? Well, this is because we want to ensure that
        whatever gets returned from here binds more tightly than whatever
        the resulting expression is getting sent back to. 

        If we're being called by a '+' operator, then we need to ensure
        that any '*' we come across (in general, anything with a higher precedence
        than '+') are processed, so that the order of operations is preserved.
        """
        next_tok = self.peek_token()
        if next_tok is None:
            return None
        else:
            precedence = token_precedence(next_tok, prefix=False)
            if precedence > limit:
                # Consume it, so the caller doesn't have to
                self.next_token()
                return next_tok
            else:
                return None

    def parse(self, precedence_min=-1):
        """
        Parses an expression, using the given precedence as the minimum bound. 
        By default, the entire expression will be parsed.
        """
        tok = self.next_token()
        if tok is None:
            return None

        expr = parse_prefix(tok, self)
        tok = self.peek_precedence(precedence_min)
        while tok is not None:
            expr = parse_infix(tok, expr, self)
            tok = self.peek_precedence(precedence_min)

        return expr

def evaluate(expr):
    "Evaluates an expression."
    toks = lex(expr)
    parser = Parser(toks)
    expr = parser.parse()
    if expr is None:
        return float('NaN')
    else:
        try:
            return evaluate_expr(expr)
        except ValueError:
            return float('NaN')

if __name__ == '__main__':
    while True:
        expr = input('> ')
        try:
            print('=', evaluate(expr))
        except Exception as ex:
            print('...', ex)
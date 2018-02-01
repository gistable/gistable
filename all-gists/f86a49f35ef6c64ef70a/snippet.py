from collections import namedtuple
from functools import reduce

State = namedtuple('State', ['value', 'remaining'])

def identity(x):
    return x

def compose(functions):
    return reduce(lambda f, g: lambda x: f(g(x)), functions, identity)

class ParseFail(Exception):
    def __init__(self, state, expected):
        self.state = state
        self.expected = expected

    def __str__(self):
        return 'Expected ' + self.expected

def char_satisfies(pred, name):
    def parser(state):
        if len(state.remaining) > 0 and pred(state.remaining[0]):
            return State(state.value + [state.remaining[0]], state.remaining[1:])
        raise ParseFail(state, expected=name)
    return parser

def pure(x):
    def parser(state):
        return State(state.value + [x], state.remaining)
    return parser

def char(x):
    return char_satisfies(lambda c: c == x, 'character "{}"'.format(x))

any_char = char_satisfies(lambda _: True, 'any character')

def one_of(chars):
    return char_satisfies(lambda c: c in chars, 'one of ' + ','.join(chars))

def none_of(chars):
    return char_satisfies(lambda c: c not in chars, 'none of ' + ','.join(chars))

def sequence(parsers):
    return compose(reversed(parsers))

def maybe(parser):
    def new_parser(state):
        try:
            return parser(state)
        except ParseFail:
            return State(state.value, state.remaining)
    return new_parser


def many(parser):
    def new_parser(state):
        while True:
            try:
                state = parser(state)
            except ParseFail:
                return state
    return new_parser

def choose(parsers):
    def new_parser(state):
        for parser in parsers[:-1]:
            try:
                return parser(state)
            except ParseFail:
                pass
        return parsers[-1](state)
    return new_parser

def eof(state):
    if state.remaining == '':
        return state
    raise ParseFail(state, expected='EOF')


def text(parser):
    def new_parser(state):
        new_state = parser(State([], state.remaining))
        return State(state.value + [''.join(new_state.value)], new_state.remaining)
    return new_parser

def many1(parser):
    return sequence([parser, many(parser)])

letter = char_satisfies(str.isalpha, 'letter')

digit = char_satisfies(str.isdigit, 'digit')

word = text(many1(letter))

number = text(many1(digit))

def discard(parser):
    def new_parser(state):
        new_state = parser(state)
        return State(state.value, new_state.remaining)
    return new_parser

whitespace = char_satisfies(str.isspace, 'whitespace')

ws = discard(many(whitespace))

def token(parser):
    return sequence([ws, parser, ws])

def between(left, right, middle):
    return sequence([discard(left), middle, discard(right)])


def double_quoted(parser):
    return between(char('"'), char('"'), parser)


def sep_by1(separator, parser):
    return sequence([parser, many(sequence([separator, parser]))])

def sep_by(separator, parser):
    return maybe(sep_by1(separator, parser))

def coerce(coercion, parser):
    def new_parser(state):
        new_state = parser(State([], state.remaining))
        return State(state.value + [coercion(new_state.value)], new_state.remaining)
    return new_parser


def as_tuple(parser):
    return coerce(tuple, parser)

def as_list(parser):
    return coerce(list, parser)

string = double_quoted(text(many(none_of(['"']))))

key = string

class Dict(object):
    def __init__(self, impl=None):
        self.impl = impl

    def __call__(self, state):
        return self.impl(state)

dict_ = Dict()

print(id(dict_))
value = choose([string, number, dict_])

key_value = as_tuple(sequence([text(token(key)), discard(char(':')), token(value)]))

dict_.impl = as_list(between(char('{'), char('}'), sep_by(token(char(',')), key_value)))
print(id(dict_))
between(char('"'), char('"'), number)(State([], '"932"'))

sep_by(token(char(',')), number)(State([], '3  ,  4,  5'))

value(State([], '{"ab   ce _ d": 9, "no": 10}'))

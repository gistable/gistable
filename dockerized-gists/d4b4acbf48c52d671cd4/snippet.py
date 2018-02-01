# -*- coding: utf8 -*-
import pytest


ADDITION = '+'
SUBTRACTION = '-'
MULTIPLICATION = '*'
DIVISION = '/'
MODULO = '%'


class RPN(object):
    OPERATORS = (ADDITION, SUBTRACTION, MULTIPLICATION, DIVISION, MODULO)

    def __init__(self):
        self.stack = []

    def calc(self, string):
        self.stack = []
        for s in string.split(' '):
            self.process(s)
        return self.stack[0]

    def process(self, string):
        if self.is_num(string):
            self.append(string)
        elif self.is_operator(string):
            self.operation(string)
        else:
            raise Exception('Unknown string: %s', string)

    def append(self, string):
        self.stack.append(int(string))

    def operation(self, string):
        y, x = self.stack.pop(-1), self.stack.pop(-1)
        if string == ADDITION:
            self.stack.append(x + y)
        elif string == SUBTRACTION:
            self.stack.append(x - y)
        elif string == MULTIPLICATION:
            self.stack.append(x * y)
        elif string == DIVISION:
            self.stack.append(x / y)
        elif string == MODULO:
            self.stack.append(x % y)

    @staticmethod
    def is_num(string):
        return string.isdigit()

    def is_operator(self, string):
        return string in self.OPERATORS


@pytest.fixture
def rpn():
    return RPN()


@pytest.mark.parametrize(
    'string,expected',
    [
        ('1', True),
        ('2', True),
        ('3', True),
        ('0', True),
        ('-', False),
        (' ', False),
        ('o', False),
    ]
)
def test_is_num(string, expected):
    assert RPN.is_num(string) is expected


@pytest.mark.parametrize(
    'string,expected',
    [
        ('*', True),
        ('-', True),
        ('+', True),
        ('/', True),
        ('%', True),
        (' ', False),
        ('o', False),
    ]
)
def test_is_operator(string, expected):
    assert RPN().is_operator(string) is expected


@pytest.mark.parametrize(
    'expression,expected',
    (
        ('5 8 3 + *', 55),
        ('8 2 5 * + 1 3 2 * + 4 - /', 6)
    )
)
def test_calc(rpn, expression, expected):
    assert rpn.calc(expression) == expected


@pytest.mark.parametrize(
    'stack,operation_string,expected',
    (
        ([3, 2, 2], '+', [3, 4]),
        ([9, 6, 2], '*', [9, 12]),
        ([6, 3], '/', [2]),
        ([64, 4], '%', [0]),
    )
)
def test_operation(rpn, stack, operation_string, expected):
    rpn.stack = stack
    rpn.operation(operation_string)
    assert rpn.stack == expected


def test_process(rpn):
    rpn.process('5')
    assert rpn.stack == [5]
    rpn.process('4')
    assert rpn.stack == [5, 4]
    rpn.process('*')
    assert rpn.stack == [20]

    with pytest.raises(Exception):
        rpn.process(' ')

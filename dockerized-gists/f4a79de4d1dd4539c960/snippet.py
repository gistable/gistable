#!/usr/bin/python3

import operator
import re

number_re = re.compile('^\d+')
operator_or_paren = re.compile('^[()+*-/]')

OPERATORS = {'+': (1, operator.add), '-': (1, operator.sub),
             '*': (2, operator.mul), '/': (2, operator.truediv)}


def eval_(formula):
    def parse(formula_string):
        skipn = 0
        for i in range(len(formula_string)):
            if skipn:
                skipn -= 1
                continue
            number = number_re.match(formula_string[i:])
            if number:
                end = number.end()
                yield float(number.string[:end])
                skipn = end - 1

            op = operator_or_paren.match(formula_string[i:])
            if op:
                yield op.string[0]

    def shunting_yard(parsed_formula):
        stack = []
        for token in parsed_formula:
            if token in OPERATORS:
                while stack and stack[-1] != "(" and OPERATORS[token][0] <= OPERATORS[stack[-1]][0]:
                    yield stack.pop()
                stack.append(token)
            elif token == ")":
                while stack:
                    x = stack.pop()
                    if x == "(":
                        break
                    yield x
            elif token == "(":
                stack.append(token)
            else:
                yield token
        while stack:
            yield stack.pop()

    def calc(polish):
        stack = []
        for token in polish:
            if token in OPERATORS:
                y, x = stack.pop(), stack.pop()
                stack.append(OPERATORS[token][1](x, y))
            else:
                stack.append(token)
        return stack[0]

    return calc(shunting_yard(parse(formula)))
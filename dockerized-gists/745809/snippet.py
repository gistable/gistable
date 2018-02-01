# problem: http://club.filltong.net/codingdojo/27611
# coded by jong10

import unittest

# infix to prefix(s-expression)
# modified from http://news.ycombinator.com/item?id=284954
def parse(s):
    for operator in ["+-", "*/"]:
        depth = 0
        for p in xrange(len(s) - 1, -1, -1):
            if s[p] == ')': depth += 1
            if s[p] == '(': depth -= 1
            if not depth and s[p] in operator:
                return (s[p], parse(s[:p]), parse(s[p+1:]))
    s = s.strip()
    if s[0] == '(':
        return parse(s[1:-1])
    return s

# s-expression has the '_' ?
def has_x(expr):
    if getattr(expr, '__iter__', False):
        return reduce(lambda x, y: x + y > 0, (has_x(e) for e in expr))
    else:
        return expr == '_'

# evaluate the s-expression without '_'
def evaluate(e):
    if getattr(e, '__iter__', False):
        return eval("%s%s%s" % (evaluate(e[1]), e[0], evaluate(e[2])))
    else:
        return e

# reverse of operator
REVERSE = {'+': '-', '-': '+', '*': '/', '/': '*'}

# find number '_' of equation
def find_number(expr):
    l, r = (parse(x) for x in expr.split('='))
    if has_x(r):
        l, r = r, l  # swap
    r = evaluate(r)
    while len(l) > 1 or len(r) > 1:
        if l == '_':
            break
        op = REVERSE[l[0]]
        if l[0] in '+*':
            if has_x(l[2]):
                move, other = 1, 2
            else:
                move, other = 2, 1
            e = (op, r, l[move])
            l, r = l[other], str(evaluate(e))
        else:
            move, other = 2, 1
            e = (op, r, l[move])
            if has_x(l[move]):
                l, r = str(evaluate(l[other])), e
                l, r = r, l
            else:
                l, r = l[other], str(evaluate(e))
    return eval(r)

# testcase
class TestFindNumber(unittest.TestCase):
    def test_find_number(self):
        self.assertEqual(find_number("_ + 2 = 12"), 10)
        self.assertEqual(find_number("( _ * 2 ) + 10 = 20"), 5)
        self.assertEqual(find_number("(3 + _) / 3 + 4 = 10"), 15)
        self.assertEqual(find_number("3 - _ = 10"), -7)
        self.assertEqual(find_number("3 - 103 = _ / 10 + 4"), -1040)
        self.assertEqual(find_number("10 = _"), 10)
        self.assertEqual(find_number("_ + 3.14 = 5.1234"), 1.9834)

if __name__ == '__main__':
    unittest.main()

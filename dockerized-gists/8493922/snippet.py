# simple math expression pratt parser

def lexer(s):
    '''token generator'''
    ix = 0
    while ix < len(s):
        if s[ix].isspace(): ix += 1
        elif s[ix] in "+-*/()":
            yield s[ix]; ix += 1
        elif s[ix].isdigit():
            jx = ix + 1
            while jx < len(s) and s[jx].isdigit(): jx += 1
            yield s[ix:jx]; ix = jx
        else:
            raise Exception("invalid character at %d: '%s'" % (ix, s[ix]))
    while True:
        yield ""


# construct a simple pratt parser
def make_op_parselet(op, precedence):
    def _parse(parse_func, left):
        right = parse_func(precedence)
        return (left, op, right)
    _parse.precedence = precedence
    return _parse

def make_group_parselet():
    def _parse(parse_func, consume_func):
        grouped = parse_func()
        consume_func(')')
        return grouped
    return _parse

def parse(s):
    tokens = lexer(s)

    group_parselet = make_group_parselet()
    op_parselets = {
        '+' : make_op_parselet('+', 1),
        '-' : make_op_parselet('-', 1),
        '*' : make_op_parselet('*', 2),
        '/' : make_op_parselet('/', 2),
    }

    # workaround the nonlocal
    parse.next_token = tokens.next()

    def consume(what=None):
        t = parse.next_token
        parse.next_token = tokens.next()
        if what is not None and t != what:
            raise Exception("expect %s, get %s" % (what, t))
        return t

    def next_precedence():
        if parse.next_token and parse.next_token in '+-*/':
            return op_parselets[parse.next_token].precedence
        return 0

    def parse_expr(precedence=0):
        t = consume()
        if t.isdigit():
            left = t
        elif t == '(':
            left = group_parselet(parse_expr, consume)
        else:
            raise Exception("unexpected prefix token %s" % t)

        while precedence < next_precedence():
            t = consume()
            left = op_parselets[t](parse_expr, left)

        return left

    return parse_expr()


if __name__ == '__main__':
    from json import dumps
    print dumps(parse("1 + (2 - 3) * 456"), indent=4)
    print dumps(parse("1 * (2 * 3) / 5 + (2 - 3) * 456"), indent=4)

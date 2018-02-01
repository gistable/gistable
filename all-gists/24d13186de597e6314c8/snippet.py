import itertools, re, sys

ops = (lambda x, y: x + y, lambda x, y: x - y, lambda x, y: x * y, lambda x, y: x / y)

def recurse(so_far, operands, desired):
    if not operands:
        return '' if so_far == desired else None
    for op, op_char in itertools.izip(ops, '+-*/'):
        expr = recurse(op(so_far, operands[0]), operands[1:], desired)
        if isinstance(expr, basestring):
            return ' %c %d%s' % (op_char, operands[0], expr)

inputs = [float(i) for i in re.findall('\S+', sys.stdin.readline())]
for permuted in itertools.permutations(inputs[:-1]):
    result = recurse(permuted[0], permuted[1:], inputs[-1])
    if result:
        print '%d%s' % (permuted[0], result)
        sys.exit()
print 'Invalid'
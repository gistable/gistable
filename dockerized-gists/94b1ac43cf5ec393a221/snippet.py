def getdata(filename):
    d = dict()
    with open(filename, "r") as f:
        for line in f.readlines():
            line = line.replace('\n', '').split(' -> ')
            d[line[1]] = line[0]
    return d
def evaluate(var, d):
    try:
        val = int(var)
        return val
    except:
        pass
    try:
        val = evaluate((d[var]), d)
        d[var] = val
        return val
    except:
        pass
    s = d[var].split()
    l = len(s)
    if l == 2:
        val = 2**16-1-evaluate(s[1], d)
        d[var] = val
        return val
    else:
        op1, op , op2 = s[0], s[1], s[2]
        if op == "AND":
            d[var] = evaluate(op1, d) & evaluate(op2, d)
        if op == "OR":
            d[var] = evaluate(op1, d) | evaluate(op2, d)
        if op == "LSHIFT":
            d[var] = evaluate(op1, d) << evaluate(op2, d)
        if op == "RSHIFT":
            d[var] = evaluate(op1, d) >> evaluate(op2, d)
        return d[var]


if __name__ == '__main__':
    filename = 'input.txt'
    data = getdata(filename)
    answerPart1 = evaluate('a', dict(data))
    print "Answer to 1st part", answerPart1
    data['b'] = 956
    print "Answer to IInd part", evaluate('a', data)

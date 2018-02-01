def curryargs(arg=None, args=()):
    def _ca(next=None):
        return curryargs(next, args + (arg,))
    if arg:
        return _ca
    else:
        return args

def printargs(args):
    for arg in args:
        print(arg)
printargs(curryargs("1")("2")())
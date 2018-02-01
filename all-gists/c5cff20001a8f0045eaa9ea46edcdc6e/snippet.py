def fib():
    a, b = 0, 1
    while True:
        yield a
        a, b = b, a + b

        
def main():
    i = int(raw_input())
    if i is 0:
        return 0
    f = fib()
    for s in range(0, i + 1):
        if s == i:
            return next(f)
        else:
            next(f)


print main()
def inc(x):
    return x + 1

def pipe(val, *args):
    for func in args:
        val = func(val)
    return val
    
pipe(1, inc, inc, inc)

=> 4
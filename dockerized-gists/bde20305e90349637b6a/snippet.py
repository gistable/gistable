def int_to_tuple(num, base=4):
    result = ((),) * (num % base)
    if num >= base:
        result = (int_to_tuple(num // base, base),) + result
    return result
    
def tuple_to_int(tup, base=4):
    if len(tup) == 0:
        return 0
    return tuple_to_int(tup[0], base)*base + tup.count(())

def string_to_tuples(s, base=4):
    return tuple(int_to_tuple(ord(c), base) for c in s)

def tuples_to_string(tups, base=4):
    return ''.join(chr(tuple_to_int(t, base)) for t in tups)


# short lambda versions
i2t=lambda n,b=4:((i2t(n//b,b),)if n>=b else())+((),)*(n%b)
t2i=lambda t,b=4:0 if len(t)==0 else t2i(t[0],b)*b+t.count(())
s2t=lambda s,b=4:tuple(i2t(ord(c),b)for c in s)
t2s=lambda a,b=4:''.join(chr(t2i(t,b))for t in a)
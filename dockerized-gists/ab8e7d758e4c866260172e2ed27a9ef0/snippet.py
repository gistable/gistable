def do_some_work(x, y):
    return (x+y)/x

def loop_function(n):
    data = range(1, n)
    result = 0
    for a, b in zip(data, data[1:]):
        result += do_some_work(a, b)
    #print('loop function result: ' + str(result))


def loop_reduce(n):
    from functools import reduce
    data = range(1, n)
    result = reduce(lambda a,b: a + do_some_work(*b), zip(data, data[1:]), 0)
    #print('loop reduce result: ' + str(result))

def do_some_work2(arg):
    return (arg[0]+arg[1])/arg[0]

def loop_map(n):
    data = range(1,n)
    result = 0
    result = sum(map(do_some_work2, zip(data, data[1:])))

def do_some_work3(l):
    result = 0
    for x, y in l:
        result += (x+y)/x
    return result

def loop_pass(n):
    data = range(1, n)
    r = do_some_work3(zip(data, data[1:]))

def do_some_work4(l):
    return sum([(x+y)/x for x,y in l])

def do_some_work5(l):
    return sum(map(lambda x:sum(x), l))

def loop_pass_map(n):
    data = range(1, n)
    r = do_some_work4(zip(data, data[1:]))

def no_helper(n):
    data = range(1, n)
    result = sum([(x+y)/x for x,y in zip(data, data[1:])])


if __name__ == "__main__":
    from timeit import timeit
    print("BASE --------------> ", timeit(stmt="loop_function(10 ** 5)", 
        setup="from __main__ import loop_function;",
        number=10))
    
    print("REDUCE ------------> ", timeit(stmt="loop_reduce(10 ** 5)", 
        setup="from __main__ import loop_reduce;",
        number=10))
    
    print("MAP ------------> ", timeit(stmt="loop_map(10 ** 5)", 
        setup="from __main__ import loop_map;",
        number=10))
    
    print("PASS ------------> ", timeit(stmt="loop_pass(10 ** 5)", 
        setup="from __main__ import loop_pass;",
        number=10))
    
    print("PASS AND MAP ------------> ", timeit(stmt="loop_pass_map(10 ** 5)", 
        setup="from __main__ import loop_pass_map;",
        number=10))
    
    print("NO HELPER ------------> ", timeit(stmt="no_helper(10 ** 5)", 
        setup="from __main__ import no_helper;",
        number=10))
        
"""
BASE -------------->  0.41014268523293795
REDUCE ------------>  0.5462599329294733
MAP ------------>  0.40563402687439554
PASS ------------>  0.28740670038153726
PASS AND MAP ------------>  0.2716002247658047
NO HELPER ------------>  0.2697507819335503
"""
def double(i):
    return i*2

def increment(i):
    if i=='broken':
        return None
    return i+1

def flatten(listOfOptions):
    return reduce(list.__add__, listOfOptions)

def applyfn(input, fn):
    value = map(fn, input)
    if value == [None]:
        return []
    return value

def pipeline(functions, inputs):
    def input(item):
        return reduce(applyfn, functions, [item])
    return flatten(map(input, inputs))

print("{}".format(pipeline([increment, double],[1,'broken',2])))
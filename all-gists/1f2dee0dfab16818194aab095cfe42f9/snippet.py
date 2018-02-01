def log(f):
    def wrapper(*args, **kwargs):
        print "f address: ", f
        return f(*args, **kwargs)
    return wrapper

def add(a, b):
    return a + b

add = log(add)
add(1, 1)
inner_add = add.__closure__[0].cell_contents
print inner_add(1, 1)
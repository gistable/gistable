def f(x = []):
    x.append(1)
    return x
print f() # [1]
print f() # [1, 1]
print f() # [1, 1, 1]
print f() # [1, 1, 1, 1]
def debug(msg):
    print("calling debug decorator")
    def actual_decorator(fn):
        print("calling actual_decorator")
        def wrapper(*args):
            print("calling wrapper with" + str(args))
            print(msg)
            print("calling " + fn.__name__)
            return fn(*args)
        print("returning wrapper")
        return wrapper
    print("returning actual_decorator")
    return actual_decorator

print("Decoration Time")

@debug("Let's multiply")
def mul(x, y):
    return x * y

print("\nCall Time")

print(mul(5, 2))

# ======
# Output
# ======
# Decoration Time
# calling debug decorator
# returning actual_decorator
# calling actual_decorator
# returning wrapper
# 
# Call Time
# calling wrapper with (5, 2)
# Let's multiply
# calling mul
# 10
# 

def omg():
    def inner(foo):
        # Works fine, purely by accident...
        return f

    # ...because the list comprehension leaks its variable in to the outer scope
    return [inner(f) for f in range(5)]


def broken():
    def inner(foo):
        # Raises a NameError...
        return f

    # ...because generators *don't* leak the iteration variable in to the outer scope
    return list(inner(f) for f in range(5))

# In my real code I meant to use 'foo' inside the 'inner' function but forgot to rename it from 'f'
# when copying some code around. I never noticed the mistake because the code still worked, and tests passed.
    

if __name__ == "__main__":
    print omg()
    print broken()
from inspect import signature

def auto_args(f):
    sig = signature(f)  # Get a signature object for the target:
    def replacement(self, *args, **kwargs):
        # Parse the provided arguments using the target's signature:
        bound_args = sig.bind(self, *args, **kwargs)
        # Save away the arguments on `self`:
        for k, v in bound_args.arguments.items():
            if k != 'self':
                setattr(self, k, v)
        # Call the actual constructor for anything else:
        f(self, *args, **kwargs)
    return replacement


class MyClass:
    @auto_args
    def __init__(self, a, b, c=None):
        pass

m = MyClass('A', 'B', 'C')
print(m.__dict__)
# {'a': 'A', 'b': 'B', 'c': 'C'}
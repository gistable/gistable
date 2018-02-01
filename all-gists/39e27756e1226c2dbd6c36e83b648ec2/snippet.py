"""
Simple example of manually performing "automatic" differentiation
"""
import numpy as np
from numpy import exp, sin, cos


def f(x, with_grad=False):
    # Need to cache intermediates from forward pass (might not use all of them).
    a = exp(x)
    b = a**2
    c = a + b
    d = exp(c)
    e = sin(c)
    f = d + e

    if not with_grad:
        return f

    # initialize all adjoints to zero. "Adjoints" are specifically the gradients
    # of intermediates wrt to the output variable. Often they are abbreviated
    # since they all are df_*.
    df_da = df_db = df_dc = df_dd = df_de = df_dx = 0

    # Loop thru rules in reverse order

    # f = d + e ==> two inputs -> two ajoint rules. (At the final output the
    # adjoints are just the local gradients.)
    df_dd = 1
    df_de = 1

    # e = sin(c)
    de_dc = cos(c)          # local gradient: how `e` changes with its input `c`
    df_dc += df_de * de_dc  # backprop: adjoint from `e` is "converted" into
                            # adjoint for `c` where `de/dc` is the "conversion
                            # factor" Note how the units match like in
                            # dimensional analysis: df/de * de/dc => df/dc. This
                            # is a useful sanity check.

    # d = exp(c)
    dd_dc = exp(c)
    df_dc += df_dd * dd_dc  # Note that because `c` is used twice in the program, its ajoint is a sum!

    # c = a + b ==> two inputs -> two ajoint rules
    dc_da = 1
    dc_db = 1
    df_da += df_dc * dc_da
    df_db += df_dc * dc_db

    # b = a**2
    db_da = 2*a
    df_da += df_db * db_da  # variable `a` is used twice so its adjoints sum, just like `c`

    # a = exp(x)
    da_dx = exp(x)
    df_dx += df_da * da_dx

    # Output the gradient of the input variable
    return f, df_dx


def main():
    from arsenal.math.checkgrad import fdcheck
    for x in np.random.uniform(-10, 3, size=10):
        x = np.array([x])
        fdcheck(lambda: f(x), x, f(x, with_grad=1)[1])


if __name__ == '__main__':
    main()
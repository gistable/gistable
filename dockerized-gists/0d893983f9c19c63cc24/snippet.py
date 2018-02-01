"""
This program compares ADAM vs AdaGrad. You can modify the function f and its gradient grad_f 
in the code, run the two algorithms and compare their convergence. For the simple function
f(x1, x2) = (x1 - 2) ** 2 + (x1 + 3) ** 2, (alpha = 0.1 and tolerence 1e-3)
AdaGrad converged at 2023 iterations, whereas ADAM required only 83!
"""

import numpy


def f(x):
    return ((x[0] - 2) ** 2) + ((x[1] + 3) ** 2)


def grad_f(x):
    # f(x,y) = (x-2)^2 + (y+3)^2
    # grad = 2(x-2) + 2(y+3)
    n = x.shape[0]
    g = numpy.zeros(n, dtype=float)
    g[0] = 2 * (x[0] - 2)
    g[1] = 2 * (x[1] + 3)
    return g


def ADAM(f, gf, n):
    alpha = 0.1
    b1 = 0.1
    b2 = 0.001
    e = 1e-8
    l = 1e-8
    T = 10000
    # Check convergence requirement
    if (1 - b1) ** 2 > numpy.sqrt(1 - b2):
        raise "Convergence Requirement Failed", ValueError
    theta = numpy.zeros(n, dtype=float)
    m = numpy.zeros(n, dtype=float)
    v = numpy.zeros(n, dtype=float)
    for t in range(1, T):
        b1_t = 1 - ((1 - b1) * (l ** (t - 1)))
        g = gf(theta)
        m = (b1_t * g) + ((1.0 - b1_t) * m)
        v = (b2 * g * g) + ((1.0 - b2) * v)
        mp = m / (1.0 - ((1.0 - b1) ** t))
        vp = v / (1.0 - ((1.0 - b2) ** t))
        for i in range(0, n):
            theta[i] -= ((alpha * mp[i]) / (numpy.sqrt(vp[i]) + e))
        grad_norm = numpy.linalg.norm(gf(theta))
        print "Itr = %d" % t
        print "theta =", theta
        print "f(theta) =", f(theta)
        print "grad_f(theta) =", gf(theta)
        print "norm(grad) =", grad_norm
        if grad_norm < 1e-3:
            return

    pass


def AdaGrad(f, gf, n):
    theta = numpy.zeros(n, dtype=float)
    gsqd = numpy.zeros(n, dtype=float)
    T = 10000
    alpha = 0.1
    e = 1e-8
    for t in range(1, T):
        g = gf(theta)
        gsqd += g * g
        for i in range(0, n):
            theta[i] -= alpha * g[i] / numpy.sqrt(gsqd[i] + e)
        grad_norm = numpy.linalg.norm(gf(theta))
        print "Itr = %d" % t
        print "theta =", theta
        print "f(theta) =", f(theta)
        print "grad_f(theta) =", gf(theta)
        print "norm(grad) =", grad_norm
        if grad_norm < 1e-3:
            return
    pass


def main():
    ADAM(f, grad_f, 2)
    #AdaGrad(f, grad_f, 2)
    pass


if __name__ == "__main__":
    main()

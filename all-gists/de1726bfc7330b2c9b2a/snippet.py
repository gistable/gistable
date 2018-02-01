"""
Newton's method
Author: Daniel Homola
Licence: BSD 3-clause
"""

from scipy.optimize import newton
from sklearn.utils.testing import assert_almost_equal

def f(x):
    return 6*x**5-5*x**4-4*x**3+3*x**2
def df(x):
    return 30*x**4-20*x**3-12*x**2+6*x

def dx(f, x):
    return abs(0-f(x))
    
def newtons_method(f, df, x0, e, print_res=False):
    delta = dx(f, x0)
    while delta > e:
        x0 = x0 - f(x0)/df(x0)
        delta = dx(f, x0)
    if print_res:
        print 'Root is at: ', x0
        print 'f(x) at root is: ', f(x0)
    return x0

def test_with_scipy(f, df, x0s, e):
    for x0 in x0s:
        my_newton = newtons_method(f, df, x0, e)
        scipy_newton = newton(f, x0, df, tol=e)
        assert_almost_equal(my_newton, scipy_newton, decimal=5)
        print 'Tests passed.'

if __name__ == '__main__':
    # run test
    x0s= [0, .5, 1]    
    test_with_scipy(f, df, x0s, 1e-5)
        
    for x0 in x0s:
        newtons_method(f, df, x0, 1e-10, True)
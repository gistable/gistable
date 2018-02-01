# coding: utf-8

# An attempt at implementing Bayesian optimization according to
# Brochu, Cora, and de Freitas' tutorial
# http://haikufactory.com/files/bayopt.pdf

from sklearn import gaussian_process
import numpy as np
import scipy.optimize, scipy.stats as st

def ucb_acq(sigma):
    """The upper-confidence-bound acquisition function with parameter sigma.
    
    To avoid over-exploration all the way off to infinity (where the
    variance is huge) I truncate the confidence term.
    """
    def acq(gp, best_y):
        def ev(x):
            y, ms = gp.predict([x], eval_MSE=True)
            return -(y[0] + sigma*max(np.abs(y[0]), np.sqrt(ms[0])))
        return ev
    return acq


def expected_improvement(gp, best_y):
    """The expected improvement acquisition function.

    The equation is explained in Eq (3) of the tutorial"""
    def ev(x):
        y, ms = gp.predict([x], eval_MSE=True)
        Z = (y[0] - best_y)/np.sqrt(ms[0])
        return -((y[0]-best_y)*st.norm.cdf(Z) + np.sqrt(ms[0])*st.norm.pdf(Z))
    return ev

def bayesopt(f, initial_x, acquisition, niter=100, debug=False):
    """The actual bayesian optimization function. 

    f is the very expensive function we want to optimize. 

    initial_x is a matrix of at least two data points (preferrably
    more, randomly sampled). 

    acquisition is the acquisiton function we want to use to find
    query points. 

    Note that doing simulated annealing as done here is a very bad
    idea, as we should be very careful about the domain."""
    X = initial_x
    y = [f(x) for x in initial_x]
    best_x = initial_x[np.argmax(y)]
    best_f = y[np.argmax(y)]
    print y
    gp = gaussian_process.GaussianProcess()
    for i in xrange(niter):
        gp.fit(np.array(X), np.array(y))
        new_x = scipy.optimize.anneal(acquisition(gp, best_f), best_x)[0]
        new_f = f(new_x)
        X.append(new_x)
        y.append(new_f)
        if new_f > best_f:
            best_f = new_f
            best_x = new_x
        if debug:
            print "iter", i, "best_x", best_x, best_f
    return best_x, best_f

if __name__ == '__main__':
    print "Running a completely silly example."
    def func(x):
        x = x[0] - 2.0
        return 20.0 - min(100.0, (x*x + np.abs(x)*np.sin(x)))
    print "With UCB:"
    X = [[-5.0, -1.0], [-12.0, 10.0]]
    bayesopt(func, X[:], ucb_acq(0.1), niter=10, debug=True)
    print "With EI:"
    bayesopt(func, X[:], expected_improvement, niter=10, debug=True)

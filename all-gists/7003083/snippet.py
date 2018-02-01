"""
Implementation of the beta-geometric/NBD (BG/NBD) model from '"Counting Your Customers" the Easy Way: An Alternative to
the Pareto/NBD Model' (Fader, Hardie and Lee 2005) http://brucehardie.com/papers/018/fader_et_al_mksc_05.pdf and
accompanying technical note http://www.brucehardie.com/notes/004/

Apache 2 License
"""
from math import log, exp

import numpy as np
from scipy.optimize import minimize

from scipy.special import gammaln

__author__ = 'JD Maturen'


def log_likelihood_individual(r, alpha, a, b, x, tx, t):
    """Log of the likelihood function for a given randomly chosen individual with purchase history = (x, tx, t) where
    x is the number of transactions in time period (0, t] and tx (0 < tx <= t) is the time of the last transaction"""
    ln_a1 = gammaln(r + x) - gammaln(r) + r * log(alpha)
    ln_a2 = gammaln(a + b) + gammaln(b + x) - gammaln(b) - gammaln(a + b + x)
    ln_a3 = -(r + x) * log(alpha + t)
    a4 = 0
    if x > 0:
        a4 = exp(log(a) - log(b + x - 1) - (r + x) * log(alpha + tx))
    return ln_a1 + ln_a2 + log(exp(ln_a3) + a4)


def log_likelihood(r, alpha, a, b, customers):
    """Sum of the individual log likelihoods"""
    # can't put constraints on n-m minimizer so fake them here
    if r <= 0 or alpha <= 0 or a <= 0 or b <= 0:
        return -np.inf
    return sum([log_likelihood_individual(r, alpha, a, b, x, tx, t) for x, tx, t in customers])


def maximize(customers):
    negative_ll = lambda params: -log_likelihood(*params, customers=customers)
    params0 = np.array([1., 1., 1., 1.])
    res = minimize(negative_ll, params0, method='nelder-mead', options={'xtol': 1e-8})
    return res


def fit(customers):
    res = maximize(customers)
    if res.status != 0:
        raise Exception(res.message)
    return res.x


def cdnow_customer_data(fname):
    data = []
    with open(fname) as f:
        f.readline()
        for line in f:
            data.append(map(float, line.strip().split(',')[1:4]))
    return data


def main():
    data = cdnow_customer_data('cdnow_customers.csv')
    r, alpha, a, b = fit(data)
    # fit according to the note
    print r, alpha, a, b
    print np.allclose([r, alpha, a, b], [.243, 4.414, .793, 2.426], 1e-2)


if __name__ == '__main__':
    main()

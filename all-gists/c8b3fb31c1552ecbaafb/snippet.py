from scipy.stats import binom


def mcnemar_midp(b, c):
    """
    Compute McNemar's test using the "mid-p" variant suggested by:
    
    M.W. Fagerland, S. Lydersen, P. Laake. 2013. The McNemar test for 
    binary matched-pairs data: Mid-p and asymptotic are better than exact 
    conditional. BMC Medical Research Methodology 13: 91.
    
    `b` is the number of observations correctly labeled by the first---but 
    not the second---system; `c` is the number of observations correctly 
    labeled by the second---but not the first---system.
    """
    n = b + c
    x = min(b, c)
    dist = binom(n, .5)
    p = 2. * dist.cdf(x)
    midp = p - dist.pmf(x)
    return midp
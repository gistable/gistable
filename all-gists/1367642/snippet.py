import numpy as NP

def _regress(x, y):
    """
    Compute the intercept and slope for y ~ C + \beta x
    """
    solution = NP.linalg.lstsq(NP.vstack((NP.ones(len(x)), x)).T, y)
    return solution[0]
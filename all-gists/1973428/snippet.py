def gauss_distr(mu, sigmaSquare, x):
    from math import sqrt, pi, e
    return (1 / sqrt(2 * pi * sigmaSquare)) * e ** ((-0.5) * (x - mu) ** 2 / sigmaSquare)
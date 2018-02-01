"""
Hilbert matrix using numpy. Contains:

  - hilb(n, m) : returns the Hilbert matrix of size (n, m)

  - invhilb(n) : returns the inverse of the Hilbert matrix of size (n, n)
"""
import numpy as np
from math import factorial

def binomial(n, k):
    """binomial(n, k): return the binomial coefficient (n k)."""

    if k < 0 or k > n:
        return 0
    if k == 0 or k == n:
        return 1
    return factorial(n) // (factorial(k) * factorial(n-k))

def hilb(n, m=0):
    """
    hilb   Hilbert matrix.
       hilb(n,m) is the n-by-m matrix with elements 1/(i+j-1).
       it is a famous example of a badly conditioned matrix.
       cond(hilb(n)) grows like exp(3.5*n).
       hilb(n) is symmetric positive definite, totally positive, and a
       Hankel matrix.

       References:
       M.-D. Choi, Tricks or treats with the Hilbert matrix, Amer. Math.
           Monthly, 90 (1983), pp. 301-312.
       N.J. Higham, Accuracy and Stability of Numerical Algorithms,
           Society for Industrial and Applied Mathematics, Philadelphia, PA,
           USA, 2002; sec. 28.1.
       M. Newman and J. Todd, The evaluation of matrix inversion
           programs, J. Soc. Indust. Appl. Math., 6 (1958), pp. 466-476.
       D.E. Knuth, The Art of Computer Programming,
           Volume 1, Fundamental Algorithms, second edition, Addison-Wesley,
           Reading, Massachusetts, 1973, p. 37.

       NOTE added in porting.  We do not use the function cauchy here to
       generate the Hilbert matrix.  That is done so we can unit test the
       the functions against each other.  Also, the function has been
       generalized to take by row and column sizes.  If only a row size
       is given, we assume a square matrix is desired.
    """
    if n < 1 or m < 0:
        raise ValueError("Matrix size must be one or greater")
    elif n == 1 and (m == 0 or m == 1):
        return np.array([[1]])
    elif m == 0:
        m = n

    return 1. / (np.arange(1, n + 1) + np.arange(0, m)[:, np.newaxis])


def invhilb(n):
    """
    invhilb   Generate the exact inverse of the n-by-n Hilbert matrix.

    Limitations:
    Comparing invhilb(n) with inv(hilb(n)) involves the effects of two or
    three sets of roundoff errors:

        - The errors caused by representing hilb(n)
        - The errors in the matrix inversion process
        - The errors, if any, in representing invhilb(n)

    It turns out that the first of these, which involves representing
    fractions like 1/3 and 1/5 in floating-point, is the most significant.
    """
    H = np.empty((n, n))
    for i in range(n):
        for j in range(n):
            H[i, j] = ((-1)**(i + j)) * (i + j + 1) * binomial(n + i, n - j - 1) * \
             binomial(n + j, n - i - 1) * binomial(i + j, i) ** 2
    return H

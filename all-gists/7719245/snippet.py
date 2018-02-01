#  Copyright (C) 2013 Istituto per l'Interscambio Scientifico I.S.I.
#  You can contact us by email (isi@isi.it) or write to:
#  ISI Foundation, Via Alassio 11/c, 10126 Torino, Italy.
#
#  This work is licensed under a Creative Commons 4.0
#  Attribution-NonCommercial-ShareAlike License
#  You may obtain a copy of the License at
#  http://creativecommons.org/licenses/by-nc-sa/4.0/
#
#  This program was written by Andre Panisson <panisson@gmail.com> at
#  the Data Science Lab of the ISI Foundation,
#  and its development was partly supported by
#  the EU FET project MULTIPLEX (grant number 317532).
#
'''
Nonnegative Tensor Factorization, based on the Matlab source code
available at Jingu Kim's (jingu.kim@gmail.com) home page:

    https://github.com/kimjingu/nonnegfac-matlab
    https://github.com/kimjingu/nonnegfac-python

Requires the installation of Numpy and Scikit-Tensor
    (https://github.com/mnick/scikit-tensor).

For examples, see main() function.

This code comes with no guarantee or warranty of any kind.
Created on Nov 2013

@author: Andre Panisson
@contact: panisson@gmail.com
@organization: ISI Foundation, Torino, Italy
'''

import numpy as np
from numpy import zeros, ones, diff, kron, tile, any, all, linalg
import numpy.linalg as nla
import time
from sktensor import ktensor


def find(condition):
    "Return the indices where ravel(condition) is true"
    res, = np.nonzero(np.ravel(condition))
    return res


def normalEqComb(AtA, AtB, PassSet=None):
    """ Solve many systems of linear equations using combinatorial grouping.

    M. H. Van Benthem and M. R. Keenan, J. Chemometrics 2004; 18: 441-450

    Parameters
    ----------
    AtA : numpy.array, shape (n,n)
    AtB : numpy.array, shape (n,k)

    Returns
    -------
    Z : numpy.array, shape (n,k) - solution
    """
    if AtB.size == 0:
        Z = np.zeros([])
    elif (PassSet == None) or np.all(PassSet):
        Z = nla.solve(AtA, AtB)
    else:
        Z = np.zeros(AtB.shape)
        if PassSet.shape[1] == 1:
            if np.any(PassSet):
                cols = PassSet.nonzero()[0]
                Z[cols] = nla.solve(AtA[np.ix_(cols, cols)], AtB[cols])
        else:
            #
            # Both _column_group_loop() and _column_group_recursive() work well.
            # Based on preliminary testing,
            # _column_group_loop() is slightly faster for tiny k(<10), but
            # _column_group_recursive() is faster for large k's.
            #
            grps = _column_group_recursive(PassSet)
            for gr in grps:
                cols = PassSet[:, gr[0]].nonzero()[0]
                if cols.size > 0:
                    ix1 = np.ix_(cols, gr)
                    ix2 = np.ix_(cols, cols)
                    #
                    # scipy.linalg.cho_solve can be used instead of numpy.linalg.solve.
                    # For small n(<200), numpy.linalg.solve appears faster, whereas
                    # for large n(>500), scipy.linalg.cho_solve appears faster.
                    # Usage example of scipy.linalg.cho_solve:
                    # Z[ix1] = sla.cho_solve(sla.cho_factor(AtA[ix2]),AtB[ix1])
                    #
                    Z[ix1] = nla.solve(AtA[ix2], AtB[ix1])
    return Z


def _column_group_recursive(B):
    """ Given a binary matrix, find groups of the same columns
        with a recursive strategy

    Parameters
    ----------
    B : numpy.array, True/False in each element

    Returns
    -------
    A list of arrays - each array contain indices of columns that are the same.
    """
    initial = np.arange(0, B.shape[1])
    return [a for a in column_group_sub(B, 0, initial) if len(a) > 0]


def column_group_sub(B, i, cols):
    vec = B[i][cols]
    if len(cols) <= 1:
        return [cols]
    if i == (B.shape[0] - 1):
        col_trues = cols[vec.nonzero()[0]]
        col_falses = cols[(-vec).nonzero()[0]]
        return [col_trues, col_falses]
    else:
        col_trues = cols[vec.nonzero()[0]]
        col_falses = cols[(-vec).nonzero()[0]]
        after = column_group_sub(B, i + 1, col_trues)
        after.extend(column_group_sub(B, i + 1, col_falses))
    return after


def nnlsm_activeset(A, B, overwrite=0, isInputProd=0, init=None):
    """
    Nonnegativity Constrained Least Squares with Multiple Righthand Sides
         using Active Set method

    This function solves the following problem: given A and B, find X such that
               minimize || AX-B ||_F^2 where X>=0 elementwise.

    Reference:
         Charles L. Lawson and Richard J. Hanson,
               Solving Least Squares Problems,
               Society for Industrial and Applied Mathematics, 1995
         M. H. Van Benthem and M. R. Keenan,
               Fast Algorithm for the Solution of Large-scale
               Non-negativity-constrained Least Squares Problems,
               J. Chemometrics 2004; 18: 441-450

    Based on the Matlab version written by Jingu Kim (jingu.kim@gmail.com)
                  School of Computational Science and Engineering,
                  Georgia Institute of Technology

    Parameters
    ----------
    A : input matrix (m x n) (by default),
        or A'*A (n x n) if isInputProd==1

    B : input matrix (m x k) (by default),
        or A'*B (n x k) if isInputProd==1

    overwrite : (optional, default:0)
        if turned on, unconstrained least squares solution is computed
        in the beginning

    isInputProd : (optional, default:0)
        if turned on, use (A'*A,A'*B) as input instead of (A,B)

    init : (optional) initial value for X

    Returns
    -------
    X : the solution (n x k)

    Y : A'*A*X - A'*B where X is the solution (n x k)
    """

    if isInputProd:
        AtA = A
        AtB = B
    else:
        AtA = A.T.dot(A)
        AtB = A.T.dot(B)

    n, k = AtB.shape
    MAX_ITER = n * 5

    # set initial feasible solution
    if overwrite:
        X = normalEqComb(AtA, AtB)
        PassSet = (X > 0).copy()
        NotOptSet = any(X < 0)
    elif init is not None:
        X = init
        X[X < 0] = 0
        PassSet = (X > 0).copy()
        NotOptSet = ones((1, k), dtype=np.bool)
    else:
        X = zeros((n, k))
        PassSet = zeros((n, k), dtype=np.bool)
        NotOptSet = ones((1, k), dtype=np.bool)

    Y = zeros((n, k))
    if (~NotOptSet).any():
        Y[:, ~NotOptSet] = AtA.dot(X[:, ~NotOptSet]) - AtB[:, ~NotOptSet]
    NotOptCols = find(NotOptSet)

    bigIter = 0

    while NotOptCols.shape[0] > 0:
        bigIter = bigIter + 1
        # set max_iter for ill-conditioned (numerically unstable) case
        if ((MAX_ITER > 0) & (bigIter > MAX_ITER)):
            break

        Z = normalEqComb(AtA, AtB[:, NotOptCols], PassSet[:, NotOptCols])

        Z[abs(Z) < 1e-12] = 0  # for numerical stability.

        InfeaSubSet = Z < 0
        InfeaSubCols = find(any(InfeaSubSet, axis=0))
        FeaSubCols = find(all(~InfeaSubSet, axis=0))

        if InfeaSubCols.shape[0] > 0:               # for infeasible cols
            ZInfea = Z[:, InfeaSubCols]
            InfeaCols = NotOptCols[InfeaSubCols]

            Alpha = zeros((n, InfeaSubCols.shape[0]))
            Alpha[:] = np.inf

            ij = np.argwhere(InfeaSubSet[:, InfeaSubCols])
            i = ij[:, 0]
            j = ij[:, 1]

            InfeaSubIx = np.ravel_multi_index((i, j), Alpha.shape)
            if InfeaCols.shape[0] == 1:
                InfeaIx = np.ravel_multi_index((i,
                                                InfeaCols * ones((len(j), 1),
                                                                 dtype=int)),
                                               (n, k))
            else:
                InfeaIx = np.ravel_multi_index((i, InfeaCols[j]), (n, k))

            Alpha.ravel()[InfeaSubIx] = X.ravel()[InfeaIx] / \
                (X.ravel()[InfeaIx] - ZInfea.ravel()[InfeaSubIx])

            minVal, minIx = np.min(Alpha, axis=0), np.argmin(Alpha, axis=0)
            Alpha[:, :] = kron(ones((n, 1)), minVal)

            X[:, InfeaCols] = X[:, InfeaCols] + \
                              Alpha * (ZInfea - X[:, InfeaCols])

            IxToActive = np.ravel_multi_index((minIx, InfeaCols), (n, k))

            X.ravel()[IxToActive] = 0
            PassSet.ravel()[IxToActive] = False

        if FeaSubCols.shape[0] > 0:  # for feasible cols

            FeaCols = NotOptCols[FeaSubCols]
            X[:, FeaCols] = Z[:, FeaSubCols]
            Y[:, FeaCols] = AtA.dot(X[:, FeaCols]) - AtB[:, FeaCols]

            Y[abs(Y) < 1e-12] = 0   # for numerical stability.

            NotOptSubSet = (Y[:, FeaCols] < 0) & ~PassSet[:, FeaCols]

            NewOptCols = FeaCols[all(~NotOptSubSet, axis=0)]
            UpdateNotOptCols = FeaCols[any(NotOptSubSet, axis=0)]

            if UpdateNotOptCols.shape[0] > 0:
                minIx = np.argmin(Y[:, UpdateNotOptCols] * \
                                  ~PassSet[:, UpdateNotOptCols], axis=0)
                idx = np.ravel_multi_index((minIx, UpdateNotOptCols), (n, k))
                PassSet.ravel()[idx] = True

            NotOptSet.T[NewOptCols] = False
            NotOptCols = find(NotOptSet)

    return X, Y


def nnlsm_blockpivot(A, B, isInputProd=0, init=None):
    """
    Nonnegativity Constrained Least Squares with Multiple Righthand Sides
         using Block Principal Pivoting method

    This function solves the following problem: given A and B, find X such that
               minimize || AX-B ||_F^2 where X>=0 elementwise.

    Reference:
        Jingu Kim and Haesun Park. Fast Nonnegative Matrix Factorization:
            An Activeset-like Method and Comparisons.
            SIAM Journal on Scientific Computing, 33(6), pp. 3261-3281, 2011.

    Based on the Matlab version written by Jingu Kim (jingu.kim@gmail.com)
                  School of Computational Science and Engineering,
                  Georgia Institute of Technology

    Parameters
    ----------
    A : input matrix (m x n) (by default),
        or A'*A (n x n) if isInputProd==1

    B : input matrix (m x k) (by default),
        or A'*B (n x k) if isInputProd==1

    overwrite : (optional, default:0)
        if turned on, unconstrained least squares solution is computed
        in the beginning

    isInputProd : (optional, default:0)
        if turned on, use (A'*A,A'*B) as input instead of (A,B)

    init : (optional) initial value for X

    Returns
    -------
    X : the solution (n x k)

    Y : A'*A*X - A'*B where X is the solution (n x k)
    """

    if isInputProd:
        AtA = A
        AtB = B
    else:
        AtA = A.T.dot(A)
        AtB = A.T.dot(B)

    n, k = AtB.shape
    MAX_BIG_ITER = n * 5

    # set initial feasible solution
    X = zeros((n, k))
    if init is None:
        Y = - AtB
        PassiveSet = zeros((n, k), dtype=np.bool)
    else:
        PassiveSet = (init > 0).copy()
        X = normalEqComb(AtA, AtB, PassiveSet)
        Y = AtA.dot(X) - AtB

    # parameters
    pbar = 3
    P = zeros((1, k))
    P[:] = pbar
    Ninf = zeros((1, k))
    Ninf[:] = n + 1

    NonOptSet = (Y < 0) & ~PassiveSet
    InfeaSet = (X < 0) & PassiveSet
    NotGood = (np.sum(NonOptSet, axis=0) + \
               np.sum(InfeaSet, axis=0))[np.newaxis, :]
    NotOptCols = NotGood > 0

    bigIter = 0

    while find(NotOptCols).shape[0] > 0:

        bigIter = bigIter + 1
        # set max_iter for ill-conditioned (numerically unstable) case
        if ((MAX_BIG_ITER > 0) & (bigIter > MAX_BIG_ITER)):
            break

        Cols1 = NotOptCols & (NotGood < Ninf)
        Cols2 = NotOptCols & (NotGood >= Ninf) & (P >= 1)
        Cols3Ix = find(NotOptCols & ~Cols1 & ~Cols2)

        if find(Cols1).shape[0] > 0:
            P[Cols1] = pbar
            NotGood[Cols1]
            Ninf[Cols1] = NotGood[Cols1]
            PassiveSet[NonOptSet & tile(Cols1, (n, 1))] = True
            PassiveSet[InfeaSet & tile(Cols1, (n, 1))] = False

        if find(Cols2).shape[0] > 0:
            P[Cols2] = P[Cols2] - 1
            PassiveSet[NonOptSet & tile(Cols2, (n, 1))] = True
            PassiveSet[InfeaSet & tile(Cols2, (n, 1))] = False

        if Cols3Ix.shape[0] > 0:
            for i in range(Cols3Ix.shape[0]):
                Ix = Cols3Ix[i]
                toChange = np.max(find(NonOptSet[:, Ix] | InfeaSet[:, Ix]))
                if PassiveSet[toChange, Ix]:
                    PassiveSet[toChange, Ix] = False
                else:
                    PassiveSet[toChange, Ix] = True

        Z = normalEqComb(AtA, AtB[:, NotOptCols.flatten()],
                         PassiveSet[:, NotOptCols.flatten()])
        X[:, NotOptCols.flatten()] = Z[:]
        X[abs(X) < 1e-12] = 0  # for numerical stability.
        Y[:, NotOptCols.flatten()] = AtA.dot(X[:, NotOptCols.flatten()]) - \
                                     AtB[:, NotOptCols.flatten()]
        Y[abs(Y) < 1e-12] = 0  # for numerical stability.

        # check optimality
        NotOptMask = tile(NotOptCols, (n, 1))
        NonOptSet = NotOptMask & (Y < 0) & ~PassiveSet
        InfeaSet = NotOptMask & (X < 0) & PassiveSet
        NotGood = (np.sum(NonOptSet, axis=0) +
                   np.sum(InfeaSet, axis=0))[np.newaxis, :]
        NotOptCols = NotGood > 0

    return X, Y


def getGradient(X, F, nWay, r):
    grad = []
    for k in range(nWay):
        ways = range(nWay)
        ways.remove(k)
        XF = X.uttkrp(F, k)
        # Compute the inner-product matrix
        FF = ones((r, r))
        for i in ways:
            FF = FF * (F[i].T.dot(F[i]))
        grad.append(F[k].dot(FF) - XF)
    return grad


def getProjGradient(X, F, nWay, r):
    pGrad = []
    for k in range(nWay):
        ways = range(nWay)
        ways.remove(k)
        XF = X.uttkrp(F, k)
        # Compute the inner-product matrix
        FF = ones((r, r))
        for i in ways:
            FF = FF * (F[i].T.dot(F[i]))
        grad = F[k].dot(FF) - XF
        grad[~((grad < 0) | (F[k] > 0))] = 0.
        pGrad.append(grad)
    return pGrad


class anls_asgroup(object):

    def initializer(self, X, F, nWay, orderWays):
        F[orderWays[0]] = zeros(F[orderWays[0]].shape)
        FF = []
        for k in range(nWay):
            FF.append((F[k].T.dot(F[k])))
        return F, FF

    def iterSolver(self, X, F, FF_init, nWay, r, orderWays):
        # solve NNLS problems for each factor
        for k in range(nWay):
            curWay = orderWays[k]
            ways = range(nWay)
            ways.remove(curWay)
            XF = X.uttkrp(F, curWay)
            # Compute the inner-product matrix
            FF = ones((r, r))
            for i in ways:
                FF = FF * FF_init[i]  # (F[i].T.dot(F[i]))
            ow = 0
            Fthis, temp = nnlsm_activeset(FF, XF.T, ow, 1, F[curWay].T)
            F[curWay] = Fthis.T
            FF_init[curWay] = (F[curWay].T.dot(F[curWay]))
        return F, FF_init


class anls_bpp(object):

    def initializer(self, X, F, nWay, orderWays):
        F[orderWays[0]] = zeros(F[orderWays[0]].shape)
        FF = []
        for k in range(nWay):
            FF.append((F[k].T.dot(F[k])))
        return F, FF

    def iterSolver(self, X, F, FF_init, nWay, r, orderWays):
        for k in range(nWay):
            curWay = orderWays[k]
            ways = range(nWay)
            ways.remove(curWay)
            XF = X.uttkrp(F, curWay)
            # Compute the inner-product matrix
            FF = ones((r, r))
            for i in ways:
                FF = FF * FF_init[i]  # (F[i].T.dot(F[i]))
            Fthis, temp = nnlsm_blockpivot(FF, XF.T, 1, F[curWay].T)
            F[curWay] = Fthis.T
            FF_init[curWay] = (F[curWay].T.dot(F[curWay]))
        return F, FF_init


def getStopCriterion(pGrad, nWay, nr_grad_all):
    retVal = np.sum(np.linalg.norm(pGrad[i], 'fro') ** 2
                    for i in range(nWay))
    return np.sqrt(retVal) / nr_grad_all


def getRelError(X, F_kten, nWay, nr_X):
    error = nr_X ** 2 + F_kten.norm() ** 2 - 2 * F_kten.innerprod(X)
    return np.sqrt(max(error, 0)) / nr_X


def nonnegative_tensor_factorization(X, r, method='anls_bpp',
                                     tol=1e-4, stop_criterion=1,
                                     min_iter=20, max_iter=200, max_time=1e6,
                                     init=None, orderWays=None):
    """
    Nonnegative Tensor Factorization (Canonical Decomposition / PARAFAC)

    Based on the Matlab version written by Jingu Kim (jingu.kim@gmail.com)
               School of Computational Science and Engineering,
               Georgia Institute of Technology

    This software implements nonnegativity-constrained low-rank approximation
    of tensors in PARAFAC model. Assuming that a k-way tensor X and target rank
    r are given, this software seeks F1, ... , Fk by solving the following
    problem:

    minimize
        || X- sum_(j=1)^r (F1_j o F2_j o ... o Fk_j) ||_F^2 +
              G(F1, ... , Fk) + H(F1, ..., Fk)
    where
        G(F1, ... , Fk) = sum_(i=1)^k ( alpha_i * ||Fi||_F^2 ),
        H(F1, ... , Fk) = sum_(i=1)^k ( beta_i sum_(j=1)^n || Fi_j ||_1^2 ).
    such that
        Fi >= 0 for all i.

    To use this software, it is necessary to first install scikit_tensor.

    Reference:
         Fast Nonnegative Tensor Factorization with an Active-set-like Method.
         Jingu Kim and Haesun Park.
         In High-Performance Scientific Computing: Algorithms and Applications,
         Springer, 2012, pp. 311-326.

    Parameters
    ----------
    X : tensor' object of scikit_tensor
        Input data tensor.

    r : int
        Target low-rank.

    method : string, optional
        Algorithm for solving NMF. One of the following values:
         'anls_bpp' 'anls_asgroup' 'hals' 'mu'
         See above paper (and references therein) for the details
         of these algorithms.
         Default is 'anls_bpp'.

    tol : float, optional
        Stopping tolerance. Default is 1e-4.
        If you want to obtain a more accurate solution,
        decrease TOL and increase MAX_ITER at the same time.

    min_iter : int, optional
        Minimum number of iterations. Default is 20.

    max_iter : int, optional
        Maximum number of iterations. Default is 200.

    init : A cell array that contains initial values for factors Fi.
            See examples to learn how to set.

    Returns
    -------
        F : a 'ktensor' object that represent a factorized form of a tensor.

    Examples
    --------
        F = nonnegative_tensor_factorization(X, 5)
        F = nonnegative_tensor_factorization(X, 10, tol=1e-3)
        F = nonnegative_tensor_factorization(X, 7, init=Finit, tol=1e-5)
    """

    nWay = len(X.shape)

    if orderWays is None:
        orderWays = np.arange(nWay)

    # set initial values
    if init is not None:
        F_cell = init
    else:
        Finit = [np.random.rand(X.shape[i], r) for i in range(nWay)]
        F_cell = Finit

    grad = getGradient(X, F_cell, nWay, r)

    nr_X = X.norm()
    nr_grad_all = np.sqrt(np.sum(np.linalg.norm(grad[i], 'fro') ** 2
                                 for i in range(nWay)))

    if method == "anls_bpp":
        method = anls_bpp()
    elif method == "anls_asgroup":
        method = anls_asgroup()
    else:
        raise Exception("Unknown method")

    # Execute initializer
    F_cell, FF_init = method.initializer(X, F_cell, nWay, orderWays)

    tStart = time.time()

    if stop_criterion == 2:
        F_kten = ktensor(F_cell)
        rel_Error = getRelError(X, ktensor(F_cell), nWay, nr_X)

    if stop_criterion == 1:
        pGrad = getProjGradient(X, F_cell, nWay, r)
        SC_PGRAD = getStopCriterion(pGrad, nWay, nr_grad_all)

    # main iterations
    for iteration in range(max_iter):
        cntu = True

        F_cell, FF_init = method.iterSolver(X, F_cell,
                                            FF_init, nWay, r, orderWays)
        F_kten = ktensor(F_cell)

        if iteration >= min_iter:

            if time.time() - tStart > max_time:
                cntu = False

            else:

                if stop_criterion == 1:
                    pGrad = getProjGradient(X, F_cell, nWay, r)
                    SC_PGRAD = getStopCriterion(pGrad, nWay, nr_grad_all)
                    if SC_PGRAD < tol:
                        cntu = False

                elif stop_criterion == 2:
                    prev_rel_Error = rel_Error
                    rel_Error = getRelError(X, F_kten, nWay, nr_X)
                    SC_DIFF = np.abs(prev_rel_Error - rel_Error)
                    if SC_DIFF < tol:
                        cntu = False
                else:
                    rel_Error = getRelError(X, F_kten, nWay, nr_X)
                    if rel_Error < 1:
                        cntu = False

        if not cntu:
            break

    return F_kten


def main():

    from numpy.random import rand

    # -----------------------------------------------
    # Creating a synthetic 4th-order tensor
    # -----------------------------------------------
    N1 = 20
    N2 = 25
    N3 = 30
    N4 = 30

    R = 10

    # Random initialization
    np.random.seed(42)

    A_org = np.random.rand(N1, R)
    A_org[A_org < 0.4] = 0

    B_org = rand(N2, R)
    B_org[B_org < 0.4] = 0

    C_org = rand(N3, R)
    C_org[C_org < 0.4] = 0

    D_org = rand(N4, R)
    D_org[D_org < 0.4] = 0

    X_ks = ktensor([A_org, B_org, C_org, D_org])
    X = X_ks.totensor()

    # -----------------------------------------------
    # Tentative initial values
    # -----------------------------------------------
    A0 = np.random.rand(N1, R)
    B0 = np.random.rand(N2, R)
    C0 = np.random.rand(N3, R)
    D0 = np.random.rand(N4, R)

    Finit = [A0, B0, C0, D0]

    # -----------------------------------------------
    # Uncomment only one of the following
    # -----------------------------------------------
    X_approx_ks = nonnegative_tensor_factorization(X, R)

#     X_approx_ks = nonnegative_tensor_factorization(X, R,
#                                                    min_iter=5, max_iter=20)
#
#     X_approx_ks = nonnegative_tensor_factorization(X, R,
#                                                    method='anls_asgroup')
#
#     X_approx_ks = nonnegative_tensor_factorization(X, R,
#                                                    tol=1e-7, max_iter=300)
#
#     X_approx_ks = nonnegative_tensor_factorization(X, R,
#                                                    init=Finit)

    # -----------------------------------------------
    # Approximation Error
    # -----------------------------------------------
    X_approx = X_approx_ks.totensor()
    X_err = (X - X_approx).norm() / X.norm()
    print "Error:", X_err

if __name__ == "__main__":
    main()

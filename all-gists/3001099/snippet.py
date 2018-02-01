"""
=====================================================
Distance computations for masked arrays (:mod:`scipy.spatial.mdistance`)
=====================================================

.. sectionauthor:: Damian Eads, Jason Merkin

Function Reference
------------------

Distance matrix computation from a collection of raw observation vectors
stored in a rectangular array.

.. autosummary::
   :toctree: generated/

   mpdist   -- pairwise distances between observation vectors.
   squareform -- convert distance matrix to a condensed one and vice versa

Predicates for checking the validity of distance matrices, both
condensed and redundant. Also contained in this module are functions
for computing the number of observations in a distance matrix.

.. autosummary::
   :toctree: generated/

   is_valid_dm -- checks for a valid distance matrix
   is_valid_y  -- checks for a valid condensed distance matrix
   num_obs_dm  -- # of observations in a distance matrix
   num_obs_y   -- # of observations in a condensed distance matrix

Distance functions between two vectors ``u`` and ``v``. Computing
distances over a large collection of vectors is inefficient for these
functions. Use ``mpdist`` for this purpose.

.. autosummary::
   :toctree: generated/

   braycurtis       -- the Bray-Curtis distance.
   canberra         -- the Canberra distance.
   chebyshev        -- the Chebyshev distance.
   cityblock        -- the Manhattan distance.
   correlation      -- the Correlation distance.
   cosine           -- the Cosine distance.
   dice             -- the Dice dissimilarity (boolean).
   euclidean        -- the Euclidean distance.
   hamming          -- the Hamming distance (boolean).
   jaccard          -- the Jaccard distance (boolean).
   kulsinski        -- the Kulsinski distance (boolean).
   mahalanobis      -- the Mahalanobis distance.
   matching         -- the matching dissimilarity (boolean).
   minkowski        -- the Minkowski distance.
   rogerstanimoto   -- the Rogers-Tanimoto dissimilarity (boolean).
   russellrao       -- the Russell-Rao dissimilarity (boolean).
   seuclidean       -- the normalized Euclidean distance.
   sokalmichener    -- the Sokal-Michener dissimilarity (boolean).
   sokalsneath      -- the Sokal-Sneath dissimilarity (boolean).
   sqeuclidean      -- the squared Euclidean distance.
   yule             -- the Yule dissimilarity (boolean).


References
----------

.. [Sta07] "Statistics toolbox." API Reference Documentation. The MathWorks.
   http://www.mathworks.com/access/helpdesk/help/toolbox/stats/.
   Accessed October 1, 2007.

.. [Mti07] "Hierarchical clustering." API Reference Documentation.
   The Wolfram Research, Inc.
   http://reference.wolfram.com/mathematica/HierarchicalClustering/tutorial/HierarchicalClustering.html.
   Accessed October 1, 2007.

.. [Gow69] Gower, JC and Ross, GJS. "Minimum Spanning Trees and Single Linkage
   Cluster Analysis." Applied Statistics. 18(1): pp. 54--64. 1969.

.. [War63] Ward Jr, JH. "Hierarchical grouping to optimize an objective
   function." Journal of the American Statistical Association. 58(301):
   pp. 236--44. 1963.

.. [Joh66] Johnson, SC. "Hierarchical clustering schemes." Psychometrika.
   32(2): pp. 241--54. 1966.

.. [Sne62] Sneath, PH and Sokal, RR. "Numerical taxonomy." Nature. 193: pp.
   855--60. 1962.

.. [Bat95] Batagelj, V. "Comparing resemblance measures." Journal of
   Classification. 12: pp. 73--90. 1995.

.. [Sok58] Sokal, RR and Michener, CD. "A statistical method for evaluating
   systematic relationships." Scientific Bulletins. 38(22):
   pp. 1409--38. 1958.

.. [Ede79] Edelbrock, C. "Mixture model tests of hierarchical clustering
   algorithms: the problem of classifying everybody." Multivariate
   Behavioral Research. 14: pp. 367--84. 1979.

.. [Jai88] Jain, A., and Dubes, R., "Algorithms for Clustering Data."
   Prentice-Hall. Englewood Cliffs, NJ. 1988.

.. [Fis36] Fisher, RA "The use of multiple measurements in taxonomic
   problems." Annals of Eugenics, 7(2): 179-188. 1936


Copyright Notice
----------------

Copyright (C) Damian Eads, 2007-2008, Jason Merkin 2011. New BSD License.

"""

import warnings
import numpy as np
import numpy.ma as ma

import _distance_wrap

def _nbool_correspond_all(u, v):
    if u.dtype != v.dtype:
        raise TypeError("Arrays being compared must be of the same data type.")

    if u.dtype == np.int or u.dtype == np.float_ or u.dtype == np.double:
        not_u = 1.0 - u
        not_v = 1.0 - v
        nff = (not_u * not_v).sum()
        nft = (not_u * v).sum()
        ntf = (u * not_v).sum()
        ntt = (u * v).sum()
    elif u.dtype == np.bool:
        not_u = ~u
        not_v = ~v
        nff = (not_u & not_v).sum()
        nft = (not_u & v).sum()
        ntf = (u & not_v).sum()
        ntt = (u & v).sum()
    else:
        raise TypeError("Arrays being compared have unknown type.")

    return (nff, nft, ntf, ntt)

def _nbool_correspond_ft_tf(u, v):
    if u.dtype == np.int or u.dtype == np.float_ or u.dtype == np.double:
        not_u = 1.0 - u
        not_v = 1.0 - v
        nft = (not_u * v).sum()
        ntf = (u * not_v).sum()
    else:
        not_u = ~u
        not_v = ~v
        nft = (not_u & v).sum()
        ntf = (u & not_v).sum()
    return (nft, ntf)

def _mcopy_array_if_base_present(a):
    """
    Copies the array if its base points to a parent array.
    """
    if a.base is not None:
        return a.copy()
    elif np.issubsctype(a, np.float32):
        return ma.array(a, dtype=np.double)
    else:
        return a

def _mcopy_arrays_if_base_present(T):
    """
    Accepts a tuple of arrays T. Copies the array T[i] if its base array
    points to an actual array. Otherwise, the reference is just copied.
    This is useful if the arrays are being passed to a C function that
    does not do proper striding.
    """
    l = [_mcopy_array_if_base_present(a) for a in T]
    return l

def _mseuclidean(X, V, m, dm):
    """
    Does masked seuclidean for a full array
    """
    if V is not None:
        V = ma.asarray(V, order='c')
        if type(V) != ma.array:
            raise TypeError('Variance vector V must be a numpy array')
        if V.dtype != np.double:
            raise TypeError('Variance vector V must contain doubles.')
        if len(V.shape) != 1:
            raise ValueError('Variance vector V must be one-dimensional.')
        if V.shape[0] != n:
            raise ValueError('Variance vector V must be of the same '
                    'dimension as the vectors on which the distances '
                    'are computed.')
        # The C code doesn't do striding.
        [VV] = _mcopy_arrays_if_base_present([_convert_to_double(V)])
    else:
        VV = ma.var(X, axis=0, ddof=1)

    k = 0
    for i in xrange(0, m-1):
        for j in xrange(i+1,m):
            d = mseuclidean(X[i],X[j],VV)
            dm[k] = d
            k += 1
	return dm

def mpdist(X, metric='euclidean', p=2, w=None, V=None, VI=None):
    r"""
    Adapted pdist to masked arrays

    Computes the pairwise distances between m original observations in
    n-dimensional space. Returns a condensed distance matrix Y.  For
    each :math:`i` and :math:`j` (where :math:`i<j<n`), the
    metric ``dist(u=X[i], v=X[j])`` is computed and stored in the
    :math:`ij`th entry.

    See ``squareform`` for information on how to calculate the index of
    this entry or to convert the condensed distance matrix to a
    redundant square matrix.

    The following are common calling conventions.

    1. ``Y = mpdist(X, 'euclidean')``

       Computes the distance between m points using Euclidean distance
       (2-norm) as the distance metric between the points. The points
       are arranged as m n-dimensional row vectors in the matrix X.

    2. ``Y = mpdist(X, 'minkowski', p)``

       Computes the distances using the Minkowski distance
       :math:`||u-v||_p` (p-norm) where :math:`p \geq 1`.

    3. ``Y = mpdist(X, 'cityblock')``

       Computes the city block or Manhattan distance between the
       points.

    4. ``Y = mpdist(X, 'seuclidean', V=None)``

       Computes the standardized Euclidean distance. The standardized
       Euclidean distance between two n-vectors ``u`` and ``v`` is

       .. math::

          \sqrt{\sum {(u_i-v_i)^2 / V[x_i]}}.

       V is the variance vector; V[i] is the variance computed over all
          the i'th components of the points. If not passed, it is
          automatically computed.

    5. ``Y = mpdist(X, 'sqeuclidean')``

       Computes the squared Euclidean distance :math:`||u-v||_2^2` between
       the vectors.

    6. ``Y = mpdist(X, 'cosine')``

       Computes the cosine distance between vectors u and v,

       .. math::

          \frac{1 - uv^T}
               {{|u|}_2 {|v|}_2}

       where |*|_2 is the 2 norm of its argument *.

    7. ``Y = mpdist(X, 'correlation')``

       Computes the correlation distance between vectors u and v. This is

       .. math::

          \frac{1 - (u - \bar{u})(v - \bar{v})^T}
               {{|(u - \bar{u})|}{|(v - \bar{v})|}^T}

       where :math:`\bar{v}` is the mean of the elements of vector v.

    8. ``Y = mpdist(X, 'hamming')``

       Computes the normalized Hamming distance, or the proportion of
       those vector elements between two n-vectors ``u`` and ``v``
       which disagree. To save memory, the matrix ``X`` can be of type
       boolean.

    9. ``Y = mpdist(X, 'jaccard')``

       Computes the Jaccard distance between the points. Given two
       vectors, ``u`` and ``v``, the Jaccard distance is the
       proportion of those elements ``u[i]`` and ``v[i]`` that
       disagree where at least one of them is non-zero.

    10. ``Y = mpdist(X, 'chebyshev')``

       Computes the Chebyshev distance between the points. The
       Chebyshev distance between two n-vectors ``u`` and ``v`` is the
       maximum norm-1 distance between their respective elements. More
       precisely, the distance is given by

       .. math::

          d(u,v) = \max_i {|u_i-v_i|}.

    11. ``Y = mpdist(X, 'canberra')``

       Computes the Canberra distance between the points. The
       Canberra distance between two points ``u`` and ``v`` is

       .. math::

         d(u,v) = \sum_u \frac{|u_i-v_i|}
                              {(|u_i|+|v_i|)}


    12. ``Y = mpdist(X, 'braycurtis')``

       Computes the Bray-Curtis distance between the points. The
       Bray-Curtis distance between two points ``u`` and ``v`` is


       .. math::

            d(u,v) = \frac{\sum_i {u_i-v_i}}
                          {\sum_i {u_i+v_i}}

    13. ``Y = mpdist(X, 'mahalanobis', VI=None)``

       Computes the Mahalanobis distance between the points. The
       Mahalanobis distance between two points ``u`` and ``v`` is
       :math:`(u-v)(1/V)(u-v)^T` where :math:`(1/V)` (the ``VI``
       variable) is the inverse covariance. If ``VI`` is not None,
       ``VI`` will be used as the inverse covariance matrix.

    14. ``Y = mpdist(X, 'yule')``

       Computes the Yule distance between each pair of boolean
       vectors. (see yule function documentation)

    15. ``Y = mpdist(X, 'matching')``

       Computes the matching distance between each pair of boolean
       vectors. (see matching function documentation)

    16. ``Y = mpdist(X, 'dice')``

       Computes the Dice distance between each pair of boolean
       vectors. (see dice function documentation)

    17. ``Y = mpdist(X, 'kulsinski')``

       Computes the Kulsinski distance between each pair of
       boolean vectors. (see kulsinski function documentation)

    18. ``Y = mpdist(X, 'rogerstanimoto')``

       Computes the Rogers-Tanimoto distance between each pair of
       boolean vectors. (see rogerstanimoto function documentation)

    19. ``Y = mpdist(X, 'russellrao')``

       Computes the Russell-Rao distance between each pair of
       boolean vectors. (see russellrao function documentation)

    20. ``Y = mpdist(X, 'sokalmichener')``

       Computes the Sokal-Michener distance between each pair of
       boolean vectors. (see sokalmichener function documentation)

    21. ``Y = mpdist(X, 'sokalsneath')``

       Computes the Sokal-Sneath distance between each pair of
       boolean vectors. (see sokalsneath function documentation)

    22. ``Y = mpdist(X, 'wminkowski')``

       Computes the weighted Minkowski distance between each pair of
       vectors. (see wminkowski function documentation)

    22. ``Y = mpdist(X, f)``

       Computes the distance between all pairs of vectors in X
       using the user supplied 2-arity function f. For example,
       Euclidean distance between the vectors could be computed
       as follows::

         dm = mpdist(X, (lambda u, v: np.sqrt(((u-v)*(u-v).T).sum())))

       Note that you should avoid passing a reference to one of
       the distance functions defined in this library. For example,::

         dm = mpdist(X, sokalsneath)

       would calculate the pair-wise distances between the vectors in
       X using the Python function sokalsneath. This would result in
       sokalsneath being called :math:`{n \choose 2}` times, which
       is inefficient. Instead, the optimized C version is more
       efficient, and we call it using the following syntax.::

         dm = mpdist(X, 'sokalsneath')

    Parameters
    ----------
    X : ma.array
        An m by n masked array of m original observations in an
        n-dimensional space.
    metric : string or function
        The distance metric to use. The distance function can
        be 'braycurtis', 'canberra', 'chebyshev', 'cityblock',
        'correlation', 'cosine', 'dice', 'euclidean', 'hamming',
        'jaccard', 'kulsinski', 'mahalanobis', 'matching',
        'minkowski', 'rogerstanimoto', 'russellrao', 'seuclidean',
        'sokalmichener', 'sokalsneath', 'sqeuclidean', 'yule'.
    w : ma.array
        The weight vector (for weighted Minkowski).
    p : double
        The p-norm to apply (for Minkowski, weighted and unweighted)
    V : ma.array
            The variance vector (for standardized Euclidean).
    VI : ma.array
        The inverse of the covariance matrix (for Mahalanobis).

    Returns
    -------
    Y : ma.array
        A condensed masked distance matrix.

    See Also
    --------
    squareform : converts between condensed distance matrices and
                 square distance matrices.
    """

    X = ma.asarray(X, order='c')

    # The C code doesn't do striding.
    [X] = _mcopy_arrays_if_base_present([_convert_to_double(X)])

    s = X.shape
    if len(s) != 2:
        raise ValueError('A 2-dimensional array must be passed.');

    m, n = s
    dm = ma.zeros((m * (m - 1) / 2,), dtype=np.double)

    wmink_names = ['wminkowski', 'wmi', 'wm', 'wpnorm']
    if w is None and (metric == wminkowski or metric in wmink_names):
        raise ValueError('weighted minkowski requires a weight '
                            'vector `w` to be given.')

    if callable(metric):
        if metric == mminkowski:
            def dfun(u,v): return mminkowski(u, v, p)
        elif metric == mwminkowski:
            def dfun(u,v): return mwminkowski(u, v, p, w)
        elif metric == mseuclidean:
            def dfun(u,v): return mseuclidean(u, v, V)
        elif metric == mahalanobis:
            def dfun(u,v): return mmahalanobis(u, v, V)
        else:
            dfun = metric

        k = 0
        for i in xrange(0, m - 1):
            for j in xrange(i+1, m):
                dm[k] = dfun(X[i], X[j])
                k = k + 1

    elif isinstance(metric,basestring):
        mstr = metric.lower()
        if metric == 'euclidean':
            dm = mpdist(X, meuclidean)
        elif mstr in set(['seuclidean', 'se', 's']):
            dm = _mseuclidean(X, V, m, dm)
        elif metric == 'sqeuclidean':
            dm = mpdist(X, meuclidean)
            dm = dm ** 2.0
        elif metric == 'braycurtis':
            dm = mpdist(X, mbraycurtis)
        elif metric == 'mahalanobis':
            if VI is None:
                V = ma.cov(X.T)
                VI = np.linalg.inv(V)
            else:
                VI = ma.asarray(VI, order='c')
            [VI] = _mcopy_arrays_if_base_present([VI])
            # (u-v)V^(-1)(u-v)^T
            dm = mpdist(X, (lambda u, v: mmahalanobis(u, v, VI)))
        elif metric == 'canberra':
            dm = mpdist(X, mcanberra)
        elif metric == 'cityblock':
            dm = mpdist(X, mcityblock)
        elif metric == 'minkowski':
            dm = mpdist(X, mminkowski, p=p)
        elif metric == 'wminkowski':
            dm = mpdist(X, mwminkowski, p=p, w=w)
        elif metric == 'cosine':
            dm = mpdist(X, mcosine)
        elif metric == 'correlation':
            dm = mpdist(X, mcorrelation)
        elif metric == 'hamming':
            dm = mpdist(X, mhamming)
        elif metric == 'jaccard':
            dm = mpdist(X, mjaccard)
        elif metric == 'chebyshev' or metric == 'chebychev':
            dm = mpdist(X, mchebyshev)
        elif metric == 'yule':
            dm = mpdist(X, myule)
        elif metric == 'matching':
            dm = mpdist(X, mmatching)
        elif metric == 'dice':
            dm = mpdist(X, mdice)
        elif metric == 'kulsinski':
            dm = mpdist(X, mkulsinski)
        elif metric == 'rogerstanimoto':
            dm = mpdist(X, mrogerstanimoto)
        elif metric == 'russellrao':
            dm = mpdist(X, mrussellrao)
        elif metric == 'sokalsneath':
            dm = mpdist(X, msokalsneath)
        elif metric == 'sokalmichener':
            dm = mpdist(X, msokalmichener)
        else:
            raise ValueError('Unknown Distance Metric: %s' % mstr)

    return dm

def mminkowski(u, v, p):
    r"""
    Computes the Minkowski distance between two vectors ``u`` and ``v``,
    defined as

    .. math::

       {||u-v||}_p = (\sum{|u_i - v_i|^p})^{1/p}.

    Parameters
    ----------
    u : ndarray
        An n-dimensional vector.
    v : ndarray
        An n-dimensional vector.
    p : ndarray
        The norm of the difference :math:`{||u-v||}_p`.

    Returns
    -------
    d : double
        The Minkowski distance between vectors ``u`` and ``v``.
    """
    u = ma.asarray(u, order='c')
    v = ma.asarray(v, order='c')
    if p < 1:
        raise ValueError("p must be at least 1")
    return (abs(u-v)**p).sum() ** (1.0 / p)

def mwminkowski(u, v, p, w):
    r"""
    Computes the weighted Minkowski distance between two vectors ``u``
    and ``v``, defined as

    .. math::

       \left(\sum{(w_i |u_i - v_i|^p)}\right)^{1/p}.

    Parameters
    ----------
    u : ndarray
        An :math:`n`-dimensional vector.
    v : ndarray
        An :math:`n`-dimensional vector.
    p : ndarray
        The norm of the difference :math:`{||u-v||}_p`.
    w : ndarray
        The weight vector.

    Returns
    -------
    d : double
        The Minkowski distance between vectors ``u`` and ``v``.
    """
    u = ma.asarray(u, order='c')
    v = ma.asarray(v, order='c')
    w = ma.asarray(w)
    if p < 1:
        raise ValueError("p must be at least 1")
    return ((w * abs(u-v))**p).sum() ** (1.0 / p)

def meuclidean(u, v):
    """
    Computes the Euclidean distance between two n-vectors ``u`` and ``v``,
    which is defined as

    .. math::

       {||u-v||}_2

    Parameters
    ----------
    u : ndarray
        An :math:`n`-dimensional vector.
    v : ndarray
        An :math:`n`-dimensional vector.

    Returns
    -------
    d : double
        The Euclidean distance between vectors ``u`` and ``v``.
    """
    u = ma.asarray(u, order='c')
    v = ma.asarray(v, order='c')
    q=np.matrix(u-v)
    return np.sqrt((q*q.T).sum())

def msqeuclidean(u, v):
    """
    Computes the squared Euclidean distance between two n-vectors u and v,
    which is defined as

    .. math::

       {||u-v||}_2^2.


    Parameters
    ----------
    u : ndarray
        An :math:`n`-dimensional vector.
    v : ndarray
        An :math:`n`-dimensional vector.

    Returns
    -------
    d : double
        The squared Euclidean distance between vectors ``u`` and ``v``.
    """
    u = ma.asarray(u, order='c')
    v = ma.asarray(v, order='c')
    return ((u-v)*(u-v).T).sum()

def mcosine(u, v):
    r"""
    Computes the Cosine distance between two n-vectors u and v, which
    is defined as

    .. math::

       \frac{1-uv^T}
            {||u||_2 ||v||_2}.

    Parameters
    ----------
    u : ndarray
        An :math:`n`-dimensional vector.
    v : ndarray
        An :math:`n`-dimensional vector.

    Returns
    -------
    d : double
        The Cosine distance between vectors ``u`` and ``v``.
    """
    u = ma.asarray(u, order='c')
    v = ma.asarray(v, order='c')
    return (1.0 - (ma.dot(u, v.T) / \
                   (ma.sqrt(ma.dot(u, u.T)) * ma.sqrt(ma.dot(v, v.T)))))

def mcorrelation(u, v):
    r"""
    Computes the correlation distance between two n-vectors ``u`` and
    ``v``, which is defined as

    .. math::

       \frac{1 - (u - \bar{u}){(v - \bar{v})}^T}
            {{||(u - \bar{u})||}_2 {||(v - \bar{v})||}_2^T}

    where :math:`\bar{u}` is the mean of a vectors elements and ``n``
    is the common dimensionality of ``u`` and ``v``.

    Parameters
    ----------
    u : ndarray
        An :math:`n`-dimensional vector.
    v : ndarray
        An :math:`n`-dimensional vector.

    Returns
    -------
    d : double
        The correlation distance between vectors ``u`` and ``v``.
    """
    umu = u.mean()
    vmu = v.mean()
    um = u - umu
    vm = v - vmu
    return 1.0 - (ma.dot(um, vm) /
                  (ma.sqrt(ma.dot(um, um)) \
                   * ma.sqrt(ma.dot(vm, vm))))

def mhamming(u, v):
    r"""
    Computes the Hamming distance between two n-vectors ``u`` and
    ``v``, which is simply the proportion of disagreeing components in
    ``u`` and ``v``. If ``u`` and ``v`` are boolean vectors, the Hamming
    distance is

    .. math::

       \frac{c_{01} + c_{10}}{n}

    where :math:`c_{ij}` is the number of occurrences of
    :math:`\mathtt{u[k]} = i` and :math:`\mathtt{v[k]} = j` for
    :math:`k < n`.

    Parameters
    ----------
    u : ndarray
        An :math:`n`-dimensional vector.
    v : ndarray
        An :math:`n`-dimensional vector.

    Returns
    -------
    d : double
        The Hamming distance between vectors ``u`` and ``v``.
    """
    u = ma.asarray(u, order='c')
    v = ma.asarray(v, order='c')
    return (u != v).mean()

def mjaccard(u, v):
    """
    Computes the Jaccard-Needham dissimilarity between two boolean
    n-vectors u and v, which is

    .. math::

         \frac{c_{TF} + c_{FT}}
              {c_{TT} + c_{FT} + c_{TF}}

    where :math:`c_{ij}` is the number of occurrences of
    :math:`\mathtt{u[k]} = i` and :math:`\mathtt{v[k]} = j` for
    :math:`k < n`.

    Parameters
    ----------
    u : ndarray
        An :math:`n`-dimensional vector.
    v : ndarray
        An :math:`n`-dimensional vector.

    Returns
    -------
    d : double
        The Jaccard distance between vectors ``u`` and ``v``.
    """
    u = ma.asarray(u, order='c')
    v = ma.asarray(v, order='c')
    return (np.double(np.bitwise_and((u != v),
                     np.bitwise_or(u != 0, v != 0)).sum())
            /  np.double(np.bitwise_or(u != 0, v != 0).sum()))

def mkulsinski(u, v):
    """
    Computes the Kulsinski dissimilarity between two boolean n-vectors
    u and v, which is defined as

    .. math::

         \frac{c_{TF} + c_{FT} - c_{TT} + n}
              {c_{FT} + c_{TF} + n}

    where :math:`c_{ij}` is the number of occurrences of
    :math:`\mathtt{u[k]} = i` and :math:`\mathtt{v[k]} = j` for
    :math:`k < n`.

    Parameters
    ----------
    u : ndarray
        An :math:`n`-dimensional vector.
    v : ndarray
        An :math:`n`-dimensional vector.

    Returns
    -------
    d : double
        The Kulsinski distance between vectors ``u`` and ``v``.
    """
    u = ma.asarray(u, order='c')
    v = ma.asarray(v, order='c')
    n = len(u)
    (nff, nft, ntf, ntt) = _nbool_correspond_all(u, v)

    return (ntf + nft - ntt + n) / (ntf + nft + n)

def mseuclidean(u, v, V):
    """
    Returns the standardized Euclidean distance between two n-vectors
    ``u`` and ``v``. ``V`` is an m-dimensional vector of component
    variances. It is usually computed among a larger collection
    vectors.

    Parameters
    ----------
    u : ndarray
        An :math:`n`-dimensional vector.
    v : ndarray
        An :math:`n`-dimensional vector.

    Returns
    -------
    d : double
        The standardized Euclidean distance between vectors ``u`` and ``v``.
    """
    u = ma.asarray(u, order='c')
    v = ma.asarray(v, order='c')
    V = ma.asarray(V, order='c')
    if len(V.shape) != 1 or V.shape[0] != u.shape[0] or u.shape[0] != v.shape[0]:
        raise TypeError('V must be a 1-D array of the same dimension as u and v.')
    return ma.sqrt(((u-v)**2 / V).sum())

def mcityblock(u, v):
    r"""
    Computes the Manhattan distance between two n-vectors u and v,
    which is defined as

    .. math::

       \sum_i {(u_i-v_i)}.

    Parameters
    ----------
    u : ndarray
        An :math:`n`-dimensional vector.
    v : ndarray
        An :math:`n`-dimensional vector.

    Returns
    -------
    d : double
        The City Block distance between vectors ``u`` and ``v``.
    """
    u = ma.asarray(u, order='c')
    v = ma.asarray(v, order='c')
    return abs(u-v).sum()

def mmahalanobis(u, v, VI):
    r"""
    Computes the Mahalanobis distance between two n-vectors ``u`` and ``v``,
    which is defiend as

    .. math::

       (u-v)V^{-1}(u-v)^T

    where ``VI`` is the inverse covariance matrix :math:`V^{-1}`.

    Parameters
    ----------
    u : ndarray
        An :math:`n`-dimensional vector.
    v : ndarray
        An :math:`n`-dimensional vector.

    Returns
    -------
    d : double
        The Mahalanobis distance between vectors ``u`` and ``v``.
    """
    u = ma.asarray(u, order='c')
    v = ma.asarray(v, order='c')
    VI = ma.asarray(VI, order='c')
    return ma.sqrt(ma.dot(ma.dot((u-v),VI),(u-v).T).sum())

def mchebyshev(u, v):
    r"""
    Computes the Chebyshev distance between two n-vectors u and v,
    which is defined as

    .. math::

       \max_i {|u_i-v_i|}.

    Parameters
    ----------
    u : ndarray
        An :math:`n`-dimensional vector.
    v : ndarray
        An :math:`n`-dimensional vector.

    Returns
    -------
    d : double
        The Chebyshev distance between vectors ``u`` and ``v``.
    """
    u = ma.asarray(u, order='c')
    v = ma.asarray(v, order='c')
    return max(abs(u-v))

def mbraycurtis(u, v):
    r"""
    Computes the Bray-Curtis distance between two n-vectors ``u`` and
    ``v``, which is defined as

    .. math::

       \sum{|u_i-v_i|} / \sum{|u_i+v_i|}.

    Parameters
    ----------
    u : ndarray
        An :math:`n`-dimensional vector.
    v : ndarray
        An :math:`n`-dimensional vector.

    Returns
    -------
    d : double
        The Bray-Curtis distance between vectors ``u`` and ``v``.
    """
    u = ma.asarray(u, order='c')
    v = ma.asarray(v, order='c')
    return abs(u-v).sum() / abs(u+v).sum()

def mcanberra(u, v):
    r"""
    Computes the Canberra distance between two n-vectors u and v,
    which is defined as

    .. math::

       \frac{\sum_i {|u_i-v_i|}}
            {\sum_i {|u_i|+|v_i|}}.


    Parameters
    ----------
    u : ndarray
        An :math:`n`-dimensional vector.
    v : ndarray
        An :math:`n`-dimensional vector.

    Returns
    -------
    d : double
        The Canberra distance between vectors ``u`` and ``v``.
    """
    u = ma.asarray(u, order='c')
    v = ma.asarray(v, order='c')
    return abs(u-v).sum() / (abs(u).sum() + abs(v).sum())

def myule(u, v):
    r"""
    Computes the Yule dissimilarity between two boolean n-vectors u and v,
    which is defined as


    .. math::

         \frac{R}{c_{TT} + c_{FF} + \frac{R}{2}}

    where :math:`c_{ij}` is the number of occurrences of
    :math:`\mathtt{u[k]} = i` and :math:`\mathtt{v[k]} = j` for
    :math:`k < n` and :math:`R = 2.0 * (c_{TF} + c_{FT})`.

    Parameters
    ----------
    u : ndarray
        An :math:`n`-dimensional vector.
    v : ndarray
        An :math:`n`-dimensional vector.

    Returns
    -------
    d : double
        The Yule dissimilarity between vectors ``u`` and ``v``.
    """
    u = ma.asarray(u, order='c')
    v = ma.asarray(v, order='c')
    (nff, nft, ntf, ntt) = _nbool_correspond_all(u, v)
    return float(2.0 * ntf * nft) / float(ntt * nff + ntf * nft)

def mmatching(u, v):
    r"""
    Computes the Matching dissimilarity between two boolean n-vectors
    u and v, which is defined as

    .. math::

       \frac{c_{TF} + c_{FT}}{n}

    where :math:`c_{ij}` is the number of occurrences of
    :math:`\mathtt{u[k]} = i` and :math:`\mathtt{v[k]} = j` for
    :math:`k < n`.

    Parameters
    ----------
    u : ndarray
        An :math:`n`-dimensional vector.
    v : ndarray
        An :math:`n`-dimensional vector.

    Returns
    -------
    d : double
        The Matching dissimilarity between vectors ``u`` and ``v``.
    """
    u = ma.asarray(u, order='c')
    v = ma.asarray(v, order='c')
    (nft, ntf) = _nbool_correspond_ft_tf(u, v)
    # len needed combined masks
    return float(nft + ntf) / float(len(u + v))

def mdice(u, v):
    r"""
    Computes the Dice dissimilarity between two boolean n-vectors
    ``u`` and ``v``, which is

    .. math::

         \frac{c_{TF} + c_{FT}}
              {2c_{TT} + c_{FT} + c_{TF}}

    where :math:`c_{ij}` is the number of occurrences of
    :math:`\mathtt{u[k]} = i` and :math:`\mathtt{v[k]} = j` for
    :math:`k < n`.

    Parameters
    ----------
    u : ndarray
        An :math:`n`-dimensional vector.
    v : ndarray
        An :math:`n`-dimensional vector.

    Returns
    -------
    d : double
        The Dice dissimilarity between vectors ``u`` and ``v``.
    """
    u = ma.asarray(u, order='c')
    v = ma.asarray(v, order='c')
    if u.dtype == np.bool:
        ntt = (u & v).sum()
    else:
        ntt = (u * v).sum()
    (nft, ntf) = _nbool_correspond_ft_tf(u, v)
    return float(ntf + nft) / float(2.0 * ntt + ntf + nft)

def mrogerstanimoto(u, v):
    r"""
    Computes the Rogers-Tanimoto dissimilarity between two boolean
    n-vectors ``u`` and ``v``, which is defined as

    .. math::
       \frac{R}
            {c_{TT} + c_{FF} + R}

    where :math:`c_{ij}` is the number of occurrences of
    :math:`\mathtt{u[k]} = i` and :math:`\mathtt{v[k]} = j` for
    :math:`k < n` and :math:`R = 2(c_{TF} + c_{FT})`.

    Parameters
    ----------
    u : ndarray
        An :math:`n`-dimensional vector.
    v : ndarray
        An :math:`n`-dimensional vector.

    Returns
    -------
    d : double
        The Rogers-Tanimoto dissimilarity between vectors
        `u` and `v`.
    """
    u = ma.asarray(u, order='c')
    v = ma.asarray(v, order='c')
    (nff, nft, ntf, ntt) = _nbool_correspond_all(u, v)
    return float(2.0 * (ntf + nft)) / float(ntt + nff + (2.0 * (ntf + nft)))

def mrussellrao(u, v):
    r"""
    Computes the Russell-Rao dissimilarity between two boolean n-vectors
    ``u`` and ``v``, which is defined as

    .. math::

      \frac{n - c_{TT}}
           {n}

    where :math:`c_{ij}` is the number of occurrences of
    :math:`\mathtt{u[k]} = i` and :math:`\mathtt{v[k]} = j` for
    :math:`k < n`.

    Parameters
    ----------
    u : ndarray
        An :math:`n`-dimensional vector.
    v : ndarray
        An :math:`n`-dimensional vector.

    Returns
    -------
    d : double
        The Russell-Rao dissimilarity between vectors ``u`` and ``v``.
    """
    u = ma.asarray(u, order='c')
    v = ma.asarray(v, order='c')
    if u.dtype == np.bool:
        ntt = (u & v).sum()
    else:
        ntt = (u * v).sum()
    return float(len(u) - ntt) / float(len(u))

def msokalmichener(u, v):
    r"""
    Computes the Sokal-Michener dissimilarity between two boolean vectors
    ``u`` and ``v``, which is defined as

    .. math::

       \frac{R}
            {S + R}

    where :math:`c_{ij}` is the number of occurrences of
    :math:`\mathtt{u[k]} = i` and :math:`\mathtt{v[k]} = j` for
    :math:`k < n`, :math:`R = 2 * (c_{TF} + c_{FT})` and
    :math:`S = c_{FF} + c_{TT}`.

    Parameters
    ----------
    u : ndarray
        An :math:`n`-dimensional vector.
    v : ndarray
        An :math:`n`-dimensional vector.

    Returns
    -------
    d : double
        The Sokal-Michener dissimilarity between vectors ``u`` and ``v``.
    """
    u = ma.asarray(u, order='c')
    v = ma.asarray(v, order='c')
    if u.dtype == np.bool:
        ntt = (u & v).sum()
        nff = (~u & ~v).sum()
    else:
        ntt = (u * v).sum()
        nff = ((1.0 - u) * (1.0 - v)).sum()
    (nft, ntf) = _nbool_correspond_ft_tf(u, v)
    return float(2.0 * (ntf + nft))/float(ntt + nff + 2.0 * (ntf + nft))

def msokalsneath(u, v):
    r"""
    Computes the Sokal-Sneath dissimilarity between two boolean vectors
    ``u`` and ``v``,

    .. math::

       \frac{R}
            {c_{TT} + R}

    where :math:`c_{ij}` is the number of occurrences of
    :math:`\mathtt{u[k]} = i` and :math:`\mathtt{v[k]} = j` for
    :math:`k < n` and :math:`R = 2(c_{TF} + c_{FT})`.

    Parameters
    ----------
    u : ndarray
        An :math:`n`-dimensional vector.
    v : ndarray
        An :math:`n`-dimensional vector.

    Returns
    -------
    d : double
        The Sokal-Sneath dissimilarity between vectors ``u`` and ``v``.
    """
    u = ma.asarray(u, order='c')
    v = ma.asarray(v, order='c')
    if u.dtype == np.bool:
        ntt = (u & v).sum()
    else:
        ntt = (u * v).sum()
    (nft, ntf) = _nbool_correspond_ft_tf(u, v)
    denom = ntt + 2.0 * (ntf + nft)
    if denom == 0:
        raise ValueError('Sokal-Sneath dissimilarity is not defined for '
                            'vectors that are entirely false.')
    return float(2.0 * (ntf + nft)) / denom



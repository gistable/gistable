import numpy as np
from scipy import stats
from itertools import combinations
from statsmodels.stats.multitest import multipletests
from statsmodels.stats.libqsturng import psturng
import warnings


def kw_nemenyi(groups, to_compare=None, alpha=0.05, method='tukey'):
    """

    Kruskal-Wallis 1-way ANOVA with Nemenyi's multiple comparison test

    Arguments:
    ---------------
    groups: sequence
        arrays corresponding to k mutually independent samples from
        continuous populations

    to_compare: sequence
        tuples specifying the indices of pairs of groups to compare, e.g.
        [(0, 1), (0, 2)] would compare group 0 with 1 & 2. by default, all
        possible pairwise comparisons between groups are performed.

    alpha: float
        family-wise error rate used for correcting for multiple comparisons
        (see statsmodels.stats.multitest.multipletests for details)

    method: string
        the null distribution of the test statistic used to determine the
        corrected p-values for each pair of groups, can be either "tukey"
        (studentized range) or "chisq" (Chi-squared). the "chisq" method will
        correct for tied ranks.

    Returns:
    ---------------
    H: float
        Kruskal-Wallis H-statistic

    p_omnibus: float
        p-value corresponding to the global null hypothesis that the medians of
        the groups are all equal

    p_corrected: float array
        corrected p-values for each pairwise comparison, corresponding to the
        null hypothesis that the pair of groups has equal medians. note that
        these are only meaningful if the global null hypothesis is rejected.

    reject: bool array
        True for pairs where the null hypothesis can be rejected for the given
        alpha

    Reference:
    ---------------

    """

    # omnibus test (K-W ANOVA)
    # -------------------------------------------------------------------------

    if method is None:
        method = 'chisq'
    elif method not in ('tukey', 'chisq'):
        raise ValueError('method must be either "tukey" or "chisq"')

    groups = [np.array(gg) for gg in groups]

    k = len(groups)

    n = np.array([len(gg) for gg in groups])
    if np.any(n < 5):
        warnings.warn("Sample sizes < 5 are not recommended (K-W test assumes "
                      "a chi square distribution)")

    allgroups = np.concatenate(groups)
    N = len(allgroups)
    ranked = stats.rankdata(allgroups)

    # correction factor for ties
    T = stats.tiecorrect(ranked)
    if T == 0:
        raise ValueError('All numbers are identical in kruskal')

    # sum of ranks for each group
    j = np.insert(np.cumsum(n), 0, 0)
    R = np.empty(k, dtype=np.float)
    for ii in range(k):
        R[ii] = ranked[j[ii]:j[ii + 1]].sum()

    # the Kruskal-Wallis H-statistic
    H = (12. / (N * (N + 1.))) * ((R ** 2.) / n).sum() - 3 * (N + 1)

    # apply correction factor for ties
    H /= T

    df_omnibus = k - 1
    p_omnibus = stats.chisqprob(H, df_omnibus)

    # multiple comparisons
    # -------------------------------------------------------------------------

    # by default we compare every possible pair of groups
    if to_compare is None:
        to_compare = tuple(combinations(range(k), 2))

    ncomp = len(to_compare)

    dif = np.empty(ncomp, dtype=np.float)
    B = np.empty(ncomp, dtype=np.float)

    Rmean = R / n
    A = N * (N + 1) / 12.

    for pp, (ii, jj) in enumerate(to_compare):

        # absolute difference of mean ranks
        dif[pp] = np.abs(Rmean[ii] - Rmean[jj])
        B[pp] = (1. / n[ii]) + (1. / n[jj])

    if method == 'tukey':

        # p-values obtained from the upper quantiles of the studentized range
        # distribution
        qval = dif / np.sqrt(A * B)
        p_corrected = psturng(qval * np.sqrt(2), k, 1E6)

    elif method == 'chisq':

        # p-values obtained from the upper quantiles of the chi-squared
        # distribution
        chi2 = (dif ** 2.) / (A * B)
        p_corrected = stats.chisqprob(chi2 * T, k - 1)

    reject = p_corrected <= alpha

    return H, p_omnibus, p_corrected, reject
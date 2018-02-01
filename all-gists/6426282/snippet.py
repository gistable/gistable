"""
Structural Change

References
----------

Bai, Jushan, and Pierre Perron. 1998.
"Estimating and Testing Linear Models with Multiple Structural Changes."
Econometrica 66 (1) (January 1): 47-78.

Bai, Jushan, and Pierre Perron. 2003.
"Computation and Analysis of Multiple Structural Change Models."
Journal of Applied Econometrics 18 (1): 1-22.
"""

from __future__ import division
import numpy as np
import pandas as pd
from statsmodels.regression.linear_model import OLS, OLSResults


class InvalidRegimeError(RuntimeError):
    pass


def build_exog(exog, thresholds, threshold_var=None, trim=None):
        """
        Build a diagonally partitioned exogenous matrix for estimation of
        parameters across multiple regimes.

        TODO add date handing, either via dates in the exog matrix or via a
             dates parameter

        Parameters
        ----------
        thresholds : iterable
            The threshold values separating the data into regimes.
        threshold_var : array-like, optional
            The threshold variable. If omitted it is set to be a (zero-indexed)
            trend: range(nobs)
        trim : float, optional
            Optionally specify a trim value to put a lower limit on the number
            of observations in a regime. If omitted, the number of
            observations in regimes is not checked.

        Returns
        -------
        exog : array-like
            The exog matrix, horizontally duplicated once each for the number
            of regimes. Each duplication has the rows for which the model
            dicatates another regime set to zero.
        regime_indicators : array
            Array of which (zero-indexed) regime each observation falls into
        nobs_regimes : iterable
            Number of observations in each regime
        """
        exog = np.asarray(exog)
        nobs = exog.shape[0]

        # TODO Is there a better way to test for and fix this? (the problem is
        #      that if the exog argument is a list, so that exog is 1dim,
        #      np.concatenate fails to create a matrix, instead just makes a
        #      long vector)
        if exog.ndim == 1:
            exog = exog[:,None]

        if trim is not None:
            min_regime_nobs = np.floor(nobs * trim)
        order = len(thresholds) + 1

        if threshold_var is None:
            threshold_var = range(nobs)

        regime_indicators = np.searchsorted(thresholds, threshold_var)

        exog_list = []
        nobs_regimes = ()
        for i in range(order):
            in_regime = (regime_indicators == i)
            nobs_regime = in_regime.sum()

            if trim is not None and nobs_regime < self.min_regime_num:
                raise InvalidRegimeError('Regime %d has too few observations:'
                                         ' threshold values may need to be'
                                         ' adjusted' % i)

            exog_list.append(np.multiply(exog.T, in_regime).T)
            nobs_regimes += (nobs_regime,)

        exog = np.concatenate(exog_list, 1)

        return exog, regime_indicators, nobs_regimes

def find_breakpoints(endog, exog, nbreaks, trim=0.15):
    """
    Find the specified number of breakpoints in a sample.

    TODO add support for partial structural change case
    TODO add support for dates, and return breakdates as well

    Parameters
    ----------
    endog : array-like
        The endogenous variable.
    exog : array-like
        The exogenous matrix.
    nbreaks : integer
        The number of breakpoints to select.
    trim : float or int, optional
        If a float, the minimum percentage of observations in each regime,
        if an integer, the minimum number of observations in each regime.
    
    Returns
    -------
    breakpoints : iterable
        The (zero-indexed) indices of the breakpoints. The k-th breakpoints is
        defined to be the last observation in the (k-1)th regime.
    ssr : float
        The sum of squared residuals from the model with the selected breaks.
    """
    nobs = len(endog)
    if trim < 1:
        trim = int(np.floor(nobs*trim))

    if nobs < 2*trim:
        raise InvalidRegimeError

    # TODO add test to make sure trim is consistent with the number of breaks

    # This is how many calculations will be performed
    ncalcs = (
        ( nobs * (nobs + 1) / 2 ) -
        ( (trim-1)*nobs - (trim-2)*(trim-1)/2 ) -
        ( (trim**2)*nbreaks*(nbreaks+1)/2 ) -
        ( nobs*(trim-1) - nbreaks*trim*(trim-1) -
          (trim-1)**2 - trim*(trim-1)/2 )
    )
    # Estimate the sum of squared errors for each possible segment
    # TODO Important - change this to compute via recursive OLS, will
    #      be much faster!
    results = {}
    for i in range(nobs):
        for j in range(i, nobs):
            length = j - i + 1
            # Current segment too small
            if length < trim:
                continue
            # First segment too small
            if i > 0 and i < trim:
                continue
            # Not enough room for other segments
            if (i // trim) + ((nobs - j - 1) // trim) < nbreaks:
                continue
            
            res = OLS(endog[i:j+1], exog[i:j+1]).fit()

            # Change from zero-index to one-index
            results[(i+1,j+1)] = res.ssr
    assert(len(results) == ncalcs)

    # Dynamic Programming approach to select global minimia
    optimal = []
    for nbreak in range(1, nbreaks):
        optimal.append({})
        for end in range((nbreak+1)*trim, nobs-(nbreaks-nbreak)*trim+1):
            min_ssr = np.Inf
            optimal_breakpoints = None
            for breakpoint in range(nbreak*trim, end-trim+1):
                ssr = optimal[-2][breakpoint][0] if nbreak > 1 else results[(1, breakpoint)]
                ssr += results[(breakpoint+1, end)]
                if ssr < min_ssr:
                    min_ssr = ssr
                    if nbreak > 1:
                        optimal_breakpoints = optimal[-2][breakpoint][1] + (breakpoint,)
                    else:
                        optimal_breakpoints = (breakpoint,)
            optimal[-1][end] = (min_ssr, optimal_breakpoints)

    final_breaks = optimal[-1].keys() if nbreaks > 1 else range(trim, nobs-trim)

    min_ssr = np.Inf
    breakpoints = None
    for breakpoint in final_breaks:
        ssr = optimal[-1][breakpoint][0] if nbreaks > 1 else results[(1, breakpoint)]
        ssr += results[(breakpoint+1, nobs)]
        if ssr < min_ssr:
            min_ssr = ssr
            if nbreaks > 1:
                breakpoints = optimal[-1][breakpoint][1] + (breakpoint,)
            else:
                breakpoints = (breakpoint,)

    # Breakpoints are one-indexed, so change them to be zero-indexed
    breakpoints = tuple(np.array(breakpoints)-1)

    return breakpoints, min_ssr

def break_test(endog, exog, nbreaks, trim=0.15, vcov=None):
    """
    Test that `nbreaks` exists in the sample.

    TODO again, better cache the SSRs
    TODO add support for p-value calculation (Hansen 1997)

    Parameters
    ----------
    endog : array-like
        The endogenous variable.
    exog : array-like
        The exogenous matrix.
    nbreaks : integer
        The number of breakpoints in the null hypothesis
    trim : float or int, optional
        If a float, the minimum percentage of observations in each regime,
        if an integer, the minimum number of observations in each regime.
    vcov : callback, optional
        Optionally provide a callback to modify the variance / covariance
        matrix used in calculating the test statistic.
    
    Returns
    -------
    fstat : float
        The test statistic.
    crits : iterable
        The critical values.
    """
    nobs = len(endog)
    if trim < 1:
        trim = int(np.floor(trim * nobs))

    exog = np.asarray(exog)
    # TODO Is there a better way to test for and fix this? (the problem is
    #      that if the exog argument is a list, so that exog is 1dim,
    #      np.concatenate fails to create a matrix, instead just makes a
    #      long vector)
    if exog.ndim == 1:
        exog = exog[:, None]

    breakpoints, ssr = find_breakpoints(endog, exog, nbreaks, trim)

    built_exog, regime_indicators, nobs_regimes = build_exog(exog, breakpoints)
    res = OLS(endog, built_exog).fit()

    q = exog.shape[1] # number of parameters subject to break, hard-coded to entire exog for now
    p = 0 # number of parameters not subject to break, hard-coded to zero for now
    R = np.zeros((nbreaks, nbreaks+1))
    R[np.diag_indices(nbreaks)] = [-1]*nbreaks
    R[tuple(np.diag_indices(nbreaks) + np.array([[0]*nbreaks, [1]*nbreaks]))] = [1]*nbreaks
    Rd = R.dot(res.params[:, None])

    V = vcov(res) if vcov else res.cov_params()

    const = (nobs - (nbreaks+1)*q - p) / (nobs*nbreaks*q)
    fstat = const * Rd.T.dot(np.linalg.inv(R.dot(V).dot(R.T))).dot(Rd)

    return fstat

def sequential_break_test(endog, exog, nbreaks_null=0, trim=0.15, vcov=None):
    """
    Test that one more break exists in the sample, given that there are at
    least `nbreaks_null` breaks.

    TODO obviously in sequential estimation of breakpoints, this will right now
        recalculate the SSRs for the segments of the model many times. Easy
        optimization is possible
    TODO add support for dates, and return breakdates as well
    TODO add support for p-value calculation (Hansen 1997)
    TODO add support for different trimming values when calculating the null
         model and when estimating the additional break (see Footnote 4,
         Bai and Perron 2003)

    Parameters
    ----------
    endog : array-like
        The endogenous variable.
    exog : array-like
        The exogenous matrix.
    nbreaks_null : integer
        The number of breakpoints in the null hypothesis
    trim : float or int, optional
        If a float, the minimum percentage of observations in each regime,
        if an integer, the minimum number of observations in each regime.
    vcov : callback, optional
        Optionally provide a callback to modify the variance / covariance
        matrix used in calculating the test statistic.
    
    Returns
    -------
    fstat : float
        The test statistic.
    crits : iterable
        The critical values.
    """
    nobs = len(endog)
    if trim < 1:
        trim = int(np.floor(trim * nobs))

    exog = np.asarray(exog)
    # TODO Is there a better way to test for and fix this? (the problem is
    #      that if the exog argument is a list, so that exog is 1dim,
    #      np.concatenate fails to create a matrix, instead just makes a
    #      long vector)
    if exog.ndim == 1:
        exog = exog[:, None]
    
    # TODO add test to make sure trim is consistent with the number of breaks
    #      in both the null and alternative hypotheses
    
    # Estimate the breakpoints under the null
    breakpoints, ssr_null = find_breakpoints(endog, exog, nbreaks_null, trim)

    # Get the indices for the start and end of each segment
    segments = zip((0,) + breakpoints, breakpoints + (nobs,))

    # For each segment (there are nbreaks_null+1), estimate an additional
    # breakpoint
    optimal_segment = None
    new_breakpoints = None
    min_ssr = np.Inf
    for segment in range(nbreaks_null+1):
        start, end = segments[segment]
        # Add one to the end, since breakpoint is actually the last observation
        # in the previous regime
        end += 1
        segment_endog = endog[start:end]
        segment_exog = exog[start:end]

        # TODO this involves re-calculating SSR for lots of segments. Should
        #      use a cache of the upper-triangular set of SSRs from the
        #      find_breakpoints estimation above
        try:
            breakpoint, ssr = find_breakpoints(segment_endog, segment_exog, 1,
                                               trim)

            if ssr < min_ssr:
                min_ssr = ssr
                optimal_segment = segment
                new_breakpoints = breakpoint
        except InvalidRegimeError:
            pass

    # Find the parameters
    start, end = segments[optimal_segment]
    end += 1
    segment_exog, _, _ = build_exog(exog[start:end], new_breakpoints)
    res = OLS(endog[start:end], segment_exog).fit()

    # Calculate the test statistic
    nbreaks = 1
    q = exog.shape[1] # number of parameters subject to break, hard-coded to entire exog for now
    p = 0 # number of parameters not subject to break, hard-coded to zero for now
    R = np.zeros((nbreaks, nbreaks+1))
    R[np.diag_indices(nbreaks)] = [-1]*nbreaks
    R[tuple(np.diag_indices(nbreaks) + np.array([[0]*nbreaks, [1]*nbreaks]))] = [1]*nbreaks
    Rd = R.dot(res.params[:, None])

    V = vcov(res) if vcov else res.cov_params()

    nobs_segment = end - start
    const = (nobs_segment - (nbreaks+1)*q - p) / (nobs_segment*nbreaks*q)
    fstat = const * Rd.T.dot(np.linalg.inv(R.dot(V).dot(R.T))).dot(Rd)

    return fstat


if __name__ == "__main__":
    from numpy.testing import assert_equal, assert_almost_equal
    # Tested against Bai and Perron (2003), section 6.1 - The US Ex-post Real Interest Rate
    real = [
        1.99132, 0.00403, 2.27, 0.84833, 1.89112, -0.28, 3.68431, 1.62478, 1.21599,
        1.28373, 1.70141, 3.16687, 2.32779, 2.26202, 1.91218, 3.53196, -0.31777,
        3.44694, 1.52422, 0.74268, 1.31541, 0.36646, 3.59562, 3.6574, 0.97494,
        -0.5328, 1.12681, 0.31123, 0.57834, 1.08163, 0.24977, 0.23792, -0.32653,
        1.14733, 1.19323, 2.58962, 0.01195, 2.63842, 0.42092, 2.58823, -2.19809,
        2.89548, 1.8213, 0.86332, 0.67496, 0.34435, 1.22762, -2.83991, -1.8163,
        -2.22965, -1.58457, -6.31184, -2.46258, -5.61479, -3.53887, 1.0178,
        -1.58875, -1.85396, -0.2567, 2.42226, -1.29502, -0.48977, 1.21167,
        -4.85498, -3.599, 0.17094, 1.51603, -1.85304, -5.60478, -1.25767, 0.96658,
        -3.09451, -5.26773, -4.03154, -1.76618, -5.73978, 3.83047, 0.52007,
        -0.18033, 3.82808, 3.01171, 2.75289, 11.74184, 9.91701, 3.03444, 10.15143,
        9.29177, 6.87498, 2.43675, 4.37202, 6.77774, 4.16692, 5.65037, 5.17734,
        9.41206, 3.77006, 4.24568, 4.53154, 3.39706, 8.93951, 4.20825, 3.43461,
        4.30529
    ]
    data = pd.DataFrame(
        real,
        index=pd.date_range('1961-01-01', '1986-07-01', freq='QS'),
        columns=['real']
    )
    nobs = len(data)
    const = np.array([1 for i in range(nobs)])
    
    # Estimate 3 breakpoints
    breakpoints, ssr = find_breakpoints(data.real, const, 3)
    assert_equal(breakpoints, (23, 46, 78))
    
    # Test for 3 breakpoints
    # (Bai and Perron use Andrews (1991) HAC var/cov matrix, which SM
    # can't currently estimate, so insert it here to make tests match
    V = np.array([[0.036057291777551,        0,        0,        0],
                  [     0,   0.023560598517385,        0,        0],
                  [     0,        0,   0.261105369875645,        0],
                  [     0,        0,        0,   0.363491918147632]])
    fstat = break_test(data.real, const, 3, vcov = lambda _: V)
    assert_almost_equal(fstat, 33.3228, 4)
    
    # Sequential test, for 1 vs 0 breakpoints
    V = np.array([[0.024165305694794,                    0],
                  [                0,    0.261105369875645]])
    fstat = sequential_break_test(data.real, const, 1, vcov = lambda _: V)
    assert_almost_equal(fstat, 33.9275, 4)
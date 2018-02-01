# Author Denis A. Engemann <d.engemann@gmail.com>
#
# License: BSD (3-clause)

import numpy as np
import pandas as pd

def ci_within(df, indexvar, withinvars, measvar, confint=0.95,
                      copy=True):
    """ Compute CI / SEM correction factor

    Morey 2008, Cousinaueu 2005, Loftus & Masson, 1994
    Also see R-cookbook http://goo.gl/QdwJl

    Note. This functions helps to generate appropriate confidence
    intervals for repeated measure designs.
    Standard confidence intervals are are computed on normalized data
    and a correction factor is applied that prevents insanely small values.

    df : instance of pandas.DataFrame
        The data frame objetct.
    indexvar : str
        The column name of of the identifier variable that representing
        subjects or repeated measures
    withinvars : str | list of str
        The column names of the categorial data identifying random effects
    measvar : str
        The column name of the response measure
    confint : float
        The confidence interval
    copy : bool
        Whether to copy the data frame or not.
    """
    if copy:
        df = df.copy()

    # Apply Cousinaueu's method:
    # compute grand mean
    mean_ = df[measvar].mean()

    # compute subject means
    subj_means = df.groupby(indexvar)[measvar].mean().values
    for subj, smean_ in zip(df[indexvar].unique(), subj_means):
        # center
        df[measvar][df[indexvar] == subj] -= smean_
        # add grand average
        df[measvar][df[indexvar] == subj] += mean_

    def sem(x):
        return x.std() / np.sqrt(len(x))

    def ci(x):
        se = sem(x)
        return se * scipy.stats.t.interval(confint, len(x) - 1)[1]

    aggfuncs = [np.mean, np.std, sem, ci]
    out = df.groupby(withinvars)[measvar].agg(aggfuncs)

    # compute & apply correction factor
    n_within = np.prod([len(df[k].unique()) for k in withinvars],
                       dtype= df[measvar].dtype)
    cf = np.sqrt(n_within / (n_within - 1))
    for k in ['sem', 'std', 'ci']:
        out[k] *= cf

    return out

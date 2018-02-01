# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np

_dummy_data_anova2 = pd.DataFrame(np.random.rand(30,4) + [[0., 1., 0.2, 0.8]],
                           columns=pd.MultiIndex.from_tuples([
                           ('a0','b0'),('a0','b1'),('a1','b0'),('a1','b1')],
                           names=['factor_a', 'factor_b']),
                           index=range(30))

from collections import namedtuple

ANOVA2 = namedtuple("ANOVA2",["univariate_tests", "sphericity_tests", 
                                  "pval_adjustments", "full_dict"])

def anova2(x, print_summary=False):
    """
    Uses {car} Anova in R, via rpy2, to compute two-way repeeated measures anova.
    ``x`` should be a pandas dataframe of the form::
        
        
        factor_a    a0            a1       
        factor_b    b0     b1     b0     b1
        0          0.3   0.35   0.44   0.49
        1          0.5   0.47   0.92   1.20
        2         43.7  42.60  18.10  17.40
        3          3.8   4.50   9.20  10.40
        4         18.2  17.60  21.30  21.90
        5         22.4  23.10  19.30  19.80
        ...
        
    In the above, there are two "factors", which we have called "factor_a" and
    "factor_b". Here, each of the two factors has two "levels": ["a0", "a1"]
    and ["b0", "b1"]. Note that it is the fact that we have two *factors* that
    makes this a two-way anova, you *can* have more than two levels in each
    factor.
    
    This module includes ``_dummy_data_anova2``, which you can use here.
    
    Note on sphericity:
        The sphericity requirement is, roughly speaking, that all *pairs* of
        levels within a given factor must have roughly the same covariance.
        i.e. the "information" about a repeated measure is distributed evenly 
        across all the levels rather than some of the levels being more correlated
        to each other than others.  Note that if there are only two levels then
        there is only one covariance, so sphericity must be valid 
        (see http://stats.stackexchange.com/a/59206).
        When sphericity is violated, the way to compensate is to reduce the 
        number of degrees of freedom.  There are three similar ways of doing this.
        The most convervative is the "lower bound", then "Greenhouse-G", then
        "Huynh-F". You are recommended to just look at the Greenhouse-G values.
        (see https://youtu.be/wkMwW_2_TzY?t=40m34s).
        
    Returns a namedtuple with three pandas dataframes: 
        univariate_tests, sphericity_tests, and pval_adjustments
    There is also an attribute "full_dict", the values of which are rpy2 objects
    and provide the full output of the anova.
    
    You need to install R, rpy2, and the car package in R.
    Good luck.
    
    DM, Jun 2015.
    """
    from rpy2.robjects import pandas2ri
    from rpy2.robjects.packages import importr
    import rpy2.robjects as R
    pandas2ri.activate()
    car = importr("car")
    
    level_values = x.columns.to_series().reset_index().drop(0,axis=1)
    level_names = x.columns.names
    x = x.copy()
    x.columns = [xx[0] + xx[1] for xx in x.columns]
    R.globalenv["data_x"] = R.r["as.matrix"](pandas2ri.py2ri(x))    
    anova_r = car.Anova(R.r.lm("data_x ~ 1"),
                    idata=pandas2ri.py2ri(level_values),
                    idesign=R.reval("~" + "*".join(level_names)))
    R.r.rm("data_x")
    ret = R.r.summary(anova_r)
    if print_summary:
        print ret

    full_dict = {k.replace(".","_"): v for k,v in ret.items()}
    
    def to_df(v):
        try:
            return pd.DataFrame(pandas2ri.ri2py(v), 
                                columns=v.colnames, 
                                index=v.rownames)
        except TypeError:
            return None
    return ANOVA2(univariate_tests=to_df(full_dict["univariate_tests"]), 
                  sphericity_tests=to_df(full_dict["sphericity_tests"]),
                  pval_adjustments=to_df(full_dict["pval_adjustments"]),
                  full_dict=full_dict)
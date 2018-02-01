# -*- coding: utf-8 -*-

import datetime

from numpy import asarray, ceil
import pandas
import rpy2.robjects as robjects

def stl(data, ns, np=None, nt=None, nl=None, isdeg=0, itdeg=1, ildeg=1,
        nsjump=None, ntjump=None, nljump=None, ni=2, no=0, fulloutput=False):
    """
    Seasonal-Trend decomposition procedure based on LOESS

    data : pandas.Series

    ns : int
        Length of the seasonal smoother.
        The value of  ns should be an odd integer greater than or equal to 3.
        A value ns>6 is recommended. As ns  increases  the  values  of  the
        seasonal component at a given point in the seasonal cycle (e.g., January
        values of a monthly series with  a  yearly cycle) become smoother.

    np : int
        Period of the seasonal component.
        For example, if  the  time series is monthly with a yearly cycle, then
        np=12.
        If no value is given, then the period will be determined from the
        ``data`` timeseries.

    nt : int
        Length of the trend smoother.
        The  value  of  nt should be an odd integer greater than or equal to 3.
        A value of nt between 1.5*np and 2*np is  recommended. As nt increases,
        the values of the trend component become  smoother.
        If nt is None, it is estimated as the smallest odd integer greater
        or equal to ``(1.5*np)/[1-(1.5/ns)]``

    nl : int
        Length of the low-pass filter.
        The value of nl should  be an odd integer greater than or equal to 3.
        The smallest odd integer greater than or equal to np is used by default.

    isdeg : int
        Degree of locally-fitted polynomial in seasonal smoothing.
        The value is 0 or 1.

    itdeg : int
        Degree of locally-fitted polynomial in trend smoothing.
        The value is 0 or 1.

    ildeg : int
        Degree of locally-fitted polynomial in low-pass smoothing.
        The value is 0 or 1.

    nsjump : int
        Skipping value for seasonal smoothing.
        The seasonal smoother skips ahead nsjump points and then linearly
        interpolates in between.  The value  of nsjump should be a positive
        integer; if nsjump=1, a seasonal smooth is calculated at all n points.
        To make the procedure run faster, a reasonable choice for nsjump is
        10%-20% of ns. By default, nsjump= 0.1*ns.

    ntjump : int
        Skipping value for trend smoothing. If None, ntjump= 0.1*nt

    nljump : int
        Skipping value for low-pass smoothing. If None, nljump= 0.1*nl

    ni :int
        Number of loops for updating the seasonal and trend  components.
        The value of ni should be a positive integer.
        See the next argument for advice on the  choice of ni.
        If ni is None, ni is set to 2 for robust fitting, to 5 otherwise.

    no : int
        Number of iterations of robust fitting. The value of no should
        be a nonnegative integer. If the data are well behaved without
        outliers, then robustness iterations are not needed. In this case
        set no=0, and set ni=2 to 5 depending on how much security
        you want that  the seasonal-trend looping converges.
        If outliers are present then no=3 is a very secure value unless
        the outliers are radical, in which case no=5 or even 10 might
        be better.  If no>0 then set ni to 1 or 2.
        If None, then no is set to 15 for robust fitting, to 0 otherwise.

    fulloutput : bool
        If True, a dictionary holding the full output of the original R routine
        will be returned.

    returns

    data : pandas.DataFrame
        The seasonal, trend, and remainder components

    """
    # make sure that data doesn't start or end with nan
    _data = data.copy()
    _data = _data.dropna()
    # TODO: account for non-monthly series
    _idx = pandas.DateRange(start=_data.index[0], end=_data.index[-1],
                            offset=pandas.datetools.MonthBegin())
    data = pandas.Series(index=_idx)
    data[_data.index] = _data

    # zoo package contains na.approx
    zoo_ = robjects.packages.importr("zoo")

    ts_ = robjects.r['ts']
    stl_ = robjects.r['stl']
    naaction_ = robjects.r['na.approx']

    # find out the period of the time series
    if np is None:
        np = 12
        # TODO: find out the offset of the Series, and set np accordingly
        #if isinstance(data.index.offset, pandas.core.datetools.MonthEnd):
        #    np = 12
        #else:
        #    raise NotImplementedError()
    # fill default values
    if nt is None:
        nt = ceil((1.5 * np) / (1 - (1.5 / ns)))
    nt = nt + 1 if nt % 2 == 0 else nt

    if nl is None:
        nl = np if np % 2 is 1 else np + 1
    if nsjump is None:
        nsjump = ceil(ns / 10.)
    if ntjump is None:
        ntjump = ceil(nt / 10.)
    if nljump is None:
        nljump = ceil(nl / 10.)

    # convert data to R object
    if np is 12:
        start = robjects.IntVector([data.index[0].year, data.index[0].month])
    ts = ts_(robjects.FloatVector(asarray(data)), start=start, frequency=np)

    if nt is None:
        nt = robjects.rinterface.R_NilValue

    result = stl_(ts, ns, isdeg, nt, itdeg, nl, ildeg, nsjump, ntjump, nljump,
                  False, ni, no, naaction_)

    res_ts = asarray(result[0])
    try:
        res_ts = pandas.DataFrame({"seasonal" : pandas.Series(res_ts[:,0],
                                                           index=data.index),
                                   "trend" : pandas.Series(res_ts[:,1],
                                                           index=data.index),
                                   "remainder" : pandas.Series(res_ts[:,2],
                                                           index=data.index)})
    except:
        return res_ts, data
        raise
#        res_ts = pandas.DataFrame({"seasonal" : pandas.Series(index=data.index),
#                                   "trend" : pandas.Series(index=data.index),
#                                   "remainder" : pandas.Series(index=data.index)})

    if fulloutput:
        return {"time.series" : res_ts,
                "weights" : result[1],
                "call" : result[2],
                "win" : result[3],
                "deg" : result[4],
                "jump" : result[5],
                "ni" : result[6],
                "no" : result[7]}
    else:
        return res_ts


if __name__ == "__main__":
    data = np.arange(85.) / 12.
    data = np.sin(data * (2*np.pi))
    data += np.arange(85.) / 12. * .5
    data += .1 * np.random.randn(85)
    idx = pandas.DateRange(start=datetime.datetime(1999,1,1), end=datetime.datetime(2006,2,1), offset=pandas.datetools.MonthEnd())
    data = pandas.Series(data, index=idx)

    res = stl(data, 7, nt=11)
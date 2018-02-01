# https://github.com/dalejung/trtools/blob/master/trtools/rpy/conversion.py
import sys, copy, os, itertools

import rpy2.robjects as robjects
import rpy2.rinterface as rinterface
from rpy2.robjects.vectors import SexpVector, ListVector
from rpy2.robjects.robject import RObjectMixin, RObject
import rpy2.robjects as robj
import numpy as np
import pandas.rpy.common as rcom
import pandas as pd

NA_TYPES = rcom.NA_TYPES
VECTOR_TYPES = rcom.VECTOR_TYPES

baseenv_ri = rinterface.baseenv
globalenv_ri = rinterface.globalenv

def my_ri2py(o):
    res = None
    try:
        rcls = o.do_slot("class")
    except LookupError, le:
        rcls = [None]

    if isinstance(o, SexpVector):
        if 'xts' in rcls:
            res = convert_xts_to_df(o)

    if res is None:
        res = robjects.default_ri2py(o)

    return res

def convert_xts_to_df(o):
    """
        Will convert xts objects to DataFrame
    """
    dates = o.do_slot('index')
    dates = np.array(dates, dtype=np.dtype("M8[s]"))
    res = robjects.default_ri2py(o)
    df = rcom.convert_robj(res)
    df.index = dates
    return df

robjects.conversion.ri2py = my_ri2py

def pd_py2ri(o):
    """ 
    """

    res = None
    if isinstance(o, pd.DataFrame) and isinstance(o.index, pd.DatetimeIndex):
        res = convert_df_to_xts(o)

    if res is None:
        res = robjects.default_py2ri(o)

    return res

def convert_df_to_xts(df, strings_as_factors=False):
    r_dataframe = XTS(df)
    return r_dataframe

class XTS(RObject):
    """ R 'as.xts'.
    """
    
    def __init__(self, df):
        """ Create a xts.
        """
        self.rdf = None
        if isinstance(df, pd.DataFrame):
            rdf = rcom.convert_to_r_dataframe(df)
            self.rdf = rdf
            xts = baseenv_ri.get("as.xts").rcall(tuple([('x', rdf)]), globalenv_ri)
            super(XTS, self).__init__(xts)
        else:
            raise ValueError("Currently only supporting DataFrames")
    
    def __repr__(self):
        return self.rdf.__repr__()

robjects.conversion.py2ri = pd_py2ri
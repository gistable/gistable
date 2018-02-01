import scipy
import numpy as np
import pandas as pd
import statsmodels.api as sm
from statsmodels.tools.tools import chain_dot
from statsmodels.tools.decorators import cache_readonly
from statsmodels.regression.linear_model import (RegressionModel,
                                                 RegressionResults)

class Group():
    def __init__(self, index_pandas=None, index_list=None):
        '''
        index_pandas pandas (multi-)index
        index_list list of arrays, pandas series or lists, all of which are
            of length nobs 
        '''
        if index_list != None:
            try:
                tup = zip(*args)
                self.index = pd.MultiIndex.from_tuples(tup)
            except:
                raise Exception("index_list must be a list of lists, pandas series, \
                        or numpy arrays, each of identitcal length nobs.") 
        else:
            self.index = index_pandas
        self.nobs = len(self.index)
        self.slices = None

    def get_slices(self):
        '''Only works on first index level'''
        groups = self.index.get_level_values(0).unique()
        self.slices = [self.index.get_loc(x) for x in groups]

    def count_categories(self, level=0):
        self.counts = np.bincount(self.index.labels[level])

    def transform_dataframe(self, dataframe, function, level=0):
        '''Apply function to each column, by group
        Assumes that the dataframe already has a proper index'''
        if dataframe.shape[0] != self.nobs:
            raise Exception('dataframe does not have the same shape as index')
        out = dataframe.groupby(level=level).apply(function)
        if 1 in out.shape:
            return np.ravel(out)
        else:
            return np.array(out)
     
    def transform_array(self, array, function, level=0):
        '''Apply function to each column, by group'''
        if array.shape[0] != self.nobs:
            raise Exception('array does not have the same shape as index')
        dataframe = pd.DataFrame(array, index=self.index)
        return self.transform_dataframe(dataframe, function, level=level)

    def transform_slices(self, array, function,  **kwargs):
        '''Assumes array is a 1D or 2D numpy array'''
        if array.shape[0] != self.nobs:
            raise Exception('array does not have the same shape as index')
        if self.slices == None:
            self.get_slices()
        processed = []
        for s in self.slices:
            if array.ndim == 2:
                subset = array[s,:]
            elif array.ndim == 1:
                subset = array[s]
            processed.append(function(subset, s, **kwargs))
        return np.concatenate(processed)

    def dummy_sparse(self, level=0):
        '''create a sparse indicator from a group array with integer labels

        Parameters
        ----------
        groups: ndarray, int, 1d (nobs,) an array of group indicators for each
            observation. Group levels are assumed to be defined as consecutive
            integers, i.e. range(n_groups) where n_groups is the number of
            group levels. A group level with no observations for it will still
            produce a column of zeros.

        Returns
        -------
        indi : ndarray, int8, 2d (nobs, n_groups)
            an indicator array with one row per observation, that has 1 in the
            column of the group level for that observation

        Examples
        --------

        >>> g = np.array([0, 0, 2, 1, 1, 2, 0])
        >>> indi = dummy_sparse(g)
        >>> indi
        <7x3 sparse matrix of type '<type 'numpy.int8'>'
            with 7 stored elements in Compressed Sparse Row format>
        >>> indi.todense()
        matrix([[1, 0, 0],
                [1, 0, 0],
                [0, 0, 1],
                [0, 1, 0],
                [0, 1, 0],
                [0, 0, 1],
                [1, 0, 0]], dtype=int8)


        current behavior with missing groups
        >>> g = np.array([0, 0, 2, 0, 2, 0])
        >>> indi = dummy_sparse(g)
        >>> indi.todense()
        matrix([[1, 0, 0],
                [1, 0, 0],
                [0, 0, 1],
                [1, 0, 0],
                [0, 0, 1],
                [1, 0, 0]], dtype=int8)

        '''
        
        groups = self.index.labels[level]
        indptr = np.arange(len(groups)+1)
        data = np.ones(len(groups), dtype=np.int8)
        self.dummies = scipy.sparse.csr_matrix((data, groups, indptr))

class PanelLM(RegressionModel):
    def __init__(self, endog, exog, method='pooling', effects='oneway',
                 unit=None, time=None, hasconst=None, **kwargs):
        if (time != None) and (unit != None):
            self.groupings = Group(index_list=[unit, time])
        else:
            self.groupings = Group(index_pandas=endog.index)
        self.endog = endog
        self.exog = exog
        self.method = method
        self.effects = effects
        if method == 'swar':
            self.var_u, self.var_e, self.theta = swar_ercomp(self.endog, self.exog)
        super(PanelLM, self).__init__(endog, exog, **kwargs)

    def initialize(self, unit=None, time=None):
        self.wexog = self.whiten(self.exog)
        self.wendog = self.whiten(self.endog)
        self.nobs = float(self.wexog.shape[0])
        self.rank = np.rank(self.exog)
        self.df_model = float(self.rank - self.k_constant)
        if self.method == 'within':
            self.df_resid = self.nobs - self.rank - self.groupings.index.levshape[0]
        else:
            self.df_resid = self.nobs - self.rank - 1
        self.df_model = float(self.rank - self.k_constant)

    def whiten(self, data):
        g = self.groupings
        if self.method == 'within':
            f = lambda x: x - x.mean()
            if (self.effects == 'oneway') or (self.effects == 'unit'):
                out = g.transform_array(data, f, 0)
                return out
            elif (self.effects == 'time'):
                out = g.transform_array(data, f, 1)
                return out
            elif (self.effects == 'twoways'):
                out = g.transform_array(data, f, 0)
                out = g.transform_array(data, f, 1)
                return out
            else:
                raise Exception('Method must be unit, time, oneway, or twoways')
        elif self.method == 'between':
            f = lambda x: x.mean()
            out = g.transform_array(data, f, 0)
            return out
        elif self.method == 'fd':
            f = lambda x: (x - x.shift(1))[1:],
            out = g.transform_array(data, f, 0)
            return out
        elif self.method == 'pooling':
            return data
        elif self.method == 'swar':
            out = g.transform_slices(array=data, function=swar_transform,
                                     theta=self.theta) 
            return out

    def fit(self, method="pinv", **kwargs):
        wexog = self.wexog
        self.pinv_wexog = pinv_wexog = np.linalg.pinv(wexog)
        self.normalized_cov_params = np.dot(pinv_wexog, pinv_wexog.T)
        beta = np.dot(self.pinv_wexog, self.wendog)
        lfit = PanelLMResults(self, beta,
                   normalized_cov_params=self.normalized_cov_params)
        return lfit

def swar_ercomp(y, X):
    '''Swamy-Arora error decomposition'''
    b = PanelLM(y, X, 'between').fit()
    w = PanelLM(y, X, 'within').fit()
    w.model.groupings.count_categories(level=0)
    Ts = w.model.groupings.counts   
    Th = scipy.stats.mstats.hmean(Ts)
    var_e = w.ssr / (X.shape[0] - w.model.groupings.index.levshape[0] - X.shape[1] + 1)
    var_u = b.ssr / (b.model.groupings.index.levshape[0] - X.shape[1]) - var_e / Th
    var_u = max(var_u, 0)
    Ts = np.concatenate([np.repeat(x,x) for x in Ts])
    theta = 1 - np.sqrt(var_e / (Ts * var_u + var_e))
    return var_e, var_u, np.array(theta)

def swar_transform(subset, position, theta):
    '''Apply to a sub-group of observations'''
    n = subset.shape[0]
    B = np.ones((n,n)) / n
    out = subset - chain_dot(np.diag(theta[position]), B, subset)
    return out

class PanelLMResults(RegressionResults):
    def __init__(self, model, params, normalized_cov_params=None):
        super(PanelLMResults, self).__init__(model, params)
        self.normalized_cov_params = normalized_cov_params

    @cache_readonly
    def bse(self):
        if self.model.method == 'within':
            scale = self.nobs - self.model.groupings.index.levshape[0] - self.df_model
            scale = np.sum(self.wresid**2) / scale
            bse = np.sqrt(np.diag(self.cov_params(scale=scale)))
        else:
            bse = np.sqrt(np.diag(self.cov_params()))
        return bse

    @cache_readonly
    def ssr(self):
        return np.sum(self.wresid**2)

    @cache_readonly
    def resid(self):
        if (self.model.method == 'within') and not (self.model.panel_balanced):
            Xb_bar = np.dot(self.model.exog.mean(axis=0), self.params)
            alph = np.mean(self.model.endog) - Xb_bar
            pred = alph + np.dot(self.model.exog, self.params)
            resid = self.model.endog - pred
        else:
            resid = self.model.wendog - self.model.predict(self.params,
                                                           self.model.wexog)
        return resid

    @cache_readonly
    def fvalue(self):
        f = self.mse_model/self.mse_resid
        if self.model.method == 'between':
            # TODO: Why is this correct (from Stata)?
            f = f / 2.
        return f

    @cache_readonly
    def scale(self):
        wresid = self.wresid
        return np.dot(wresid.T, wresid) / self.df_resid

def pooltest(endog, exog):
    '''Chow poolability test: F-test of joint significance for the unit dummies
    in a LSDV model
    
    Returns
    -------

    F statistic for the null hypothesis that unit effects are zero.
    p value
    '''
    # TODO: Does this assume balanced panels?
    unrestricted = PanelLM(endog, exog, 'within').fit()
    restricted = PanelLM(endog, exog, 'pooling').fit()
    N = unrestricted.model.panel_N
    T = unrestricted.model.panel_T
    K = unrestricted.model.exog.shape[1]
    urss = unrestricted.ssr
    rrss = restricted.ssr 
    F = ((rrss - urss) / (N-1)) / (urss / (N*T - N - K))
    p = 1 - scipy.stats.distributions.f.cdf(F, N-1, N*(T-1)-K) 
    return F, p


from statsmodels.iolib.summary import summary_col
from patsy import dmatrices
def test(y, X):
    mod1 = PanelLM(y, X, method='pooling').fit()
    mod2 = PanelLM(y, X, method='between').fit()
    mod3 = PanelLM(y, X.ix[:,1:], method='within').fit()
    mod4 = PanelLM(y, X.ix[:,1:], method='within', effects='time').fit()
    mod5 = PanelLM(y, X.ix[:,1:], method='within', effects='twoways').fit()
    mod6 = PanelLM(y, X, 'swar').fit()
    mn = ['OLS', 'Between', 'Within N', 'Within T', 'Within 2w', 'RE-SWAR']
    out = summary_col([mod1, mod2, mod3, mod4, mod5, mod6], model_names=mn, stars=False)
    return out
url = 'http://vincentarelbundock.github.com/Rdatasets/csv/plm/EmplUK.csv'
url = 'EmplUK.csv'
gasoline = pd.read_csv(url).set_index(['firm', 'year'])
f = 'emp~wage+capital'
y, X = dmatrices(f, gasoline, return_type='dataframe')

'''
# Statsmodels

================================================================
            OLS    Between  Within N Within T Within 2w RE-SWAR 
----------------------------------------------------------------
Intercept  10.3598  10.5060                               9.0390
          (1.2023) (3.3055)                             (1.1015)
capital     2.1049   2.2673   0.8015   2.0999    0.7854   1.1564
          (0.0441) (0.1136) (0.0641) (0.0470)  (0.0622) (0.0592)
wage       -0.3238  -0.3371  -0.1436  -0.3334   -0.0955  -0.1589
          (0.0487) (0.1338) (0.0328) (0.0527)  (0.0356) (0.0338)
----------------------------------------------------------------
N             1031      140     1031     1031      1031     1031
R2           0.693    0.748    0.164    0.695     0.155    0.283
================================================================
Standard errors in parentheses.

# Stata replication

wget http://vincentarelbundock.github.com/Rdatasets/csv/plm/EmplUK.csv

insheet using EmplUK.csv, clear
xtset firm year
xtreg emp wage capital, fe

# R replication

library(plm)
dat = read.csv('EmplUK.csv')
dat = pdata.frame(dat, c('firm', 'year'))
mod = plm(emp ~ wage + capital, data=dat, model='within')
'''
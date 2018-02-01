# coding=UTF8
#########################################################################
# This class is to help sklearn to handle statistical process           #
# Author: Joon Lim from Master of Science in Analytics at Northwestern  #
# Date: 04.23.2013                                                      #
#########################################################################

''' this Module is built on top of numpy and sklearn. '''

    
#### covariance Matrix function
def CovMat(X):
        '''Calculate the covariance matrix with ndarray & DataFrame'''
        cov = 1/float(len(X)-1) * (X-X.mean(0)).T.dot(X-X.mean(0))
        return cov

#### correlation Matrix function
def CorrMat(X):
        '''Calculate the correlation matrix with ndarray & DataFrame'''
        corr = 1/float(len(X)-1) * ((X-X.mean(0))/X.std(0, ddof=True)).T.dot(((X-X.mean(0))/X.std(0, ddof=True)))
        return corr

#Adj R square — first find the metrics.r2_score — then,
def adj_r2_score(self,model,y,yhat):
        """Adjusted R square — put fitted linear model, y value, estimated y value in order
        
            Example:
            In [142]: metrics.r2_score(diabetes_y_train,yhat)
            Out[142]: 0.51222621477934993
        
            In [144]: adj_r2_score(lm,diabetes_y_train,yhat)
            Out[144]: 0.50035823946984515"""
        from sklearn import metrics
        adj = 1 - float(len(y)-1)/(len(y)-len(model.coef_)-1)*(1 - metrics.r2_score(y,yhat))
        return adj

### sample list of one generator
def one(p):
        ''' numpy array of ones generator
            
            In [1]: one(10)
            Out[2]: array([1, 1, 1, 1, 1, 1, 1, 1, 1, 1])
            '''
        return np.random.randint(1,2,p)

### sample list of zero generator
def zero(p):
        ''' numpy array of ones generator
            
            In [1]: zero(10)
            Out[2]: array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
            '''
        return np.random.randint(0,1,p)


### Summary Statistic that we can get in 'R'
def summary(df):
        '''summary statistic with min, mean, sd, median, max, and sample size
            
            In [218]: summary(df3)
            Out[218]:
                    Column1   Column2   Column3
            Min    -1.141389 -0.358481 -0.814520
            Mean   -0.612211  0.551169  0.231508
            std    -0.580043  0.609654  0.183388
            Median -0.147370  1.343851  1.373775
            Max     0.420570  0.723449  1.006741
            count   4.000000  4.000000  4.000000
            '''
        import pandas as pd
        def f(x):
            return pd.Series([x.min(),x.mean(),x.median(),x.max(),x.std(),len(x.notnull())], index=['Min','Mean','std','Median','Max','count'])
        return df.apply(f)

### sklearn viewer for predict_proba & predict
def viewer(mat,yhat):
        ''' sklearn viewer for predict_proba & predict.
            
            In [418]: viewer(lgm.predict_proba(X),lgm.predict(X))
            Out[418]:
            array([[ 0.52038098,  0.47961902,  0.        ],
                   [ 0.27792502,  0.72207498,  1.        ],
                   [ 0.12013796,  0.87986204,  1.        ]])
            '''
        a,b = np.shape(mat); p=a*(b+1)
        background = np.arange(p,dtype=float).reshape([a,(b+1)])
        background[:,:-1] = mat
        background[:,-1] = yhat
        return background




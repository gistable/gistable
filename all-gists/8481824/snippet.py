import numpy as np
import rpy2.robjects as ro
import rpy2.robjects.numpy2ri as n2r
n2r.activate()

r = ro.r
r.library('glmnet')

# input files (for this example) need to have header and NO index column
X = np.loadtxt('./x.csv', dtype=float, delimiter=',', skiprows=1)
y = np.loadtxt('./y.csv', dtype=int, delimiter=',', skiprows=1)
y = ro.FactorVector(list(y.transpose())) # use factors

trained_model = r['cv.glmnet'](X, y, nfolds=3, family="binomial")
lambda_ = np.asanyarray(trained_model.rx2('lambda'))
cvm_ = np.asanyarray(trained_model.rx2('cvm'))
cvsd_ = np.asanyarray(trained_model.rx2('cvsd'))

lambda_min = np.asanyarray(trained_model.rx2('lambda.min'))[0]
min_cvm = cvm_[np.argwhere(lambda_ == lambda_min)[0][0]]

idx = np.argwhere(cvm_ < min_cvm + 0.1*cvsd_)
idx[0]

fit = trained_model.rx2('glmnet.fit')
beta = n2r.ri2numpy(r['as.matrix'](fit.rx2('beta')))

relvars = np.argwhere(beta[:,idx[0]].transpose()[0] > 1e-5)
print relvars.transpose()[0]

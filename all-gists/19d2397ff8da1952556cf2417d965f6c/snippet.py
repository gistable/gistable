
## Makes a monitor where the mean of last x oob improvements
## are used to determine early stopping. This can be ammended
## to any stopping criteria one sees as fit - consecutive x 
## negatives, more negatives than positives in last x, etc.
def make_monitor(running_mean_len):
    def monitor(i,self,args):
        if np.mean(self.oob_improvement_[max(0,i-running_mean_len+1):i+1])<0:
            return True
        else:
            return False
    return monitor

  
## Example use
from sklearn.ensemble import GradientBoostingRegressor

gbr = GradientBoostingRegressor(n_estimators=10000000,verbose=5) ## n_estimators can be arbitrarily high

monitor = make_monitor(10) ## this is a number that should be fit to a validation set
gbr.fit(X_train,y_train,monitor=monitor)

print gbr.estimators_.shape[0]


# http://www.dataiku.com/blog/2015/08/24/xgboost_and_dss.html

import dataiku
import pandas as pd, numpy as np
from dataiku import pandasutils as pdu
from sklearn.metrics import roc_auc_score
import xgboost as xgb
from hyperopt import hp, fmin, tpe, STATUS_OK, Trials 

train = dataiku.Dataset("train").get_dataframe()
valid = dataiku.Dataset("valid").get_dataframe()

y_train = train.target
y_valid = valid.target

del train["target"]
del valid["target"]

def objective(space):

    clf = xgb.XGBClassifier(n_estimators = 10000, 
                            max_depth = space['max_depth'],
                            min_child_weight = space['min_child_weight'],
                            subsample = space['subsample'])

    eval_set  = [( train, y_train), ( valid, y_valid)]

    clf.fit(train[col_train], y_train,
            eval_set=eval_set, eval_metric="auc", 
            early_stopping_rounds=30)

    pred = clf.predict_proba(valid)[:,1]
    auc = roc_auc_score(y_valid, pred)
    print "SCORE:", auc

    return{'loss':1-auc, 'status': STATUS_OK }


space ={
        'max_depth': hp.quniform("x_max_depth", 5, 30, 1),
        'min_child_weight': hp.quniform ('x_min_child', 1, 10, 1),
        'subsample': hp.uniform ('x_subsample', 0.8, 1)
    }


trials = Trials()
best = fmin(fn=objective,
            space=space,
            algo=tpe.suggest,
            max_evals=100,
            trials=trials)

print best
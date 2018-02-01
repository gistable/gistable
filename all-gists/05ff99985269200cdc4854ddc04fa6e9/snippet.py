import os
import numpy as np
import lightgbm as lgb

# directory with your models
dir_with_models = './tmp'

# 100 samples of random data (with 70 columns), just for testing
X = np.random.rand(100, 70)

pred = None 
for f in os.listdir(dir_with_models):
    print('Using {0}'.format(f))
    # read model
    model = lgb.Booster(model_file = os.path.join(dir_with_models,f))  
    # compute predictions
    pred = model.predict(X) if pred is None else pred + model.predict(X)
    
# get average of predictions from all models
pred = pred/float(len(os.listdir(dir_with_models)))
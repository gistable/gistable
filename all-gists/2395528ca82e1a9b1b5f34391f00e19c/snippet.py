# Import a bunch of models
from sklearn.linear_model import LinearRegression
from sklearn.svm import SVR
from sklearn.neighbors import KNeighborsRegressor
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.cross_decomposition import PLSRegression
from sklearn.ensemble import AdaBoostRegressor

# Import gridsearch
from sklearn.model_selection import GridSearchCV

# Add the models and grids to a list
models = [
  [LinearRegression(), {"fit_intercept": [True, False]}], 
  [SVR(), {"kernel": ["linear", "poly", "rbf", "sigmoid"]}], 
  [KNeighborsRegressor(), {"n_neighbors": [1,2], "weights": ["uniform", "distance"]}], 
  [DecisionTreeRegressor(), {"criterion": ["mse", "friedman_mse"], "splitter": ["best", "random"],
    "min_samples_split": [x for x in range(2,6)] # generates a list [2,3,4,5]
  }],
  [GradientBoostingRegressor(), {"loss": ["ls", "lad", "huber", "quantile"]}],
  [GaussianProcessRegressor(), {}],
  [PLSRegression(), {}],
  [AdaBoostRegressor(), {}]
]

# Dataset
train_X = [[5,3],[9,1],[8,6],[5,4]]
train_Y = [28,810,214,19]
pred_X = [7,3]

# Train each model individually using grid search
for model in models:
  regressor = model[0]
  param_grid = model[1]

  model = GridSearchCV(regressor, param_grid)
  
  # Finds the most accurate hyperparametors for the regressor
  # Based on the score function
  model.fit(train_X, train_Y)

  # assess accuracy
  acc = model.score(train_X, train_Y)
  
  # output model if it's perfect
  if acc == 1:
    print (model)
    print ("Accuracy: %d" % acc)
    print ("Prediction: %d" % model.predict([pred_X]))
    print()
